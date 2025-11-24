# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.lang import Builder
from datetime import datetime
from database import Database
from matplotlib.figure import Figure
from matplotlib.backends.backend_kivy import FigureCanvasKivy
import matplotlib.pyplot as plt

# Load KV files
Builder.load_file('task_screen.kv')
Builder.load_file('pareto_screen.kv')
Builder.load_file('gantt_screen.kv')
Builder.load_file('oee_screen.kv')

# === TASK SCREEN ===

class TaskScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.layout = BoxLayout(orientation='vertical')
        self.task_container = BoxLayout(orientation='vertical', size_hint=(1, 0.9))
        self.scroll = BoxLayout(orientation='vertical')
        self.scroll.add_widget(self.task_container)
        self.layout.add_widget(self.scroll)

        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        add_btn = Button(text="Add Task", size_hint=(0.2, 1))
        add_btn.bind(on_press=self.show_add_task_popup)
        top_bar.add_widget(add_btn)
        self.layout.add_widget(top_bar)

        self.add_widget(self.layout)
        self.refresh_tasks()

    def refresh_tasks(self, *args):
        self.task_container.clear_widgets()
        tasks = self.db.get_all_tasks()
        parent_tasks = {t[0]: t for t in tasks if t[10] is None}
        child_tasks = {pid: [] for pid in parent_tasks}
        
        for t in tasks:
            if t[10] is not None:
                child_tasks.get(t[10], []).append(t)

        for pid, parent in parent_tasks.items():
            parent_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
            
            info = BoxLayout(orientation='vertical')
            Label(text=f"📁 {parent[1]}", bold=True, font_size='18sp').bind(size=info.size)
            Label(text=f"Assigned to: {parent[3] or 'N/A'}").text_size = (200, None)
            status = parent[9]
            status_color = (0,1,0,1) if status == 'Completed' else (1,0,0,1) if status == 'In Progress' else (0.5,0.5,0.5,1)
            Label(text=f"Status: {status}", color=status_color).halign = 'left'
            
            info.add_widget(Label(text=f"Description: {parent[2] or 'N/A'}"))
            info.add_widget(Label(text=f"Standard Time: {parent[7]:.2f}s"))
            info.add_widget(Label(text=f"Efficiency: {parent[8]:.2f}%"))
            parent_layout.add_widget(info)

            action = BoxLayout(orientation='vertical', spacing=5)
            if parent[9] == 'Pending':
                btn_start = Button(text="Start", size_hint=(None, None), width=100, height=40)
                btn_start.bind(on_press=lambda b, tid=parent[0]: self.start_task(tid))
                action.add_widget(btn_start)
            elif parent[9] == 'In Progress':
                btn_stop = Button(text="Stop", size_hint=(None, None), width=100, height=40)
                btn_stop.bind(on_press=lambda b, tid=parent[0]: self.stop_task(tid))
                action.add_widget(btn_stop)

            btn_edit = Button(text="Edit", size_hint=(None, None), width=100, height=40)
            btn_edit.bind(on_press=lambda b, tid=parent[0]: self.show_edit_task_popup(tid))
            action.add_widget(btn_edit)

            btn_delete = Button(text="Delete", size_hint=(None, None), width=100, height=40)
            btn_delete.bind(on_press=lambda b, tid=parent[0]: self.delete_task(tid))
            action.add_widget(btn_delete)

            parent_layout.add_widget(action)
            self.task_container.add_widget(parent_layout)

            child_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=0, spacing=3)
            for child in child_tasks.get(pid, []):
                child_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
                Label(text=f"  ➤ {child[1]}", size_hint=(0.7, 1))
                Label(text=f"{child[7]:.2f}s", size_hint=(0.3, 1))
                child_box.bind(on_press=lambda b, cid=child[0]: self.show_edit_task_popup(cid))
                child_layout.add_widget(child_box)
            parent_layout.add_widget(child_layout)

    def show_add_task_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.current_parent = None

        self.ti_name = TextInput(hint_text='Task Name', multiline=False)
        self.ti_desc = TextInput(hint_text='Description', multiline=True)
        self.ti_assign = TextInput(hint_text='Assigned To', multiline=False)
        self.ti_std_time = TextInput(hint_text='Standard Time (seconds)', input_filter='float', multiline=False, text='0')

        spinner = Spinner(
            text='None',
            values=('None',) + tuple(str(t[0]) for t in self.db.get_all_tasks() if t[10] is None),
            size_hint=(None, None), size=(200, 44)
        )
        spinner.bind(on_text=self.set_parent)

        content.add_widget(Label(text='Task Name:'))
        content.add_widget(self.ti_name)
        content.add_widget(Label(text='Description:'))
        content.add_widget(self.ti_desc)
        content.add_widget(Label(text='Assigned To:'))
        content.add_widget(self.ti_assign)
        content.add_widget(Label(text='Standard Time (seconds):'))
        content.add_widget(self.ti_std_time)
        content.add_widget(Label(text='Parent Task (optional):'))
        content.add_widget(spinner)

        popup = Popup(title='Add Task', content=content, size_hint=(0.8, 0.8))

        def submit(instance):
            name = self.ti_name.text
            if not name:
                Label(text='Task name required!').text_size = (200, 50)
                return
            try:
                std_time = float(self.ti_std_time.text)
            except:
                std_time = 0
            self.db.add_task(name, self.ti_desc.text, self.ti_assign.text, std_time, self.current_parent)
            popup.dismiss()
            self.refresh_tasks()

        btn_submit = Button(text='Submit', size_hint=(1, 0.15))
        btn_submit.bind(on_press=submit)
        content.add_widget(btn_submit)
        popup.open()

    def set_parent(self, spinner, value):
        if value == 'None':
            self.current_parent = None
        else:
            self.current_parent = int(value)

    def show_edit_task_popup(self, task_id):
        task = self.db.get_task(task_id)
        if not task:
            return
        _, name, desc, assign, _, _, total, std, eff, status, parent = task

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.ti_e_name = TextInput(text=name, multiline=False)
        self.ti_e_desc = TextInput(text=desc, multiline=True)
        self.ti_e_assign = TextInput(text=assign, multiline=False)
        self.ti_e_std_time = TextInput(text=str(std), input_filter='float', multiline=False)

        spinner = Spinner(
            text='None' if parent is None else str(parent),
            values=('None',) + tuple(str(t[0]) for t in self.db.get_all_tasks() if t[10] is None),
            size_hint=(None, None), size=(200, 44)
        )
        spinner.bind(on_text=lambda s, v: self.set_edit_parent(int(v) if v != 'None' else None))

        self.edit_parent = parent

        content.add_widget(Label(text='Task Name:'))
        content.add_widget(self.ti_e_name)
        content.add_widget(Label(text='Description:'))
        content.add_widget(self.ti_e_desc)
        content.add_widget(Label(text='Assigned To:'))
        content.add_widget(self.ti_e_assign)
        content.add_widget(Label(text='Standard Time:'))
        content.add_widget(self.ti_e_std_time)
        content.add_widget(Label(text='Parent Task:'))
        content.add_widget(spinner)

        popup = Popup(title='Edit Task', content=content, size_hint=(0.8, 0.8))

        def submit(instance):
            self.db.update_task(task_id, self.ti_e_name.text, self.ti_e_desc.text,
                                self.ti_e_assign.text, float(self.ti_e_std_time.text), self.edit_parent)
            popup.dismiss()
            self.refresh_tasks()

        btn_submit = Button(text='Update', size_hint=(1, 0.15))
        btn_submit.bind(on_press=submit)
        content.add_widget(btn_submit)
        popup.open()

    def set_edit_parent(self, value):
        self.edit_parent = int(value) if value != 'None' else None

    def start_task(self, task_id):
        self.db.start_task(task_id)
        self.refresh_tasks()

    def stop_task(self, task_id):
        self.db.stop_task(task_id)
        self.refresh_tasks()

    def delete_task(self, task_id):
        self.db.delete_task(task_id)
        self.refresh_tasks()

