

_STATUS_UNFEASIBLE = "unfeasible"
_STATUS_UNEXECUTED = "unexecuted"
_STATUS_DOING = "doing"
_STATUS_DONE = "done"
_allowed_statuses = [_STATUS_UNFEASIBLE, _STATUS_UNEXECUTED, _STATUS_DOING, _STATUS_DONE]


class TaskStatus:

    def __init__(self, id:str, name:str, is_multiple:bool, is_optional:bool, completed_count:int, dependent_task_ids:list[str], status:str, execution_environments:list[str]) -> None:
        self._id = id
        self._name = name
        self._is_multiple = is_multiple
        self._is_optional = is_optional
        self._completed_count = completed_count
        self._dependent_task_ids = dependent_task_ids
        self._set_status(status)
        self._execution_environments = execution_environments

    def _set_status(self, status:str):
        if status in _allowed_statuses:
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

    @status.setter
    def status(self, status:str):
        self._set_status(status)


class StatusManager:

    def __init__(self, tasks) -> None:
        self.task_statuses = [TaskStatus(**task) for task in tasks]

    def update_status(self):
        count_dict = {ts.id: ts.completed_count for ts in self.task_statuses}

        for ts in self.task_statuses:
            if ts.status != _STATUS_UNFEASIBLE:
                continue

            is_all_completed = all(count_dict.get(id, 0) >= 1 for id in ts.dependent_task_ids)
            if is_all_completed:
                ts.status = _STATUS_UNEXECUTED


