import streamlit as st
import pandas as pd
from datetime import datetime
import heapq
import networkx as nx
import os

# =========================
# File paths
# =========================
DATA_FILE = "../data/tasks.csv"
if not os.path.exists(DATA_FILE):
    os.makedirs("../data", exist_ok=True)
    df = pd.DataFrame(columns=["id","title","duration","deadline","priority","dependencies","completed"])
    df.to_csv(DATA_FILE, index=False)

# =========================
# Task Manager
# =========================
class TaskManager:
    def __init__(self):
        self.tasks = pd.read_csv(DATA_FILE)

    def add_task(self, title, duration, deadline, priority, dependencies=[]):
        self.tasks = pd.read_csv(DATA_FILE)  # reload
        # Prevent duplicate tasks with same title & deadline
        existing = self.tasks[(self.tasks.title == title) & (self.tasks.deadline == str(deadline))]
        if len(existing) > 0:
            st.warning(f"Task '{title}' already exists for this date!")
            return
        task_id = len(self.tasks) + 1
        dep_str = ",".join(map(str, dependencies))
        new_task = {"id": task_id, "title": title, "duration": duration, "deadline": deadline,
                    "priority": priority, "dependencies": dep_str, "completed": False}
        self.tasks = pd.concat([self.tasks, pd.DataFrame([new_task])], ignore_index=True)
        self.tasks.to_csv(DATA_FILE, index=False)
        st.success(f"Task '{title}' added successfully!")

    def complete_task(self, task_id, completed=True):
        self.tasks = pd.read_csv(DATA_FILE)
        self.tasks.loc[self.tasks.id == task_id, "completed"] = completed
        self.tasks.to_csv(DATA_FILE, index=False)

    def list_tasks(self):
        self.tasks = pd.read_csv(DATA_FILE)
        return self.tasks

# =========================
# Scheduler
# =========================
class Scheduler:
    def __init__(self):
        self.tasks = pd.read_csv(DATA_FILE)

    def priority_schedule(self):
        self.tasks = pd.read_csv(DATA_FILE)
        heap = []
        for _, row in self.tasks.iterrows():
            if not row.completed:
                deadline = datetime.strptime(row.deadline, "%Y-%m-%d")
                heapq.heappush(heap, (-row.priority, deadline, row.id, row.title))
        schedule = []
        while heap:
            _, _, task_id, title = heapq.heappop(heap)
            schedule.append((task_id, title))
        return schedule

    def dependency_schedule(self):
        self.tasks = pd.read_csv(DATA_FILE)
        G = nx.DiGraph()
        for _, row in self.tasks.iterrows():
            G.add_node(row.id, title=row.title)
            if pd.notna(row.dependencies) and row.dependencies != "":
                for dep in str(row.dependencies).split(","):
                    if dep.strip().isdigit():
                        G.add_edge(int(dep), row.id)
        try:
            order = list(nx.topological_sort(G))
            return [(task_id, self.tasks[self.tasks.id == task_id].title.values[0]) for task_id in order]
        except nx.NetworkXUnfeasible:
            st.error("Cycle detected in dependencies! Cannot schedule tasks.")
            return []

    def ai_suggest_tasks(self, max_tasks=5):
        """Suggest top tasks to do today based on priority, deadline, dependencies, completion."""
        self.tasks = pd.read_csv(DATA_FILE)
        today = datetime.today().strftime("%Y-%m-%d")
        suggestions = []
        for _, row in self.tasks.iterrows():
            if row.completed:
                continue
            score = 0
            # High priority
            score += row.priority * 2
            # Deadline soon
            days_left = (datetime.strptime(row.deadline, "%Y-%m-%d") - datetime.today()).days
            score += max(0, 5 - days_left)
            # Dependencies not completed
            if pd.notna(row.dependencies) and row.dependencies != "":
                for dep in str(row.dependencies).split(","):
                    if dep.strip().isdigit():
                        dep_id = int(dep)
                        dep_row = self.tasks[self.tasks.id == dep_id]
                        if not dep_row.empty and not dep_row.iloc[0].completed:
                            score -= 3
            suggestions.append((score, row.id, row.title, row.duration))
        suggestions.sort(reverse=True)
        return suggestions[:max_tasks]