# === PARETO SCREEN ===

class ParetoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.layout = BoxLayout(orientation='vertical')
        self.btn = Button(text="Generate Pareto Chart", size_hint=(1, 0.1))
        self.btn.bind(on_press=self.generate_pareto)
        self.chart = FigureCanvasKivy()
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.chart)
        self.add_widget(self.layout)

    def generate_pareto(self, instance):
        tasks = self.db.get_all_tasks()
        times = [(t[1], t[6]) for t in tasks if t[6] > 0]  # (name, time)

        if len(times) == 0:
            Label(text="No completed tasks found.").text_size = (200, 50)
            return

        times.sort(key=lambda x: x[1], reverse=True)
        total_time = sum(t[1] for t in times)
        cum_time = 0
        labels = []
        percentages = []

        for name, t in times:
            cum_time += t
            pct = (cum_time / total_time) * 100
            labels.append(name)
            percentages.append(pct)
            if pct >= 80:
                break

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.plot(labels, percentages, 'bo-', label='Cumulative %')
        ax.set_title('Pareto Analysis')
        ax.set_xlabel('Tasks')
        ax.set_ylabel('Cumulative Time (%)')
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.legend()
        self.chart.figure = fig

# === GANTT SCREEN ===

class GanttScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.layout = BoxLayout(orientation='vertical')
        self.btn = Button(text="Generate Gantt Chart", size_hint=(1, 0.1))
        self.btn.bind(on_press=self.generate_gantt)
        self.chart = FigureCanvasKivy()
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.chart)
        self.add_widget(self.layout)

    def generate_gantt(self, instance):
        tasks = self.db.get_all_tasks()
        if len(tasks) == 0:
            return

        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        import dateutil.parser

        starts = []
        ends = []
        labels = []

        for t in tasks:
            if t[4] and t[5]:
                start_dt = datetime.fromisoformat(t[4])
                end_dt = datetime.fromisoformat(t[5])
                starts.append(start_dt)
                ends.append(end_dt)
                labels.append(t[1])

        if len(starts) == 0:
            return

        durations = [(e - s).total_seconds() / (24 * 3600) for s, e in zip(starts, ends)]

        y_pos = list(range(len(labels)))
        ax.barh(y_pos, durations, left=starts, height=0.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Time')
        ax.grid(True)
        self.chart.figure = fig

# === OEE SCREEN ===

class OeeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.equipment_name = TextInput(hint_text='Equipment Name', multiline=False)
        self.planned_time = TextInput(hint_text='Planned Time (hours)', input_filter='float', multiline=False)
        self.standard_output = TextInput(hint_text='Standard Output (units/hour)', input_filter='float', multiline=False)

        self.btn_add_eq = Button(text='Add Equipment')
        self.btn_add_eq.bind(on_press=self.add_equipment)

        self.equipment_list = BoxLayout(orientation='vertical', size_hint=(1, 0.6))

        self.btn_calc = Button(text='Calculate OEE', size_hint=(1, 0.1))
        self.btn_calc.bind(on_press=self.calculate_oee)

        self.oee_label = Label(text='OEE: --%')

        self.layout.add_widget(Label(text='Add New Equipment'))
        self.layout.add_widget(self.equipment_name)
        self.layout.add_widget(self.planned_time)
        self.layout.add_widget(self.standard_output)
        self.layout.add_widget(self.btn_add_eq)
        self.layout.add_widget(self.equipment_list)
        self.layout.add_widget(self.btn_calc)
        self.layout.add_widget(self.oee_label)

        self.add_widget(self.layout)
        self.load_equipment()

    def add_equipment(self, instance):
        name = self.equipment_name.text
        try:
            planned = float(self.planned_time.text)
            std_out = float(self.standard_output.text)
        except:
            Label(text='Invalid numbers').text_size = (200, 50)
            return
        self.db.add_equipment(name, planned, std_out)
        self.equipment_name.text = ''
        self.planned_time.text = ''
        self.standard_output.text = ''
        self.load_equipment()

    def load_equipment(self):
        self.equipment_list.clear_widgets()
        for eq in self.db.get_equipment():
            eq_id, name, planned, downtime, actual, good, std = eq
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)

            self.ti_downtime = TextInput(text=str(downtime), input_filter='float', multiline=False, size_hint=(0.3, 1))
            self.ti_actual = TextInput(text=str(actual), input_filter='int', multiline=False, size_hint=(0.3, 1))
            self.ti_good = TextInput(text=str(good), input_filter='int', multiline=False, size_hint=(0.3, 1))

            self.ti_downtime.bind(on_text=lambda i, eid=eq_id: self.update_equipment(eid, i.text, 'downtime'))
            self.ti_actual.bind(on_text=lambda i, eid=eq_id: self.update_equipment(eid, i.text, 'actual'))
            self.ti_good.bind(on_text=lambda i, eid=eq_id: self.update_equipment(eid, i.text, 'good'))

            box.add_widget(Label(text=name, size_hint=(0.4, 1)))
            box.add_widget(self.ti_downtime)
            box.add_widget(self.ti_actual)
            box.add_widget(self.ti_good)
            self.equipment_list.add_widget(box)

    def update_equipment(self, eq_id, value, field):
        try:
            val = float(value) if field != 'actual' and field != 'good' else int(value)
            eq = self.db.get_equipment(eq_id)
            if field == 'downtime':
                self.db.update_equipment(eq_id, val, eq[4], eq[5])
            elif field == 'actual':
                self.db.update_equipment(eq_id, eq[3], val, eq[5])
            elif field == 'good':
                self.db.update_equipment(eq_id, eq[3], eq[4], val)
        except:
            pass
        self.calculate_oee(None)

    def calculate_oee(self, instance):
        equipments = self.db.get_equipment()
        if len(equipments) == 0:
            self.oee_label.text = 'OEE: No equipment added'
            return
        oee_vals = [self.db.compute_oee(eq[0]) for eq in equipments]
        avg_oee = sum(oee_vals) / len(oee_vals)
        self.oee_label.text = f'OEE: {avg_oee:.2f}%'

# === APP ===

class TaskTrackerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TaskScreen(name='task_screen'))
        sm.add_widget(ParetoScreen(name='pareto_screen'))
        sm.add_widget(GanttScreen(name='gantt_screen'))
        sm.add_widget(OeeScreen(name='oee_screen'))
        return sm

if __name__ == '__main__':
    TaskTrackerApp().run()
