from ..utils.file import JsonFile

__IS_COMPLETED = 'is_completed'
__TASKS = 'tasks'


class TaskStatus:

    __ID = 'id'
    __NAME = 'name'
    __IS_MULTIPLE = 'is_multiple'
    __IS_REQURED = 'is_required'
    __COMPLETED_COUNT = 'completed_count'
    __DEPENDENT_TASK_IDS = 'dependent_task_ids'
    __STATUS = 'status'
    __EXECUTION_ENVIRONMENTS = 'execution_environments'
    __DISABLED = 'disabled'

    STATUS_UNFEASIBLE = "unfeasible"
    STATUS_UNEXECUTED = "unexecuted"
    STATUS_DOING = "doing"
    STATUS_DONE = "done"
    allowed_statuses = [STATUS_UNFEASIBLE, STATUS_UNEXECUTED, STATUS_DOING, STATUS_DONE]

    def __init__(self, id: str, name: str, is_multiple: bool, is_required: bool, completed_count: int, dependent_task_ids: list[str], status: str, execution_environments: list[str], disabled: bool) -> None:
        self._id = id
        self._name = name
        self._is_multiple = is_multiple
        self._is_required = is_required
        self._completed_count = completed_count
        self._dependent_task_ids = dependent_task_ids
        self._set_status(status)
        self._execution_environments = execution_environments
        self._disable = disabled

    def _set_status(self, status: str):
        if status in self.allowed_statuses:
            self._status = status
        else:
            raise ValueError

    def add_execution_environments(self, id:str):
        self._execution_environments.append(id)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def is_required(self):
        return self._is_required

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
    def disable(self):
        return self._disable

    @status.setter
    def status(self, status: str):
        self._set_status(status)

    def to_dict(self):
        return {
            self.__ID: self.id
            self.__
        }


class SubflowStatus:

    def __init__(self, is_completed: bool, tasks: list[dict]) -> None:
        self._is_completed = is_completed
        self._tasks = [TaskStatus(**task) for task in tasks]

    @property
    def is_completed(self):
        return self._is_completed

    @property
    def tasks(self):
        return self._tasks

    @is_completed.setter
    def is_completed(self, is_completed: bool):
        self._is_completed = is_completed

    def update_task_unexcuted(self):
        count_dict = {con.id: con.completed_count for con in self.tasks}
        for con in self.tasks:
            if con.status != con.STATUS_UNFEASIBLE:
                continue
            is_all_completed = all(count_dict.get(id, 0) >= 1 for id in con.dependent_task_ids)
            if is_all_completed:
                con.status = con.STATUS_UNEXECUTED

    def to_dict(self):
        return {
            __IS_COMPLETED : self.is_completed,
            __TASKS: [
                con.to_dict() for con in self.tasks
            ]
        }


class StatusFile(JsonFile):

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def read(self):
        content = super().read()
        return SubflowStatus(content[__IS_COMPLETED], content[__TASKS])

    def write(self, tasks: SubflowStatus):
        data = tasks.to_dict()
        super().write(data)

    def is_completed(self)->bool:
        content = super().read()
        return content['is_completed']