# =========================
# Productivity Tracker
# =========================
class ProductivityTracker:
    def __init__(self):
        self.tasks = pd.read_csv(DATA_FILE)

    def daily_completion_rate(self):
        self.tasks = pd.read_csv(DATA_FILE)
        today = datetime.today().strftime("%Y-%m-%d")
        completed_today = self.tasks[(self.tasks.completed == True) & (self.tasks.deadline == today)]
        total_today = self.tasks[self.tasks.deadline == today]
        if len(total_today) == 0:
            return 0
        return len(completed_today) / len(total_today)

    def overall_completion_rate(self):
        self.tasks = pd.read_csv(DATA_FILE)
        completed = self.tasks[self.tasks.completed == True]
        if len(self.tasks) == 0:
            return 0
        return len(completed) / len(self.tasks)

# =========================
# Initialize
# =========================
tm = TaskManager()
scheduler = Scheduler()
tracker = ProductivityTracker()

# =========================
# Streamlit UI
# =========================
st.title("Smart Study & Productivity Planner")

# -------------------------
# Add New Task
# -------------------------
st.header("Add New Task")
with st.form(key="task_form"):
    title = st.text_input("Task Title")
    duration = st.number_input("Duration (hours)", min_value=0)
    deadline = st.date_input("Deadline")
    priority = st.slider("Priority (1-low,5-high)", 1, 5)
    dependencies = st.text_input("Dependencies (comma-separated task IDs)")
    
    submit_button = st.form_submit_button("Add Task")
    
    if submit_button:
        deps_list = [int(x) for x in dependencies.split(",") if x.strip().isdigit()]
        tm.add_task(title, duration, str(deadline), priority, deps_list)
        # Refresh scheduler & tracker after adding
        scheduler = Scheduler()
        tracker = ProductivityTracker()

# -------------------------
# Mark Tasks Completed
# -------------------------
st.header("Mark Tasks Completed")
tasks = tm.list_tasks()
for idx, row in tasks.iterrows():
    checked = st.checkbox(f"{row['id']}: {row['title']}", value=row['completed'], key=f"task_{row['id']}")
    tm.complete_task(row['id'], checked)

# -------------------------
# Scheduled Tasks
# -------------------------
st.header("Scheduled Tasks")
scheduler = Scheduler()  # reload
st.subheader("By Priority & Deadline")
priority_schedule = scheduler.priority_schedule()
for task_id, title in priority_schedule:
    st.write(f"{task_id}: {title}")

st.subheader("By Dependencies")
dep_schedule = scheduler.dependency_schedule()
for task_id, title in dep_schedule:
    st.write(f"{task_id}: {title}")

# -------------------------
# AI Task Suggestions
# -------------------------
st.header("AI Suggested Tasks for Today")
scheduler = Scheduler()  # reload tasks
ai_tasks = scheduler.ai_suggest_tasks(max_tasks=5)
total_time = sum(task[3] for task in ai_tasks)
if ai_tasks:
    for score, task_id, title, duration in ai_tasks:
        st.markdown(f"<span style='color:green; font-weight:bold;'>{task_id}: {title} (Est. {duration}h)</span>", unsafe_allow_html=True)
    st.write(f"Total Estimated Time: {total_time} hours")
else:
    st.write("No tasks to suggest! All tasks completed or blocked by dependencies.")

# -------------------------
# Productivity Stats
# -------------------------
st.header("Productivity Stats")
tracker = ProductivityTracker()  # reload tasks
st.write(f"Overall Completion Rate: {tracker.overall_completion_rate()*100:.2f}%")
st.write(f"Today's Completion Rate: {tracker.daily_completion_rate()*100:.2f}%")
