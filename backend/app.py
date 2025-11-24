from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from datetime import datetime, timedelta
from models import db, User, Task, TimeLog
from config import Config
import os

app = Flask(__name__, template_folder='templates', static_folder='../static')
app.config.from_object(Config)
CORS(app)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize database
with app.app_context():
    db.create_all()
    # Create default admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin/admin123")


# ============= WEB ROUTES =============

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/tasks')
@login_required
def tasks_page():
    return render_template('tasks.html')


@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')


# ============= API ENDPOINTS =============

# User APIs
@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@app.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


# Task APIs
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    status = request.args.get('status')
    user_id = request.args.get('user_id')
    
    query = Task.query
    
    if status:
        query = query.filter_by(status=status)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        category=data.get('category', 'general'),
        priority=data.get('priority', 'medium'),
        estimated_time=data.get('estimated_time', 0),
        user_id=data.get('user_id', current_user.id)
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.category = data.get('category', task.category)
    task.priority = data.get('priority', task.priority)
    task.status = data.get('status', task.status)
    task.estimated_time = data.get('estimated_time', task.estimated_time)
    
    if data.get('status') == 'completed' and not task.completed_at:
        task.completed_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(task.to_dict())


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204


# Time Log APIs
@app.route('/api/timelogs', methods=['GET'])
@login_required
def get_time_logs():
    task_id = request.args.get('task_id')
    user_id = request.args.get('user_id', current_user.id)
    
    query = TimeLog.query
    
    if task_id:
        query = query.filter_by(task_id=task_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    logs = query.order_by(TimeLog.start_time.desc()).all()
    return jsonify([log.to_dict() for log in logs])


@app.route('/api/timelogs', methods=['POST'])
@login_required
def start_time_log():
    data = request.get_json()
    
    # Check if there's an active time log
    active_log = TimeLog.query.filter_by(
        user_id=current_user.id,
        end_time=None
    ).first()
    
    if active_log:
        return jsonify({'error': 'You have an active time log. Please stop it first.'}), 400
    
    time_log = TimeLog(
        task_id=data['task_id'],
        user_id=current_user.id,
        start_time=datetime.utcnow(),
        notes=data.get('notes', '')
    )
    
    # Update task status
    task = Task.query.get(data['task_id'])
    if task.status == 'pending':
        task.status = 'in_progress'
    
    db.session.add(time_log)
    db.session.commit()
    
    return jsonify(time_log.to_dict()), 201


@app.route('/api/timelogs/<int:log_id>/stop', methods=['PUT'])
@login_required
def stop_time_log(log_id):
    time_log = TimeLog.query.get_or_404(log_id)
    
    if time_log.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    time_log.end_time = datetime.utcnow()
    time_log.duration = (time_log.end_time - time_log.start_time).total_seconds() / 3600
    
    # Update task actual time
    task = Task.query.get(time_log.task_id)
    task.actual_time = db.session.query(
        db.func.sum(TimeLog.duration)
    ).filter_by(task_id=task.id).scalar() or 0
    
    db.session.commit()
    
    return jsonify(time_log.to_dict())


@app.route('/api/timelogs/active', methods=['GET'])
@login_required
def get_active_time_log():
    active_log = TimeLog.query.filter_by(
        user_id=current_user.id,
        end_time=None
    ).first()
    
    if active_log:
        return jsonify(active_log.to_dict())
    return jsonify(None)


# Analytics APIs
@app.route('/api/analytics/summary', methods=['GET'])
@login_required
def get_analytics_summary():
    user_id = request.args.get('user_id', current_user.id)
    
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, status='completed').count()
    in_progress_tasks = Task.query.filter_by(user_id=user_id, status='in_progress').count()
    
    total_time = db.session.query(
        db.func.sum(TimeLog.duration)
    ).filter_by(user_id=user_id).scalar() or 0
    
    # Time by category
    category_time = db.session.query(
        Task.category,
        db.func.sum(Task.actual_time)
    ).filter_by(user_id=user_id).group_by(Task.category).all()
    
    return jsonify({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': total_tasks - completed_tasks - in_progress_tasks,
        'total_time': round(total_time, 2),
        'category_breakdown': [
            {'category': cat, 'time': round(time or 0, 2)} 
            for cat, time in category_time
        ]
    })


# Mobile API - Login
@app.route('/api/mobile/login', methods=['POST'])
def mobile_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
