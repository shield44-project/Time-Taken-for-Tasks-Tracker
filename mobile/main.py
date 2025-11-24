from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = 'http://YOUR_SERVER_IP:5000/api'  # Change this to your server IP


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        layout.add_widget(Label(
            text='Task Time Tracker',
            font_size='24sp',
            size_hint_y=0.2
        ))
        
        # Username
        self.username_input = TextInput(
            hint_text='Username',
            multiline=False,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.username_input)
        
        # Password
        self.password_input = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.password_input)
        
        # Login button
        login_btn = Button(
            text='Login',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 1)
        )
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)
        
        # Status label
        self.status_label = Label(
            text='',
            size_hint_y=0.2,
            color=(1, 0, 0, 1)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        try:
            response = requests.post(
                f'{API_BASE_URL}/mobile/login',
                json={'username': username, 'password': password},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    app = App.get_running_app()
                    app.user_data = data['user']
                    app.root.current = 'tasks'
                else:
                    self.status_label.text = 'Invalid credentials'
            else:
                self.status_label.text = 'Login failed'
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'


class TasksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        header.add_widget(Label(text='My Tasks', font_size='20sp'))
        
        refresh_btn = Button(
            text='Refresh',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        refresh_btn.bind(on_press=self.load_tasks)
        header.add_widget(refresh_btn)
        
        self.layout.add_widget(header)
        
        # Tasks list
        self.scroll_view = ScrollView()
        self.tasks_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None
        )
        self.tasks_layout.bind(minimum_height=self.tasks_layout.setter('height'))
        self.scroll_view.add_widget(self.tasks_layout)
        self.layout.add_widget(self.scroll_view)
        
        # Active timer section
        self.active_timer_label = Label(
            text='No active timer',
            size_hint_y=0.1,
            color=(0, 0.8, 0, 1)
        )
        self.layout.add_widget(self.active_timer_label)
        
        # Logout button
        logout_btn = Button(
            text='Logout',
            size_hint_y=0.1,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        logout_btn.bind(on_press=self.logout)
        self.layout.add_widget(logout_btn)
        
        self.add_widget(self.layout)
        
        # Schedule periodic updates
        Clock.schedule_interval(self.check_active_timer, 5)
    
    def on_enter(self):
        self.load_tasks()
        self.check_active_timer()
    
    def load_tasks(self, *args):
        try:
            app = App.get_running_app()
            user_id = app.user_data['id']
            
            response = requests.get(
                f'{API_BASE_URL}/tasks?user_id={user_id}',
                timeout=5
            )
            
            if response.status_code == 200:
                tasks = response.json()
                self.display_tasks(tasks)
        except Exception as e:
            print(f'Error loading tasks: {e}')
    
    def display_tasks(self, tasks):
        self.tasks_layout.clear_widgets()
        
        for task in tasks:
            task_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=120,
                padding=10
            )
            
            # Task title and status
            title_layout = BoxLayout(size_hint_y=0.3)
            title_layout.add_widget(Label(
                text=task['title'],
                font_size='16sp',
                bold=True,
                halign='left'
            ))
            title_layout.add_widget(Label(
                text=task['status'].upper(),
                size_hint_x=0.4,
                color=self.get_status_color(task['status'])
            ))
            task_box.add_widget(title_layout)
            
            # Task info
            info_text = f"{task['category']} | {task['priority']} | {task['actual_time']:.1f}h"
            task_box.add_widget(Label(
                text=info_text,
                size_hint_y=0.3,
                font_size='12sp'
            ))
            
            # Start button
            if task['status'] != 'completed':
                start_btn = Button(
                    text='Start Timer',
                    size_hint_y=0.4,
                    background_color=(0.2, 0.6, 1, 1)
                )
                start_btn.bind(on_press=lambda x, t=task: self.start_timer(t['id']))
                task_box.add_widget(start_btn)
            
            self.tasks_layout.add_widget(task_box)
    
    def start_timer(self, task_id):
        try:
            response = requests.post(
                f'{API_BASE_URL}/timelogs',
                json={'task_id': task_id},
                timeout=5
            )
            
            if response.status_code == 201:
                self.active_timer_label.text = 'Timer started!'
                self.check_active_timer()
            else:
                data = response.json()
                self.active_timer_label.text = data.get('error', 'Failed to start timer')
        except Exception as e:
            print(f'Error starting timer: {e}')
    
    def check_active_timer(self, *args):
        try:
            response = requests.get(
                f'{API_BASE_URL}/timelogs/active',
                timeout=5
            )
            
            if response.status_code == 200:
                log = response.json()
                if log:
                    # Get task details
                    task_response = requests.get(
                        f'{API_BASE_URL}/tasks/{log["task_id"]}',
                        timeout=5
                    )
                    if task_response.status_code == 200:
                        task = task_response.json()
                        self.active_timer_label.text = f'Active: {task["title"]}'
                else:
                    self.active_timer_label.text = 'No active timer'
        except Exception as e:
            print(f'Error checking active timer: {e}')
    
    def get_status_color(self, status):
        colors = {
            'pending': (0.5, 0.5, 0.5, 1),
            'in_progress': (1, 0.8, 0, 1),
            'completed': (0, 0.8, 0, 1),
            'on_hold': (0.8, 0, 0, 1)
        }
        return colors.get(status, (0.5, 0.5, 0.5, 1))
    
    def logout(self, instance):
        app = App.get_running_app()
        app.user_data = None
        app.root.current = 'login'


class TaskTimeTrackerApp(App):
    user_data = None
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(TasksScreen(name='tasks'))
        return sm


if __name__ == '__main__':
    TaskTimeTrackerApp().run()
