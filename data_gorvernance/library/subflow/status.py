from ..utils.file import JsonFile

_IS_COMPLETED = 'is_completed'
_TASKS = 'tasks'


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

    def increme_completed_count(self):
        self._completed_count += 1

    @property
    def dependent_task_ids(self):
        return self._dependent_task_ids

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status: str):
        self._set_status(status)

    @property
    def disable(self):
        return self._disable

    @disable.setter
    def disable(self, is_disable:bool):
        self._disable = is_disable

    @property
    def execution_environments(self):
        return self._execution_environments



    def to_dict(self):
        return {
            self.__ID: self._id,
            self.__NAME: self._name,
            self.__IS_MULTIPLE: self._is_multiple,
            self.__IS_REQURED: self._is_required,
            self.__COMPLETED_COUNT: self._completed_count,
            self.__DEPENDENT_TASK_IDS: self._dependent_task_ids,
            self.__STATUS: self._status,
            self.__EXECUTION_ENVIRONMENTS: self._execution_environments,
            self.__DISABLED: self._disable
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

    def update_task_enabled(self):
        """タスクの利用可能状態を更新する"""
        count_dict = {con.id: con.completed_count for con in self.tasks}
        for con in self.tasks:
            if con.status != con.STATUS_UNFEASIBLE:
                continue
            is_all_completed = all(count_dict.get(id, 0) >= 1 for id in con.dependent_task_ids)
            if is_all_completed:
                con.status = con.STATUS_UNEXECUTED

    def to_dict(self):
        return {
            _IS_COMPLETED : self.is_completed,
            _TASKS: [
                con.to_dict() for con in self.tasks
            ]
        }

    def get_task_by_task_id(self, id:str)->TaskStatus:
        for task in self._tasks:
            if task.id == id:
                return task
        raise Exception(f'Not Found task status by {id}')

    def doing_task_by_task_name(self, task_name:str, environment_id:str):
        for task in self._tasks:
            if task.name == task_name:
                ## status を実行中ステータスへ更新
                task.status = TaskStatus.STATUS_DOING
                task.add_execution_environments(environment_id)


    def completed_task_by_task_name(self, task_name:str, environment_id:str):
        # 対象タスクのステータスを完了に更新する。
        for task in self._tasks:
            if task.name == task_name:
                ## completed_countに１プラス
                task.increme_completed_count()
                ## ステータスへ更新
                if len(task.execution_environments) == 1:
                    task.status = TaskStatus.STATUS_DONE
                else:
                    continue
                ## 実行環境IDをリストから削除する。
                task._execution_environments.remove(environment_id)

        # 上記の更新を受け、下流の実行可能状態を更新する。
        for task in self._tasks:
            if len(task.dependent_task_ids) > 0 and task.status == TaskStatus.STATUS_UNFEASIBLE:
                # 上流依存タスクを持ち、実行不可状態タスクのみ処理する。
                is_executable_state = True
                for dependent_task_id in task.dependent_task_ids:
                    upstream_task = self.get_task_by_task_id(dependent_task_id)
                    if upstream_task.completed_count <= 0:
                        # 一度も実行されていない
                        is_executable_state = False
                        break
                if is_executable_state:
                    #実行可能の場合、ステータスを実行不可から未実行に変更
                    task.status = TaskStatus.STATUS_UNEXECUTED
            else:
                continue





class StatusFile(JsonFile):

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def read(self):
        content = super().read()
        return SubflowStatus(content[_IS_COMPLETED], content[_TASKS])

    def write(self, subflow_status: SubflowStatus):
        data = subflow_status.to_dict()
        super().write(data)
