# oee_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QLineEdit, QMessageBox, QListWidget, QListWidgetItem
from database import Database
import plotly.graph_objects as go
from plotly_widget import plotly_to_qwebengine

class OeeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.layout = QVBoxLayout(self)

        form = QHBoxLayout()
        self.name = QLineEdit(); self.name.setPlaceholderText("Equipment name")
        self.planned = QLineEdit(); self.planned.setPlaceholderText("Planned time (hours)")
        self.std_out = QLineEdit(); self.std_out.setPlaceholderText("Std output (units/hour)")
        self.btn_add = QPushButton("Add")
        self.btn_add.clicked.connect(self.add_equipment)
        form.addWidget(self.name)
        form.addWidget(self.planned)
        form.addWidget(self.std_out)
        form.addWidget(self.btn_add)
        self.layout.addLayout(form)

        self.equip_list = QListWidget()
        self.layout.addWidget(self.equip_list)

        self.btn_calc = QPushButton("Calculate OEE (avg)")
        self.btn_calc.clicked.connect(self.calculate_oee)
        self.layout.addWidget(self.btn_calc)

        self.summary = QLabel("OEE: --")
        self.layout.addWidget(self.summary)

        self.chart = None
        self.refresh()

    def refresh(self):
        self.equip_list.clear()
        for eq in self.db.get_equipment():
            eq_id, name, planned, downtime, actual, good, std = eq
            it = QListWidgetItem(f"[{eq_id}] {name} — Planned: {planned}h, Down: {downtime}h, Actual: {actual}, Good: {good}")
            it.setData(1000, eq)
            self.equip_list.addItem(it)

    def add_equipment(self):
        try:
            planned = float(self.planned.text())
            std_out = float(self.std_out.text())
        except:
            QMessageBox.warning(self, "Invalid", "Planned time and standard output must be numbers")
            return
        self.db.add_equipment(self.name.text().strip(), planned, std_out)
        self.name.clear(); self.planned.clear(); self.std_out.clear()
        self.refresh()

    def calculate_oee(self):
        equipments = self.db.get_equipment()
        if not equipments:
            self.summary.setText("No equipment")
            return
        oees = []
        labels = []
        for eq in equipments:
            oid = eq[0]
            oee = self.db.compute_oee(oid)
            oees.append(oee)
            labels.append(eq[1] or f"EQ{oid}")
        avg = sum(oees) / len(oees)
        self.summary.setText(f"OEE Average: {avg:.2f}%")

        fig = go.Figure([go.Bar(x=labels, y=oees, text=[f"{v:.2f}%" for v in oees], textposition="auto")])
        fig.update_layout(title="OEE per Equipment", yaxis=dict(title="OEE %"))
        view = plotly_to_qwebengine(fig)
        if self.chart:
            self.layout.removeWidget(self.chart)
            self.chart.deleteLater()
        self.chart = view
        self.layout.addWidget(view)
