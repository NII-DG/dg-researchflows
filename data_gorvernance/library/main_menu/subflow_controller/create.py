"""サブフローの新規作成を行うモジュールです。

このモジュールはサブフロー新規作成クラスを始め、新しいサブフローのデータを用意したり、データの検証を行うメソッドなどがあります。
"""
import os
import shutil
import traceback


from dg_drawer.research_flow import PhaseStatus
import panel as pn

from library.utils import file
from library.utils.config import path_config, message as msg_config
from library.utils.error import InputWarning
from library.utils.nb_file import NbFile
from library.utils.string import StringManager
from library.utils.widgets import MessageBox
from .base import BaseSubflowForm



class CreateSubflowForm(BaseSubflowForm):
    """サブフロー新規作成クラスです。

    Attributes:
        instance:
            abs_root (str): リサーチフローのルートディレクトリ
            submit_button(Button):ボタンの設定
            reserch_flow_status_operater(ResearchFlowStatusOperater):リサーチフロー図を生成
            _sub_flow_type_selector(pn.widgets.Select):サブフロー種別(フェーズ)
            _err_output(MessageBox):エラーの出力
            _parent_sub_flow_type_selector(pn.widgets.Select): 親サブフロー種別(フェーズ)
            _parent_sub_flow_selector(pn.widgets.Select):親サブフロー選択
            _sub_flow_name_form(TextInput):サブフロー名のフォーム
            _data_dir_name_form(TextInput):データディレクトリ名のフォーム
    """

    def __init__(self, abs_root: str, message_box: MessageBox) -> None:
        """CreateSubflowForm コンストラクタのメソッドです。

        Args:
            abs_root (str): リサーチフローのルートディレクトリ
            message_box (MessageBox): メッセージを格納する。
        """
        super().__init__(abs_root, message_box)
        # 処理開始ボタン
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))

    def generate_sub_flow_type_options(self, research_flow_status: list[PhaseStatus]) -> dict[str, int]:
        """サブフロー種別(フェーズ)を表示するメソッドです。

        Args:
            research_flow_status (list[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            dict: フェーズ表示名を返す。
        """
    # サブフロー種別(フェーズ)オプション(表示名をKey、順序値をVauleとする)
        pahse_options = {}
        pahse_options['--'] = 0
        for phase_status in research_flow_status:
            if phase_status._seq_number == 1:
                continue
            else:
                # plan以外の全てのフェーズ
                pahse_options[msg_config.get('research_flow_phase_display_name', phase_status._name)] = phase_status._seq_number
        return pahse_options

    def change_submit_button_init(self, name: str):
        """ボタンの状態を初期化するメソッドです。

        Args:
            name (str): メッセージ
        """
        self.submit_button.set_looks_init(name)
        self.submit_button.icon = 'plus'

    # overwrite
    def callback_sub_flow_type_selector(self, event):
        """サブフロー種別(フェーズ)のボタンが操作できるように有効化するメソッドです。"""
        # サブフロー種別(フェーズ):シングルセレクトコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = self.reserch_flow_status_operater.load_research_flow_status()

            selected_value = self._sub_flow_type_selector.value
            if selected_value is None:
                raise Exception('Sub Flow Type Selector has None')
            # 親サブフロー種別(フェーズ)（必須)：シングルセレクトの更新
            parent_sub_flow_type_options = self.generate_parent_sub_flow_type_options(selected_value, research_flow_status)
            self._parent_sub_flow_type_selector.options = parent_sub_flow_type_options
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    # overwrite
    def change_disable_submit_button(self):
        """サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化するメソッドです。"""
        # サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化する
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))

        value = self._sub_flow_type_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif int(value) == 0:
            self.submit_button.disabled = True
            return

        value = self._sub_flow_name_form.value_input
        if value is None:
            self.submit_button.disabled = True
            return
        elif len(value) < 1:
            self.submit_button.disabled = True
            return

        value = self._data_dir_name_form.value_input
        if value is None:
            self.submit_button.disabled = True
            return
        elif len(value) < 1:
            self.submit_button.disabled = True
            return

        value = self._parent_sub_flow_type_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif int(value) == 0:
            self.submit_button.disabled = True
            return

        value = self._parent_sub_flow_selector.value
        if value is None:
            self.submit_button.disabled = True
            return
        elif len(value) < 1:
            self.submit_button.disabled = True
            return

        self.submit_button.disabled = False

    def define_input_form(self) -> pn.Column:
        """サブフロー新規作成フォームのメソッドです。

        Returns:
            pn.Column:サブフロー新規作成フォームに必要な値を返す。
        """
        return pn.Column(
            f'### {msg_config.get("main_menu", "create_sub_flow_title")}',
            self._sub_flow_type_selector,
            self._sub_flow_name_form,
            self._data_dir_name_form,
            self._parent_sub_flow_type_selector,
            self._parent_sub_flow_selector,
            self.submit_button
        )

    def main(self):
        """サブフロー新規作成処理のメソッドです。

        入力情報を取得し、その値を検証してリサーチフローステータス管理JSONの更新、新規サブフローデータの用意を行う。

        Raises:
            InputWarning:入力値の不備によるエラー
            Exception:データ取得、更新が失敗したエラー
        """

        # 新規作成ボタンを処理中ステータスに更新する
        self.change_submit_button_processing(msg_config.get('main_menu', 'creating_sub_flow'))

        # 入力情報を取得する。
        phase_seq_number = self._sub_flow_type_selector.value
        sub_flow_name = self._sub_flow_name_form.value_input
        data_dir_name = self._data_dir_name_form.value_input
        parent_sub_flow_ids = self._parent_sub_flow_selector.value

        # 入力値の検証
        try:
            sub_flow_name = StringManager.strip(sub_flow_name)
            self.validate_sub_flow_name(sub_flow_name)
            self.is_unique_subflow_name(sub_flow_name, phase_seq_number)

            data_dir_name = StringManager.strip(data_dir_name)
            self.validate_data_dir_name(data_dir_name)
            self.is_unique_data_dir(data_dir_name, phase_seq_number)
        except InputWarning as e:
            self.change_submit_button_warning(str(e))
            raise

        # リサーチフローステータス管理JSONの更新
        try:
            phase_name, new_sub_flow_id = self.reserch_flow_status_operater.create_sub_flow(
                phase_seq_number, sub_flow_name, data_dir_name, parent_sub_flow_ids
            )
        except Exception:
            self.change_submit_button_error(msg_config.get('main_menu', 'error_create_sub_flow'))
            raise

        # /data/<phase_name>/<data_dir_name>の作成
        data_dir_path = ""
        try:
            data_dir_path = self.create_data_dir(phase_name, data_dir_name)
        except Exception as e:
            # ディレクトリ名が存在した場合
            # リサーチフローステータス管理JSONをロールバック
            self.reserch_flow_status_operater.del_sub_flow_data_by_sub_flow_id(new_sub_flow_id)
            # ユーザーに再入力を促す
            message = msg_config.get('main_menu', 'data_directory_exist')
            self.change_submit_button_warning(message)
            raise InputWarning(message) from e

        # 新規サブフローデータの用意
        try:
            self.prepare_new_subflow_data(phase_name, new_sub_flow_id, sub_flow_name)
        except Exception:
            # 失敗した場合に/data/<phase_name>/<data_dir_name>の削除
            os.remove(data_dir_path)
            # 失敗した場合は、リサーチフローステータス管理JSONをロールバック
            self.reserch_flow_status_operater.del_sub_flow_data_by_sub_flow_id(new_sub_flow_id)
            # 新規作成ボタンを作成失敗ステータスに更新する
            self.change_submit_button_error(msg_config.get('main_menu', 'error_create_sub_flow'))
            raise

        # フォームの初期化
        self._sub_flow_type_selector.value = 0
        self._sub_flow_name_form.value = ''
        self._sub_flow_name_form.value_input = ''
        self._data_dir_name_form.value = ''
        self._data_dir_name_form.value_input = ''
        self.change_submit_button_init(msg_config.get('main_menu', 'create_sub_flow'))

    def create_data_dir(self, phase_name: str, data_dir_name: str) -> str:
        """データディレクトリを作成するメソッドです。

        Args:
            phase_name (str): フェーズ名
            data_dir_name (str): データディレクトリ名

        Raises:
            Exception: 既にファイルが存在しているエラー

        Returns:
            str: データディレクトリを作成するパスの値を返す。
        """
        path = path_config.get_task_data_dir(self.abs_root, phase_name, data_dir_name)
        if os.path.exists(path):
            raise Exception(f'{path} is already exist.')
        os.makedirs(path)
        return path

    def prepare_new_subflow_data(self, phase_name: str, new_sub_flow_id: str, sub_flow_name: str):
        """新しいサブフローのデータを用意するメソッドです。

        Args:
            phase_name (str): フェーズ名
            new_sub_flow_id (str): 新しいサブフローのID
            sub_flow_name (str): サブフロー名
        """

        # 新規サブフローデータの用意
        # data_gorvernance\researchflowを取得
        dg_researchflow_path = os.path.join(self.abs_root, path_config.DG_RESEARCHFLOW_FOLDER)
        # data_gorvernance\base\subflowを取得する
        dg_base_subflow_path = os.path.join(self.abs_root, path_config.DG_SUB_FLOW_BASE_DATA_FOLDER)

        # コピー先フォルダパス
        dect_dir_path = os.path.join(dg_researchflow_path, phase_name, new_sub_flow_id)

        # コピー先フォルダの作成
        os.makedirs(dect_dir_path)  # 既に存在している場合はエラーになる

        # 対象コピーファイルorディレクトリリスト
        copy_files = path_config.get_prepare_file_name_list_for_subflow()

        try:
            for copy_file_name in copy_files:
                # コピー元ファイルパス
                src_path = os.path.join(dg_base_subflow_path, phase_name, copy_file_name)
                dect_path = os.path.join(dg_researchflow_path, phase_name, new_sub_flow_id, copy_file_name)
                # コピーする。
                if os.path.isfile(src_path):
                    shutil.copyfile(src_path, dect_path)
                if os.path.isdir(src_path):
                    file.copy_dir(src_path, dect_path, overwrite=True)
                # menu.ipynbファイルの場合は、menu.ipynbのヘッダーにサブフロー名を埋め込む
                if copy_file_name == path_config.MENU_NOTEBOOK:
                    nb_file = NbFile(dect_path)
                    nb_file.embed_subflow_name_on_header(sub_flow_name)
        except Exception:
            # 失敗した場合は、コピー先フォルダごと削除する（ロールバック）
            shutil.rmtree(dect_dir_path)
            raise
