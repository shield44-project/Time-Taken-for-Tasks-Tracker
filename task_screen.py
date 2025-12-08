# task_screen.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QDialog, QFormLayout, QLineEdit, QTextEdit, QSpinBox, QComboBox, QMessageBox
)
from database import Database
from datetime import datetime
import industrial_datasets

class TaskDialog(QDialog):
    def __init__(self, db, parent=None, task=None):
        super().__init__(parent)
        self.db = db
        self.task = task  # None for add, tuple for edit
        self.setWindowTitle("Add Task" if task is None else "Edit Task")
        layout = QFormLayout(self)

        self.name = QLineEdit(task[1] if task else "")
        self.desc = QTextEdit(task[2] if task else "")
        self.assigned = QLineEdit(task[3] if task else "")
        self.std_time = QLineEdit(str(task[7] if task and task[7] is not None else "0"))

        # Category selector
        categories = ['None'] + industrial_datasets.get_all_categories()
        self.category = QComboBox()
        self.category.addItems(categories)
        if task and len(task) > 11 and task[11]:
            idx = self.category.findText(task[11])
            if idx >= 0:
                self.category.setCurrentIndex(idx)

        # parent selector
        parents = ['None'] + [str(t[0]) + " — " + t[1] for t in self.db.get_all_tasks() if t[10] is None]
        self.parent = QComboBox()
        self.parent.addItems(parents)
        if task and task[10]:
            # find index
            for i, p in enumerate(parents):
                if p.startswith(str(task[10]) + " "):
                    self.parent.setCurrentIndex(i)
                    break

        layout.addRow("Task Name:", self.name)
        layout.addRow("Description:", self.desc)
        layout.addRow("Assigned To:", self.assigned)
        layout.addRow("Standard Time (s):", self.std_time)
        layout.addRow("Category:", self.category)
        layout.addRow("Parent Task:", self.parent)

        buttons = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)
        layout.addRow(buttons)

    def values(self):
        parent_text = self.parent.currentText()
        parent_id = None
        if parent_text != 'None':
            parent_id = int(parent_text.split(" ")[0])
        try:
            std = float(self.std_time.text())
        except:
            std = 0
        
        category_text = self.category.currentText()
        category = None if category_text == 'None' else category_text
        
        return {
            "name": self.name.text().strip(),
            "desc": self.desc.toPlainText().strip(),
            "assigned": self.assigned.text().strip(),
            "std": std,
            "parent": parent_id,
            "category": category
        }

class TaskScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self.btn_add = QPushButton("Add Task")
        self.btn_edit = QPushButton("Edit Task")
        self.btn_delete = QPushButton("Delete Task")
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_load_samples = QPushButton("Load Sample Tasks")
        top.addWidget(self.btn_add)
        top.addWidget(self.btn_edit)
        top.addWidget(self.btn_delete)
        top.addWidget(self.btn_start)
        top.addWidget(self.btn_stop)
        top.addWidget(self.btn_load_samples)

        layout.addLayout(top)

        self.listw = QListWidget()
        layout.addWidget(self.listw)
        self.info = QLabel("Select a task to see details")
        layout.addWidget(self.info)

        self.btn_add.clicked.connect(self.add_task)
        self.btn_edit.clicked.connect(self.edit_task)
        self.btn_delete.clicked.connect(self.delete_task)
        self.listw.itemSelectionChanged.connect(self.show_info)
        self.btn_start.clicked.connect(self.start_task)
        self.btn_stop.clicked.connect(self.stop_task)
        self.btn_load_samples.clicked.connect(self.load_sample_tasks)

        self.refresh()

    def refresh(self):
        self.listw.clear()
        tasks = self.db.get_all_tasks()
        # show parent tasks first
        for t in tasks:
            category_str = f" [{t[11]}]" if len(t) > 11 and t[11] else ""
            display = f"[{t[0]}] {t[1]}{category_str} — Status: {t[9] or 'N/A'}"
            item = QListWidgetItem(display)
            item.setData(1000, t)  # store full tuple
            self.listw.addItem(item)

    def show_info(self):
        it = self.listw.currentItem()
        if not it: 
            self.info.setText("Select a task to see details")
            return
        t = it.data(1000)
        category = t[11] if len(t) > 11 and t[11] else 'N/A'
        txt = f"""
<b>{t[1]}</b>
Assigned to: {t[3] or 'N/A'}
Category: {category}
Status: {t[9] or 'N/A'}
Standard Time: {t[7] if t[7] is not None else 0} s
Total Time: {t[6] if t[6] is not None else 0:.2f} s
Description: {t[2] or 'N/A'}
"""
        self.info.setText(txt)

    def add_task(self):
        dlg = TaskDialog(self.db, self)
        if dlg.exec() == QDialog.Accepted:
            v = dlg.values()
            if not v['name']:
                QMessageBox.warning(self, "Error", "Task name required")
                return
            self.db.add_task(v['name'], v['desc'], v['assigned'], v['std'], v['parent'], v['category'])
            self.refresh()

    def edit_task(self):
        it = self.listw.currentItem()
        if not it: return
        t = it.data(1000)
        dlg = TaskDialog(self.db, self, task=t)
        if dlg.exec() == QDialog.Accepted:
            v = dlg.values()
            self.db.update_task(t[0], v['name'], v['desc'], v['assigned'], v['std'], v['parent'], v['category'])
            self.refresh()

    def load_sample_tasks(self):
        """Load sample industrial tasks from the datasets."""
        # Show dialog to select which task group to load
        groups = industrial_datasets.get_task_groups()
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Load Sample Industrial Tasks")
        dlg.setMinimumWidth(400)
        layout = QVBoxLayout(dlg)
        
        layout.addWidget(QLabel("Select an industrial task group to load:"))
        
        group_list = QListWidget()
        for group in groups:
            group_data = industrial_datasets.INDUSTRIAL_TASKS[group]
            item_text = f"{group} - {group_data['description']}"
            group_list.addItem(item_text)
        layout.addWidget(group_list)
        
        buttons = QHBoxLayout()
        load_btn = QPushButton("Load Selected")
        load_all_btn = QPushButton("Load All")
        cancel_btn = QPushButton("Cancel")
        
        buttons.addWidget(load_btn)
        buttons.addWidget(load_all_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        def load_selected():
            if not group_list.currentItem():
                QMessageBox.warning(dlg, "Error", "Please select a task group")
                return
            
            selected_text = group_list.currentItem().text()
            group_name = selected_text.split(" - ")[0]
            self._load_task_group(group_name)
            dlg.accept()
        
        def load_all():
            for group in groups:
                self._load_task_group(group)
            dlg.accept()
        
        load_btn.clicked.connect(load_selected)
        load_all_btn.clicked.connect(load_all)
        cancel_btn.clicked.connect(dlg.reject)
        
        dlg.exec()

    def _load_task_group(self, group_name):
        """Load tasks from a specific group."""
        tasks = industrial_datasets.get_tasks_by_group(group_name)
        category = industrial_datasets.get_category_for_group(group_name)
        
        if not tasks:
            return
        
        # Create parent task for the group
        parent_desc = industrial_datasets.INDUSTRIAL_TASKS[group_name]['description']
        self.db.add_task(
            task_name=group_name,
            description=parent_desc,
            assigned_to="Industrial Engineering",
            standard_time=0,
            parent_task_id=None,
            category=category
        )
        
        # Get the parent task ID
        all_tasks = self.db.get_all_tasks()
        parent_id = all_tasks[-1][0]  # Last inserted task
        
        # Add all subtasks
        for task_key, task_data in tasks.items():
            self.db.add_task(
                task_name=task_data['name'],
                description=task_data['description'],
                assigned_to=task_data['assigned_to'],
                standard_time=task_data['standard_time'],
                parent_task_id=parent_id,
                category=category
            )
        
        self.refresh()
        QMessageBox.information(
            self, 
            "Success", 
            f"Loaded {len(tasks)} sample tasks from {group_name}"
        )

    def delete_task(self):
        it = self.listw.currentItem()
        if not it: return
        t = it.data(1000)
        confirm = QMessageBox.question(self, "Confirm", f"Delete task [{t[0]}] {t[1]}?")
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.delete_task(t[0])
            self.refresh()

    def start_task(self):
        it = self.listw.currentItem()
        if not it: return
        t = it.data(1000)
        self.db.start_task(t[0])
        self.refresh()

    def stop_task(self):
        it = self.listw.currentItem()
        if not it: return
        t = it.data(1000)
        total = self.db.stop_task(t[0])
        QMessageBox.information(self, "Task Stopped", f"Total time recorded: {total:.2f} seconds")
        self.refresh()
