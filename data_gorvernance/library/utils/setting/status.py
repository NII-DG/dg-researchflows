"""サブフローステータス管理JSON(status.json)マネージャー
サブフローステータスに対する処理が記載されています。
"""
from ..file import JsonFile

_IS_COMPLETED = 'is_completed'
_TASKS = 'tasks'


class SubflowTask:
    """サブフローの各タスクを管理するクラスです。

    タスクの情報の保持や変換などデータの管理を行うメソッドを記載しています。

    Attributes:
        class:
            __ID(str):不明
            __NAME(str):不明
            __IS_MULTIPLE(str):不明
            __IS_REQURED(str) :不明
            __COMPLETED_COUNT(str):不明
            __DEPENDENT_TASK_IDS(str):実行依存先ID
            __STATUS(str):実行状況
            __EXECUTION_ENVIRONMENTS(str):実行環境リスト
            __DISABLED(str):不明

            STATUS_UNFEASIBLE(str):実行状況（実行不可能）
            STATUS_UNEXECUTED(str):実行状況（未実行）
            STATUS_DOING(str):実行状況（実行中）
            STATUS_DONE(str):実行状況（実行完了）
            allowed_statuses(str):許可されたステータス

        instance:
            id (str):不明
            name (str): 不明
            is_multiple (bool):不明
            is_required (bool): _不明
            completed_count (int):不明
            dependent_task_ids (list[str]):実行依存先ID
            status (str):実行状況
            execution_environments (list[str]): 実行環境リスト
            disabled (bool):不明

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

        引数として受け取った値を自身のインスタンスに保存します。

        Args:
            id (str):不明
            name (str): 不明
            is_multiple (bool):不明
            is_required (bool): _不明
            completed_count (int):不明
            dependent_task_ids (list[str]):実行依存先ID
            status (str):実行状況
            execution_environments (list[str]): 実行環境リスト
            disabled (bool):不明

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

        引数として受け取ったステータスがallowed_statusesに含まれている場合のみ、自身のインスタンスに保存します。

        Args:
            status (str):ステータス情報

        Raises:
            ValueError:強化されたステータスに含まれていない

        """
        if status in self.allowed_statuses:
            self._status = status
        else:
            raise ValueError

    def add_execution_environments(self, id:str):
        """実行環境のリストへの追加を行うメソッドです。

        引数として受け取ったidが実行環境のリストに含まれていなかった場合、リストへの追加を行います。

        Args:
            id (str): ID

        """
        if id not in self._execution_environments:
            self._execution_environments.append(id)

    @property
    def id(self):
        """_idを取得するメソッドです。

        @propertyデコレータを使用して、idという名前のゲッターを定義しています。

        Returns:
            str: ID

        """
        return self._id

    @property
    def name(self):
        """_nameを取得するメソッドです。

        @propertyデコレータを使用して、nameという名前のゲッターを定義しています。

        Returns:
            str: 名前

        """
        return self._name

    @property
    def is_multiple(self):
        """_is_multipleを取得するメソッドです。

        @propertyデコレータを使用して、is_multipleという名前のゲッターを定義しています。

        Returns:
            bool: 不明

        """
        return self._is_multiple

    @property
    def is_required(self):
        """_is_requiredを取得するメソッドです。

        @propertyデコレータを使用して、is_requiredという名前のゲッターを定義しています。

        Returns:
            bool: 不明

        """
        return self._is_required

    @property
    def completed_count(self):
        """_completed_countを取得するメソッドです。

        @propertyデコレータを使用して、completed_countという名前のゲッターを定義しています。

        Returns:
            bool: 不明

        """
        return self._completed_count

    def increme_completed_count(self):
        """_completed_countを増加させるメソッドです。

        呼び出されることで_completed_countの値を1増やします。

        """
        self._completed_count += 1

    @property
    def dependent_task_ids(self):
        """_dependent_task_idsを取得するメソッドです。

        @propertyデコレータを使用して、dependent_task_idsという名前のゲッターを定義しています。

        Returns:
            list[str]: 不明

        """
        return self._dependent_task_ids

    @property
    def status(self):
        """_statusを取得するメソッドです。

        @propertyデコレータを使用して、statusという名前のゲッターを定義しています。

        Returns:
            str: 不明

        """
        return self._status

    @status.setter
    def status(self, status: str):
        """_statusに値をセットするためのメソッドです。

         @status.setterデコレータを使用してstatusという名前のセッターを定義しています。

        Args:
            status (str):_statusにセットする値

        """
        self._set_status(status)

    @property
    def disable(self):
        """_disableを取得するメソッドです。

        @propertyデコレータを使用して、disableという名前のゲッターを定義しています。

        Returns:
            bool: 不明

        """
        return self._disable

    @disable.setter
    def disable(self, is_disable:bool):
        """_disableに値をセットするためのメソッドです。

         @disable.setterデコレータを使用してdisableという名前のセッターを定義しています。

        Args:
            is_disable (bool):_disableにセットする値

        """
        self._disable = is_disable

    @property
    def execution_environments(self):
        """_execution_environmentsを取得するメソッドです。

        @propertyデコレータを使用して、execution_environmentsという名前のゲッターを定義しています。

        Returns:
            list[str]: 不明

        """
        return self._execution_environments

    def to_dict(self):
        """辞書型のデータを作成するメソッドです。

        インスタンスが保持しているデータをクラス変数をキーとした辞書型のデータにして返します。

        Returns:
            _dict[str, Any]:サブフロータスクの辞書型データ

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
    """サブフローステータス管理JSON(status.json)の各項目を管理する

    サブフローステータス管理JSON(status.json)の各項目に対する操作を行うメソッドを記載したクラスです。
    """

    def __init__(self, is_completed: bool, tasks: list[dict]) -> None:
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        引数として受け取ったデータを変換し、自身のインスタンスに保存しています。

        Args:
            is_completed (bool): 不明
            tasks (list[dict]): 不明

        """
        self._is_completed = is_completed
        self._tasks = [SubflowTask(**task) for task in tasks]

    @property
    def is_completed(self):
        """_is_completedを取得するメソッドです。

        @propertyデコレータを使用して、is_completedという名前のゲッターを定義しています。

        Returns:
            bool: 不明

        """
        return self._is_completed

    @property
    def tasks(self):
        """_tasksを取得するメソッドです。

        @propertyデコレータを使用して、tasksという名前のゲッターを定義しています。

        Returns:
           list[SubflowTask]: 不明

        """
        return self._tasks

    @is_completed.setter
    def is_completed(self, is_completed: bool):
        """_is_completedに値をセットするためのメソッドです。

         @is_completed.setterデコレータを使用してis_completedという名前のセッターを定義しています。

        Args:
            is_completed (bool):_is_completedにセットする値

        """
        self._is_completed = is_completed

    def to_dict(self):
        """"辞書型のデータを作成するメソッドです。

        インスタンスが保持しているデータをクラス変数をキーとした辞書型のデータに変換して返します。


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

        引数として受け取ったidと一致するidを有するサブフロータスクを取得します。

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

        引数で指定されたタスクのステータスをdoingに更新し、execution_environmentsのリストに追加します。

        Args:
            task_name (str): 対象となるタスクの名前
            environment_id (str): 実行環境のリストに追加するid

        """
        for task in self._tasks:
            if task.name == task_name:
                ## status を実行中ステータスへ更新
                task.status = SubflowTask.STATUS_DOING
                task.add_execution_environments(environment_id)

    def completed_task_by_task_name(self, task_name:str, environment_id:str):
        """指定したタスクの実行状況を完了に更新するメソッドです。

        引数で指定されたタスクのステータスを完了に更新し、それに付随する処理を実行します。

        Args:
            task_name (str):対象のタスク名
            environment_id (str): 実行環境リストのid

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
    """サブフローステータス管理JSON(status.json)のファイル操作を行うクラスです。

    親クラスのメソッドを呼び出し、ジェイソンファイルへの操作を行うメソッドを記載しています。

    """

    def __init__(self, file_path: str):
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        引数として受け取ったfile_pathを用いて親クラスのコンストラクタを呼び出します。

        Args:
            file_path (str): 対象ファイルのパス

        """
        super().__init__(file_path)

    def read(self):
        """ジェイソンファイルの読み出しを行うメソッドです。

        親クラスの.read()を呼び出し、取得したファイルをSubflowStatusクラスのインスタンスに変換します。

        Returns:
            SubflowStatus:作成したSubflowStatusクラスのインスタンス

        """
        content = super().read()
        return SubflowStatus(content[_IS_COMPLETED], content[_TASKS])

    def write(self, subflow_status: SubflowStatus):
        """ジェイソンファイルへの書き込みを行うメソッドです。

        引数として受け取ったSubflowStatus型のデータを辞書型に変換し、親クラスのメソッドを用いてジェイソンファイルへの書き込みを行います。

        Args:
            subflow_status (SubflowStatus): SubflowStatus型のデータ

        """
        data = subflow_status.to_dict()
        super().write(data)
