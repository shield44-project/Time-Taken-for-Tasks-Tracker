# pareto_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from database import Database
import plotly.graph_objects as go
from plotly_widget import plotly_to_qwebengine

class ParetoScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        top_btn = QPushButton("Generate Pareto")
        self.status = QLabel("")
        top_btn.clicked.connect(self.generate)
        layout.addWidget(top_btn)
        layout.addWidget(self.status)
        self.chart_holder = None
        self.layout = layout

    def generate(self):
        tasks = self.db.get_all_tasks()
        times = [(t[1], t[6] or 0) for t in tasks if (t[6] or 0) > 0]
        if not times:
            self.status.setText("No completed tasks with recorded time.")
            return
        times.sort(key=lambda x: x[1], reverse=True)
        names = [n for n, _ in times]
        durations = [d for _, d in times]
        total = sum(durations)
        cum = []
        s = 0
        for d in durations:
            s += d
            cum.append(s/total*100)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=names, y=durations, name='Time (s)'))
        fig.add_trace(go.Scatter(x=names, y=cum, name='Cumulative %', yaxis='y2', mode='lines+markers'))
        fig.update_layout(
            title="Pareto — cumulative time",
            xaxis_tickangle=-45,
            yaxis=dict(title='Time (s)'),
            yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 100])
        )

        view = plotly_to_qwebengine(fig)
        # clear previous
        if self.chart_holder:
            self.layout.removeWidget(self.chart_holder)
            self.chart_holder.deleteLater()
        self.chart_holder = view
        self.layout.addWidget(view)
        self.status.setText(f"Total tasks used: {len(names)}")
