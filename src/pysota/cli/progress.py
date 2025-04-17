import contextvars

from rich.progress import Progress

progress_manager_var = contextvars.ContextVar("progress_manager")

class ProgressManager: 
    def __init__(self) -> None:
        self.progress = Progress()
        self.task_ids = {}

    def add_task(self, key, description, total):
        task_id = self.progress.add_task(description, total)
        self.task_ids[key] = task_id
        return task_id
    
    def advance(self, key):
        task_id = self.task_ids.get(key)
        if task_id is not None: 
            self.progress.advance(task_id)