class Storage:
    def __init__(self):
        self.tasks = {}
        self.task_counter = 1

    def clear(self):
        self.tasks = {}
        self.task_counter = 1

# Глобальный инстанс хранилища
db = Storage()