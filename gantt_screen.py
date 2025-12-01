# gantt_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from database import Database
import plotly.express as px
from plotly_widget import plotly_to_qwebengine
from datetime import datetime

class GanttScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.layout = QVBoxLayout(self)
        self.btn = QPushButton("Generate Gantt")
        self.status = QLabel("")
        self.btn.clicked.connect(self.generate)
        self.layout.addWidget(self.btn)
        self.layout.addWidget(self.status)
        self.chart = None

    def generate(self):
        tasks = self.db.get_all_tasks()
        rows = []
        for t in tasks:
            # t: id, name, desc, assigned_to, start_time, end_time, total_time, ...
            if t[4] and t[5]:
                try:
                    start = datetime.fromisoformat(t[4])
                    end = datetime.fromisoformat(t[5])
                    rows.append(dict(Task=f"[{t[0]}] {t[1]}", Start=start, Finish=end, Resource=t[3] or ""))
                except Exception:
                    continue
        if not rows:
            self.status.setText("No tasks with both start and end timestamps.")
            return
        fig = px.timeline(rows, x_start="Start", x_end="Finish", y="Task", color="Resource")
        fig.update_yaxes(autorange="reversed")
        view = plotly_to_qwebengine(fig)
        if self.chart:
            self.layout.removeWidget(self.chart)
            self.chart.deleteLater()
        self.chart = view
        self.layout.addWidget(view)
        self.status.setText(f"{len(rows)} tasks plotted")
