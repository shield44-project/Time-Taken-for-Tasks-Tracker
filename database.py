# database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='task_tracker.db'):
        self.db_name = db_name
        self.conn = None
        self.create_tables()

    def connect(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()

        # Tasks Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            description TEXT,
            assigned_to TEXT,
            start_time TEXT,
            end_time TEXT,
            total_time REAL DEFAULT 0,
            standard_time REAL,
            efficiency REAL,
            status TEXT,
            parent_task_id INTEGER,
            category TEXT
        )
        ''')

        # Equipment Table for OEE
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_name TEXT NOT NULL,
            planned_time REAL,
            downtime REAL DEFAULT 0,
            actual_output INTEGER DEFAULT 0,
            good_units INTEGER DEFAULT 0,
            standard_output REAL
        )
        ''')
        conn.commit()

    # === TASK METHODS ===

    def add_task(self, task_name, description, assigned_to, standard_time=0, parent_task_id=None, category=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO tasks (task_name, description, assigned_to, standard_time, parent_task_id, status, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (task_name, description, assigned_to, standard_time, parent_task_id, 'Pending', category))
        conn.commit()

    def start_task(self, task_id):
        conn = self.connect()
        cursor = conn.cursor()
        start_time = datetime.now().isoformat()
        cursor.execute('''
        UPDATE tasks
        SET start_time = ?
        WHERE id = ?
        ''', (start_time, task_id))
        conn.commit()

    def stop_task(self, task_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT start_time, standard_time FROM tasks WHERE id = ?', (task_id,))
        result = cursor.fetchone()
        if result and result[0]:
            start_time_str = result[0]
            standard_time = result[1]
            start_time = datetime.fromisoformat(start_time_str)
            end_time_obj = datetime.now()
            total_time = (end_time_obj - start_time).total_seconds()
            efficiency = total_time / standard_time if standard_time > 0 else 0

            end_time = end_time_obj.isoformat()
            cursor.execute('''
            UPDATE tasks
            SET end_time = ?, total_time = ?, status = 'Completed', efficiency = ?
            WHERE id = ?
            ''', (end_time, total_time, efficiency, task_id))
        else:
            cursor.execute('''
            UPDATE tasks
            SET status = 'Pending'
            WHERE id = ?
            ''', (task_id,))
        conn.commit()
        return total_time

    def get_all_tasks(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        return cursor.fetchall()

    def get_task(self, task_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        return cursor.fetchone()

    def update_task(self, task_id, task_name, description, assigned_to, standard_time, parent_task_id=None, category=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE tasks
        SET task_name = ?, description = ?, assigned_to = ?, standard_time = ?, parent_task_id = ?, category = ?
        WHERE id = ?
        ''', (task_name, description, assigned_to, standard_time, parent_task_id, category, task_id))
        conn.commit()

    def delete_task(self, task_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()

    def get_children(self, parent_task_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE parent_task_id = ?', (parent_task_id,))
        return cursor.fetchall()

    # === EQUIPMENT METHODS ===

    def add_equipment(self, name, planned_time, standard_output):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO equipment (equipment_name, planned_time, standard_output)
        VALUES (?, ?, ?)
        ''', (name, planned_time, standard_output))
        conn.commit()

    def update_equipment(self, eq_id, downtime, actual_output, good_units):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE equipment
        SET downtime = ?, actual_output = ?, good_units = ?
        WHERE id = ?
        ''', (downtime, actual_output, good_units, eq_id))
        conn.commit()

    def get_equipment(self, eq_id=None):
        conn = self.connect()
        cursor = conn.cursor()
        if eq_id:
            cursor.execute('SELECT * FROM equipment WHERE id = ?', (eq_id,))
            return cursor.fetchone()
        else:
            cursor.execute('SELECT * FROM equipment')
            return cursor.fetchall()

    def compute_oee(self, eq_id):
        eq = self.get_equipment(eq_id)
        if not eq:
            return 0

        _, name, planned_time, downtime, actual_output, good_units, standard_output = eq

        if planned_time <= 0:
            return 0

        availability = (planned_time - downtime) / planned_time if planned_time > 0 else 0
        performance = (actual_output / standard_output) / (planned_time - downtime) if (planned_time - downtime) > 0 else 0
        quality = good_units / actual_output if actual_output > 0 else 0

        oee = availability * performance * quality
        return oee * 100  # as percentage

    def close(self):
        if self.conn:
            self.conn.close()
