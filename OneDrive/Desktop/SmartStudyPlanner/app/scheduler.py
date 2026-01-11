import heapq
import networkx as nx
import pandas as pd
from datetime import datetime

DATA_FILE = "data/tasks.csv"

class Scheduler:
    def __init__(self):
        self.tasks = pd.read_csv(DATA_FILE)

    def priority_schedule(self):
        """Schedule tasks based on priority + nearest deadline"""
        heap = []
        for _, row in self.tasks.iterrows():
            if not row.completed:
                deadline = datetime.strptime(row.deadline, "%Y-%m-%d")
                # Negative priority because heapq is min-heap
                heapq.heappush(heap, (-row.priority, deadline, row.id, row.title))
        schedule = []
        while heap:
            _, _, task_id, title = heapq.heappop(heap)
            schedule.append((task_id, title))
        return schedule

    def dependency_schedule(self):
        """Schedule tasks using topological sort based on dependencies"""
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
            print("Cycle detected in dependencies! Cannot schedule tasks.")
            return []
