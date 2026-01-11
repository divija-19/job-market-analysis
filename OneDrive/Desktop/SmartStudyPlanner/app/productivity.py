import pandas as pd
from datetime import datetime

DATA_FILE = "data/tasks.csv"

class ProductivityTracker:
    def __init__(self):
        self.tasks = pd.read_csv(DATA_FILE)

    def daily_completion_rate(self):
        today = datetime.today().strftime("%Y-%m-%d")
        completed_today = self.tasks[(self.tasks.completed == True) & (self.tasks.deadline == today)]
        total_today = self.tasks[self.tasks.deadline == today]
        if len(total_today) == 0:
            return 0
        return len(completed_today) / len(total_today)

    def overall_completion_rate(self):
        completed = self.tasks[self.tasks.completed == True]
        if len(self.tasks) == 0:
            return 0
        return len(completed) / len(self.tasks)
