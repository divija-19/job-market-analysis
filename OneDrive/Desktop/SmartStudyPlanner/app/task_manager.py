import pandas as pd
import os
from datetime import datetime

DATA_FILE = "data/tasks.csv"

class TaskManager:
    def __init__(self):
        if not os.path.exists(DATA_FILE):
            df = pd.DataFrame(columns=["id", "title", "duration", "deadline", "priority", "dependencies", "completed"])
            df.to_csv(DATA_FILE, index=False)
        self.tasks = pd.read_csv(DATA_FILE)

    def add_task(self, title, duration, deadline, priority, dependencies=[]):
        task_id = len(self.tasks) + 1
        dep_str = ",".join(map(str, dependencies))
        new_task = {"id": task_id, "title": title, "duration": duration, "deadline": deadline,
                    "priority": priority, "dependencies": dep_str, "completed": False}
        self.tasks = pd.concat([self.tasks, pd.DataFrame([new_task])], ignore_index=True)
        self.tasks.to_csv(DATA_FILE, index=False)
        print(f"Task '{title}' added successfully!")

    def complete_task(self, task_id):
        self.tasks.loc[self.tasks.id == task_id, "completed"] = True
        self.tasks.to_csv(DATA_FILE, index=False)
        print(f"Task ID {task_id} marked as completed.")

    def list_tasks(self):
        return self.tasks
