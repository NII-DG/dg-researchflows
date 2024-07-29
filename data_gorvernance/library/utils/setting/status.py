"""サブフローステータス管理JSON(status.json)マネージャー"""
from library.utils.file import JsonFile


_IS_COMPLETED = 'is_completed'
_TASKS = 'tasks'


class SubflowTask:
    """サブフローの各タスクのステータスを管理する"""

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

    def __init__(self, id: str, name: str, is_multiple: bool, is_required: bool, completed_count: int,
                 dependent_task_ids: list[str], status: str, execution_environments: list[str], disabled: bool) -> None:
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
        if id not in self._execution_environments:
            self._execution_environments.append(id)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def is_multiple(self):
        return self._is_multiple

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
    """サブフローステータス管理JSON(status.json)の各項目を管理する"""

    def __init__(self, is_completed: bool, tasks: list[dict]) -> None:
        self._is_completed = is_completed
        self._tasks = [SubflowTask(**task) for task in tasks]

    @property
    def is_completed(self):
        return self._is_completed

    @property
    def tasks(self):
        return self._tasks

    @is_completed.setter
    def is_completed(self, is_completed: bool):
        self._is_completed = is_completed

    def to_dict(self):
        return {
            _IS_COMPLETED : self.is_completed,
            _TASKS: [
                con.to_dict() for con in self.tasks
            ]
        }

    def get_task_by_task_id(self, id:str)->SubflowTask:
        for task in self._tasks:
            if task.id == id:
                return task
        raise Exception(f'Not Found task status by {id}')

    def doing_task_by_task_name(self, task_name:str, environment_id:str):
        for task in self._tasks:
            if task.name == task_name:
                ## status を実行中ステータスへ更新
                task.status = SubflowTask.STATUS_DOING
                task.add_execution_environments(environment_id)

    def completed_task_by_task_name(self, task_name:str, environment_id:str):
        # 対象タスクのステータスを完了に更新する。
        for task in self._tasks:
            if task.name == task_name:
                ## completed_countに１プラス
                task.increme_completed_count()
                ## ステータスへ更新
                if len(task.execution_environments) == 1:
                    task.status = SubflowTask.STATUS_DONE
                else:
                    continue
                ## 実行環境IDをリストから削除する。
                task._execution_environments.remove(environment_id)

        # 上記の更新を受け、下流の実行可能状態を更新する。
        for task in self._tasks:
            if len(task.dependent_task_ids) > 0 and task.status == SubflowTask.STATUS_UNFEASIBLE:
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
                    task.status = SubflowTask.STATUS_UNEXECUTED
            else:
                continue

        # 上記の更新を受け、必須タスクが一度でも実行されていれば、is_completedを真に更新
        is_completed_ok = True
        for task in self._tasks:
            if task.is_required and task.completed_count < 1:
                # 必須タスクで、一度も実行されていない場合
                is_completed_ok = False
        # 判定ないようで更新する。
        self._is_completed = is_completed_ok


class SubflowStatusFile(JsonFile):
    """サブフローステータス管理JSON(status.json)のファイル操作"""

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def read(self):
        content = super().read()
        return SubflowStatus(content[_IS_COMPLETED], content[_TASKS])

    def write(self, subflow_status: SubflowStatus):
        data = subflow_status.to_dict()
        super().write(data)
