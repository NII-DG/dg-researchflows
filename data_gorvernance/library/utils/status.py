from .file import JsonFile

class TaskConfig:

    STATUS_UNFEASIBLE = "unfeasible"
    STATUS_UNEXECUTED = "unexecuted"
    STATUS_DOING = "doing"
    STATUS_DONE = "done"
    allowed_statuses = [STATUS_UNFEASIBLE, STATUS_UNEXECUTED, STATUS_DOING, STATUS_DONE]

    def __init__(self, id: str, name: str, is_multiple: bool, is_optional: bool, completed_count: int, dependent_task_ids: list[str], status: str, execution_environments: list[str], disabled: bool) -> None:
        self._id = id
        self._name = name
        self._is_multiple = is_multiple
        self._is_optional = is_optional
        self._completed_count = completed_count
        self._dependent_task_ids = dependent_task_ids
        self._set_status(status)
        self._execution_environments = execution_environments
        self._disabled = disabled

    def _set_status(self, status: str):
        if status in self.allowed_statuses:
            self._status = status
        else:
            raise ValueError

    @property
    def id(self):
        return self._id

    @property
    def completed_count(self):
        return self._completed_count

    @property
    def dependent_task_ids(self):
        return self._dependent_task_ids

    @property
    def status(self):
        return self._status

    @property
    def disabled(self):
        return self._disabled

    @status.setter
    def status(self, status: str):
        self._set_status(status)

    def to_dict(self):
        return {
            'id': self.id

        }


class Tasks:

    def __init__(self, tasks:list[dict]) -> None:
        self.config = [TaskConfig(**task) for task in tasks]

    def update_status(self):
        count_dict = {con.id: con.completed_count for con in self.config}

        for con in self.config:
            if con.status != con.STATUS_UNFEASIBLE:
                continue

            is_all_completed = all(count_dict.get(id, 0) >= 1 for id in con.dependent_task_ids)
            if is_all_completed:
                con.status = con.STATUS_UNEXECUTED

    def to_dict(self):
        return {
            'tasks': [
                con.to_dict() for con in self.config
            ]
        }

class StatusFile(JsonFile):

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def read(self):
        content = super().read()
        return Tasks(content)

    def write(self, tasks: Tasks):
        data = tasks.to_dict()
        super().write(data)
