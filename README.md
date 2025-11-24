# Time Taken for Tasks Tracker – Industrial-Level Project

This project is a **Time Taken for Tasks Tracker** designed for **Industrial Engineering** applications. It helps users track the time taken for various tasks, analyze productivity, and apply **industrial engineering principles** such as **Standard Time, Work Breakdown Structure (WBS), Overall Equipment Effectiveness (OEE), Pareto Analysis, and Gantt Charts**.

---

## 📌 **Features**

The application includes the following **industrial engineering features**:

| Feature                        | Description |
|-------------------------------|-------------|
| **Time Study & Standard Time** | Measure and set **standard time** for repetitive tasks. Compare actual vs. standard time and compute efficiency. |
| **Work Breakdown Structure (WBS)** | Break down a project into smaller, manageable tasks using a **parent-child task hierarchy**. |
| **OEE (Overall Equipment Effectiveness)** | Measure equipment performance using the **Availability × Performance × Quality** formula. |
| **Lean Manufacturing**         | Identify and eliminate waste by analyzing task times and process inefficiencies. |
| **Statistical Process Control (SPC)** | (Future enhancement) Use statistical tools to monitor and control process variability. |
| **Pareto Analysis**            | Identify the **“vital few”** tasks that contribute to the **“trivial many”** using the **80/20 rule**. |
| **Gantt Chart**                | Visualize **task scheduling and progress** with a Gantt chart. |

---

## 🛠️ **Implemented Features**

### 1. Standard Time Calculation
- **Set Standard Time:** Users can define a **standard time** (in seconds) for each task.
- **Compare Actual vs. Standard Time:** After completing a task, the system records the **actual time** spent.
- **Efficiency Calculation:**  
  \[
  \text{Efficiency} = \frac{\text{Actual Time}}{\text{Standard Time}} \times 100\%
  \]

### 2. Work Breakdown Structure (WBS)
- **Parent-Child Task Relationship:**  
  Each task can optionally have a **parent task**, allowing users to organize tasks into a **hierarchical structure**.
- **Tree View Display:**  
  Tasks are displayed in a **tree view**, where parent tasks are shown with expandable/collapsible subtasks.

### 3. Overall Equipment Effectiveness (OEE)
- **Track Equipment Performance:**  
  Users can add equipment and track:
  - **Planned Time**
  - **Downtime**
  - **Actual Output**
  - **Good Units Produced**
  - **Standard Output (units/hour)**

- **OEE Formula:**  
  \[
  \text{OEE} = \text{Availability} \times \text{Performance} \times \text{Quality}
  \]
  Where:
  - **Availability** = \(\frac{\text{Planned Time} - \text{Downtime}}{\text{Planned Time}}\)
  - **Performance** = \(\frac{\text{Actual Output}}{\text{Standard Output} \times \text{Available Time}}\)
  - **Quality** = \(\frac{\text{Good Units}}{\text{Total Units Produced}}\)

### 4. Pareto Analysis (80/20 Rule)
- **Identify Critical Tasks:**  
  After tasks are completed, the application identifies the **top 20% of tasks** that consume **80% of the total time**.
- **Pareto Chart:**  
  A chart is generated using **Matplotlib**, showing the cumulative percentage of time consumed by tasks.

### 5. Gantt Chart
- **Visualize Task Scheduling:**  
  Displays a **Gantt chart** showing the **start and end times** of each task, helping to visualize project progress.

---

## 📁 **Project Structure**
Time_Tracker/
│
├── main.py              # Main Application (Kivy GUI)
├── database.py          # SQLite Database Handling
├── task_screen.kv      # Task Management UI
├── pareto_screen.kv     # Pareto Analysis UI
├── gantt_screen.kv      # Gantt Chart UI
├── oee_screen.kv       # OEE Tracking UI
├── requirements.txt     # Python dependencies
└── README.md            # This file

---

## 📦 **Installation**

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Time_Tracker.git
cd Time_Tracker


```bash
pip install -r requirements.txt && python main.py


















# FEATURES
Time Study & Standard Time- Measure and set standard time for repetitive tasks.
Work Breakdown Structure (WBS) - Break down a project into smaller, manageable tasks.
OEE (Overall Equipment Effectiveness) - Measure equipment performance (Availability, Performance, Quality).
Lean Manufacturing - Identify and eliminate waste in processes.
Statistical Process Control (SPC) - Use statistical tools to monitor and control processes.
Pareto Analysis - Identify the “vital few” tasks that contribute to the “trivial many”.
Gantt Chart - Visualize task scheduling and progress.

1. Standard Time Calculation
Allow users to set a standard time for each task.
Compare actual time vs standard time.
Compute efficiency = Actual Time / Standard Time

2. Work Breakdown Structure
Add a parent_task_id field to link subtasks to parent tasks.
Display tasks in a tree view.

3. OEE measures how effectively a piece of equipment is used.
Formula:
OEE=Availability×Performance×Quality
Where:

* Availability = (Planned Time – Downtime) / Planned Time
* Performance = (Actual Output / Standard Output) / Available Time
* Quality = Good Units / Total Units Produced


4. Pareto Analysis
Pareto Analysis (80/20 Rule): Identify the top 20% of tasks that consume 80% of time.
How to Implement:

* After all tasks are completed, fetch all tasks with total_time > 0.
* Sort them by total_time descending.
* Plot a Pareto Chart using Matplotlib.

5. Basic Gantt Chart
Visualize task progress with a Gantt chart.

Time_Tracker/
|── main.py
├── database.py
├── task_screen.kv
├── pareto_screen.kv       # Optional
├── gantt_screen.kv        # Optional
├── requirements.txt
└── README.md

1. Install dependencies:
'''
pip install -r requirements.txt
'''

2. 
Run the app:
'''
python main.py
'''
