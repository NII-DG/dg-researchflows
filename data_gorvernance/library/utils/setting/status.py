"""サブフローステータスに関連する処理が記載されたモジュールです。"""
from ..file import JsonFile

_IS_COMPLETED = 'is_completed'
_TASKS = 'tasks'


class SubflowTask:
    """サブフロータスクの情報を管理するメソッドを記載したクラスです。

    Attributes:
        class:
            __ID(str):タスクの機能IDのキー名
            __NAME(str):タスクのファイル名のキー名
            __IS_MULTIPLE(str):タスクが複数回実行されるかの判定に用いるフラグのキー名。複数回実行されるものであればtrue、1回しか実行されないものであればfalse
            __IS_REQURED(str) :必須タスクかの判定に用いるフラグのキー名。必須であればtrue、そうでなければfalse
            __COMPLETED_COUNT(str):タスクの完了回数のキー名
            __DEPENDENT_TASK_IDS(str):依存するタスクの機能IDのキー名
            __STATUS(str):実行状況のキー名
            __EXECUTION_ENVIRONMENTS(str):実行中の実行環境IDのリストのキー名
            __DISABLED(str):使用不可の状態とするためのフラグのキー名

            STATUS_UNFEASIBLE(str):実行状況（実行不可能）のキー名
            STATUS_UNEXECUTED(str):実行状況（未実行）のキー名
            STATUS_DOING(str):実行状況（実行中）のキー名
            STATUS_DONE(str):実行状況（実行完了）のキー名
            allowed_statuses(str):許可されたステータスのキー名

        instance:
            _id (str):タスクの機能ID
            _name (str): タスクのファイル名
            _is_multiple (bool):タスクが複数回実行されるかの判定に用いるフラグ。複数回実行されるものであればtrue、1回しか実行されないものであればfalse
            _is_required (bool): 必須タスクかの判定に用いるフラグ。必須であればtrue、そうでなければfalse
            _completed_count (int):タスクの完了回数
            _dependent_task_ids (list[str]):依存するタスクの機能ID
            _status (str):実行状況
            _execution_environments (list[str]): 実行中の実行環境IDのリスト
            _disabled (bool):使用不可の状態とするためのフラグ

    """
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
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        Args:
            id (str):タスクの機能ID
            name (str): タスクのファイル名
            is_multiple (bool):タスクが複数回実行されるかの判定に用いるフラグ。複数回実行されるものであればtrue、1回しか実行されないものであればfalse
            is_required (bool): 必須タスクかの判定に用いるフラグ。必須であればtrue、そうでなければfalse
            completed_count (int):タスクの完了回数
            dependent_task_ids (list[str]):依存するタスクの機能ID
            status (str):実行状況
            execution_environments (list[str]): 実行中の実行環境IDのリスト
            disabled (bool):使用不可の状態とするためのフラグ

        """
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
        """ステータスの設定を行うメソッドです。

        Args:
            status (str):ステータス情報

        Raises:
            ValueError:許可されたステータスに含まれていない

        """
        if status in self.allowed_statuses:
            self._status = status
        else:
            raise ValueError

    def add_execution_environments(self, id:str):
        """実行環境のリストへの追加を行うメソッドです。

        Args:
            id (str): タスクの機能ID

        """
        if id not in self._execution_environments:
            self._execution_environments.append(id)

    @property
    def id(self)->str:
        """タスクの機能IDを取得するためのゲッターです。

        Returns:
            str: タスクの機能ID

        """
        return self._id

    @property
    def name(self)->str:
        """タスクのファイル名を取得するためのゲッターです。

        Returns:
            str: タスクのファイル名

        """
        return self._name

    @property
    def is_multiple(self)->bool:
        """タスクが複数回実行されるかの判定に用いるフラグを取得するためのゲッターです。

        Returns:
            bool: タスクが複数回実行されるかの判定に用いるフラグ

        """
        return self._is_multiple

    @property
    def is_required(self)->bool:
        """必須タスクかの判定に用いるフラグを取得するためのゲッターです。

        Returns:
            bool: 必須タスクかの判定に用いるフラグ

        """
        return self._is_required

    @property
    def completed_count(self)->int:
        """タスクの完了回数を取得するためのゲッターです。

        Returns:
            int:タスクの完了回数

        """
        return self._completed_count

    def increme_completed_count(self):
        """_completed_countの値を1増加させるメソッドです。 """
        self._completed_count += 1

    @property
    def dependent_task_ids(self)->list[str]:
        """依存するタスクの機能IDを取得するためのゲッターです。

        Returns:
            list[str]:依存するタスクの機能ID

        """
        return self._dependent_task_ids

    @property
    def status(self)->str:
        """実行状況を取得するためのゲッターです。

        Returns:
            str:実行状況

        """
        return self._status

    @status.setter
    def status(self, status: str):
        """実行状況を設定するためのセッターです。

        Args:
            status (str):_statusにセットする値

        """
        self._set_status(status)

    @property
    def disable(self)->bool:
        """使用不可の状態とするためのフラグを取得するためのゲッターです。

        Returns:
            bool:使用不可の状態とするためのフラグ
        """
        return self._disable

    @disable.setter
    def disable(self, is_disable:bool):
        """使用不可の状態とするためのフラグを設定するためのセッターです。

        Args:
            is_disable (bool):_disableにセットする値

        """
        self._disable = is_disable

    @property
    def execution_environments(self)->list[str]:
        """実行中の実行環境IDのリストを取得するためのゲッターです。

        Returns:
            list[str]:実行中の実行環境IDのリスト

        """
        return self._execution_environments

    def to_dict(self)->dict[str, any]:
        """インスタンスが保持しているデータを辞書型のデータに変換するメソッドです。

        Returns:
            dict[str, Any]:サブフロータスクの辞書型データ

        """
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
    """サブフローステータス管理JSON(status.json)の各項目を管理するメソッドを記載したクラスです。

    Attributes:
        instance:
            _is_completed(bool):サブフローが完了しているかの判定に用いるフラグ。初期値はfalseで必須タスクが全て完了した段階でtrueに更新
            _tasks(list[SubflowTask]):サブフローの各タスクのステータスのリスト

    """

    def __init__(self, is_completed: bool, tasks: list[dict]) -> None:
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        Args:
            is_completed (bool):サブフローが完了しているかの判定に用いるフラグ
            tasks (list[dict]):サブフローの各タスクのステータスのリスト

        """
        self._is_completed = is_completed
        self._tasks = [SubflowTask(**task) for task in tasks]

    @property
    def is_completed(self)->bool:
        """サブフローが完了しているかの判定に用いるフラグを取得するためのゲッターです。

        Returns:
            bool:サブフローが完了しているかの判定に用いるフラグ

        """
        return self._is_completed

    @property
    def tasks(self)->list[SubflowTask]:
        """:サブフローの各タスクのステータスのリストを取得するためのゲッターです。

        Returns:
           list[SubflowTask]:サブフローの各タスクのステータスのリスト

        """
        return self._tasks

    @is_completed.setter
    def is_completed(self, is_completed: bool):
        """サブフローが完了しているかの判定に用いるフラグの値を設定するためのセッターです。

        Args:
            is_completed (bool):_is_completedにセットする値

        """
        self._is_completed = is_completed

    def to_dict(self)->dict[str, any]:
        """"インスタンスが保持しているデータを辞書型のデータに変換するメソッドです。

        Returns:
            dict[str, Any]:サブフロータスクを含む辞書型データ

        """
        return {
            _IS_COMPLETED : self.is_completed,
            _TASKS: [
                con.to_dict() for con in self.tasks
            ]
        }

    def get_task_by_task_id(self, id:str)->SubflowTask:
        """指定したサブフロータスクを取得するメソッドです。

        Args:
            id (str): 対象となるサブフロータスクのid

        Returns:
            SubflowTask:サブフロータスク

        Raises:
            Exception:idの一致するタスクが存在しない

        """
        for task in self._tasks:
            if task.id == id:
                return task
        raise Exception(f'Not Found task status by {id}')

    def doing_task_by_task_name(self, task_name:str, environment_id:str):
        """指定されたタスクのステータスを実行中にするメソッドです。

        Args:
            task_name (str): 対象となるタスクの名前
            environment_id (str): 実行環境のリストに追加するID

        """
        for task in self._tasks:
            if task.name == task_name:
                ## status を実行中ステータスへ更新
                task.status = SubflowTask.STATUS_DOING
                task.add_execution_environments(environment_id)

    def completed_task_by_task_name(self, task_name:str, environment_id:str):
        """指定したタスクの実行状況を完了に更新するメソッドです。

        Args:
            task_name (str):対象のタスク名
            environment_id (str): 実行環境リストのID

        """

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
    """サブフローステータス管理JSON(status.json)のファイル操作を行うためのクラスです。"""

    def __init__(self, file_path: str):
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        Args:
            file_path (str): 対象ファイルのパス

        """
        super().__init__(file_path)

    def read(self)->SubflowStatus:
        """ジェイソンファイルの読み込みを行うメソッドです。

        Returns:
            SubflowStatus:作成したSubflowStatusクラスのインスタンス

        """
        content = super().read()
        return SubflowStatus(content[_IS_COMPLETED], content[_TASKS])

    def write(self, subflow_status: SubflowStatus):
        """ジェイソンファイルへの書き込みを行うメソッドです。

        Args:
            subflow_status (SubflowStatus): SubflowStatus型のデータ

        """
        data = subflow_status.to_dict()
        super().write(data)