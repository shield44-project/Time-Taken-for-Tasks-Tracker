# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton

from task_screen import TaskScreen
from pareto_screen import ParetoScreen
from gantt_screen import GanttScreen
from oee_screen import OeeScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Tracker — Dark Dashboard")
        self.resize(1200, 800)

        # ───────────────────────────────
        # Top navigation bar
        # ───────────────────────────────
        nav_bar = QWidget()
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(6)

        self.btn_tasks = QPushButton("Tasks")
        self.btn_pareto = QPushButton("Pareto")
        self.btn_gantt = QPushButton("Gantt")
        self.btn_oee = QPushButton("OEE")

        for btn in (self.btn_tasks, self.btn_pareto, self.btn_gantt, self.btn_oee):
            btn.setCheckable(True)
            btn.setMinimumHeight(36)
            nav_layout.addWidget(btn)

        # ───────────────────────────────
        # Screen container
        # ───────────────────────────────
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.container_layout.setSpacing(10)

        # Instantiate screens
        self.task_screen = TaskScreen()
        self.pareto_screen = ParetoScreen()
        self.gantt_screen = GanttScreen()
        self.oee_screen = OeeScreen()

        # Default screen
        self.container_layout.addWidget(self.task_screen)
        self.current = self.task_screen
        self.btn_tasks.setChecked(True)

        # Button signals
        self.btn_tasks.clicked.connect(lambda: self._switch(self.task_screen, self.btn_tasks))
        self.btn_pareto.clicked.connect(lambda: self._switch(self.pareto_screen, self.btn_pareto))
        self.btn_gantt.clicked.connect(lambda: self._switch(self.gantt_screen, self.btn_gantt))
        self.btn_oee.clicked.connect(lambda: self._switch(self.oee_screen, self.btn_oee))

        # ───────────────────────────────
        # Main layout
        # ───────────────────────────────
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(nav_bar)
        main_layout.addWidget(self.container)
        self.setCentralWidget(central)

    def _switch(self, widget, button):
        """Switch the visible screen widget."""
        # reset buttons
        for b in (self.btn_tasks, self.btn_pareto, self.btn_gantt, self.btn_oee):
            b.setChecked(False)
        button.setChecked(True)

        # replace screen
        self.container_layout.replaceWidget(self.current, widget)
        self.current.hide()
        widget.show()
        self.current = widget


def main():
    app = QApplication(sys.argv)

    # ───────────────────────────────
    # DARK THEME STYLESHEET (works on all PySide6 versions)
    # ───────────────────────────────
    dark_stylesheet = """
    QWidget {
        background-color: #121212;
        color: #EEEEEE;
        font-size: 14px;
    }
    QPushButton {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 6px;
    }
    QPushButton:hover {
        background-color: #333333;
    }
    QPushButton:checked {
        background-color: #444444;
    }
    QLineEdit, QTextEdit, QComboBox, QListWidget {
        background-color: #1A1A1A;
        border: 1px solid #333;
        color: #EEEEEE;
    }
    """
    app.setStyleSheet(dark_stylesheet)

    # Run app
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
