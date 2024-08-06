"""サブフローの操作

このモジュールはサブフロー操作基底クラスを始め、サブフローを操作する時に
ボタンを制御したり、値が入力されているか、あるいはユニークの値になっているかなどを確認するメソッドがあります。
"""
import re
from typing import Dict, List
import traceback

import panel as pn
from dg_drawer.research_flow import PhaseStatus

from ...utils.setting import ResearchFlowStatusOperater
from ...utils.config import path_config, message as msg_config
from ...utils.string import StringManager
from ...utils.widgets import Button, MessageBox
from ...utils.error import InputWarning
from typing import Callable

class BaseSubflowForm():
    """サブフロー操作基底クラス

    Attributes:
        instance:
            abs_root(str):サブフローの絶対パス
            research_flow_status(List[PhaseStatus]):リサーチフローステータス管理情報
            reserch_flow_status_operater(ResearchFlowStatusOperater):リサーチフロー図を生成
            _err_output(MessageBox):エラーの出力
            _sub_flow_type_selector(pn.widgets.Select):サブフロー種別(フェーズ)
            _sub_flow_name_selector(pn.widgets.Select):サブフロー名称
            _sub_flow_name_form(pn.widgets.TextInput):サブフロー名称
            _data_dir_name_form(pn.widgets.TextInput):データフォルダ名
            _parent_sub_flow_type_selector(pn.widgets.Select): 親サブフロー種別(フェーズ)
            _parent_sub_flow_selector(pn.widgets.Select):親サブフロー選択
            submit_button(Button):処理開始ボタン
    """

    def __init__(self, abs_root:str, message_box: MessageBox) -> None:
        """BaseSubflowForm コンストラクタのメソッドです。

        Args:
            abs_root (str): サブフローの絶対パス
            message_box (MessageBox): メッセージを格納する。
        """
        self.abs_root = abs_root

        research_flow_status_file_path = path_config.get_research_flow_status_file_path(abs_root)
        self.reserch_flow_status_operater = ResearchFlowStatusOperater(research_flow_status_file_path)

        # リサーチフローステータス管理情報の取得
        research_flow_status = self.reserch_flow_status_operater.load_research_flow_status()
        self._err_output = message_box

        # サブフロー種別(フェーズ)オプション
        sub_flow_type_options = self.generate_sub_flow_type_options(research_flow_status)
        # サブフロー種別(フェーズ):シングルセレクト
        self._sub_flow_type_selector = pn.widgets.Select(
            name=msg_config.get('main_menu', 'sub_flow_type'),
            options=sub_flow_type_options,
            value=sub_flow_type_options[msg_config.get('form', 'selector_default')]
            )
        # サブフロー種別(フェーズ)のイベントリスナー
        self._sub_flow_type_selector.param.watch(self.callback_sub_flow_type_selector, 'value')

        # サブフロー名称オプション
        sub_flow_name_options = self.generate_sub_flow_name_options(sub_flow_type_options[msg_config.get('form', 'selector_default')], research_flow_status)
        # サブフロー名称：シングルセレクト
        self._sub_flow_name_selector = pn.widgets.Select(
            name=msg_config.get('main_menu', 'sub_flow_name_select'),
            options=sub_flow_name_options,
            value=sub_flow_name_options[msg_config.get('form', 'selector_default')]
        )
        # サブフロー名称のイベントリスナー
        self._sub_flow_name_selector.param.watch(self.callback_sub_flow_name_selector, 'value')

        # サブフロー名称：テキストフォーム
        self._sub_flow_name_form = pn.widgets.TextInput(
            name=msg_config.get('main_menu', 'sub_flow_name_input'),
            max_length=15)
        # サブフロー名称：テキストフォームのイベントリスナー
        self._sub_flow_name_form.param.watch(self.callback_menu_form, 'value')

        # データフォルダ名
        self._data_dir_name_form = pn.widgets.TextInput(
            name=msg_config.get('main_menu', 'data_dir_name'),
            max_length=50)
        # データフォルダ名：テキストフォームのイベントリスナー
        self._data_dir_name_form.param.watch(self.callback_menu_form, 'value')

        # 親サブフロー種別(フェーズ)オプション
        parent_sub_flow_type_options = self.generate_parent_sub_flow_type_options(sub_flow_type_options[msg_config.get('form', 'selector_default')], research_flow_status)
        # 親サブフロー種別(フェーズ)（必須)：シングルセレクト
        self._parent_sub_flow_type_selector = pn.widgets.Select(
            name=msg_config.get('main_menu', 'parent_sub_flow_type'),
            options=parent_sub_flow_type_options,
            value=parent_sub_flow_type_options[msg_config.get('form', 'selector_default')],
            )
        # 親サブフロー種別(フェーズ)のイベントリスナー
        self._parent_sub_flow_type_selector.param.watch(self.callback_parent_sub_flow_type_selector, 'value')

        # 親サブフロー選択オプション
        parent_sub_flow_options = self.generate_parent_sub_flow_options(parent_sub_flow_type_options[msg_config.get('form', 'selector_default')], research_flow_status)
        # 親サブフロー選択 : マルチセレクト
        self._parent_sub_flow_selector = pn.widgets.MultiSelect(
            name=msg_config.get('main_menu', 'parent_sub_flow_name'),
            options=parent_sub_flow_options
            )
        # 親サブフロー選択のイベントリスナー
        self._parent_sub_flow_selector.param.watch(self.callback_menu_form, 'value')

        # 処理開始ボタン
        self.submit_button = Button(disabled=True)
        self.submit_button.width = 500


    def set_submit_button_on_click(self, callback_function:Callable):
        """処理開始ボタンのイベントリスナー設定するメソッドです。

        Args:
            callback_function(Callable):処理開始ボタンを呼び戻す
        """
        self.submit_button.on_click(callback_function)

    def generate_sub_flow_type_options(self, research_flow_status:List[PhaseStatus]) -> dict:
        """サブフロー種別(フェーズ)を表示するメソッドです。

        Args:
            research_flow_status (List[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            dict: フェーズ表示名を返す。
        """
        # サブフロー種別(フェーズ)オプション(表示名をKey、順序値をVauleとする)
        pahse_options = {}
        pahse_options['--'] = 0
        for phase_status in research_flow_status:
            # planは選択させない
            if phase_status._seq_number == 1:
                continue
            # サブフローのあるフェーズのみ
            if len(phase_status._sub_flow_data) > 0:
                pahse_options[msg_config.get('research_flow_phase_display_name',phase_status._name)] = phase_status._seq_number
        return pahse_options

    def generate_sub_flow_name_options(self, phase_seq_number:int, research_flow_status:List[PhaseStatus]) -> dict:
        """サブフロー名を表示するメソッドです。

        Args:
            phase_seq_number (int): サブフロー種別
            research_flow_status (List[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            dict: サブフロー名の値を返す。
        """
        # サブフロー名(表示名をkey, サブフローIDをVauleとする)
        name_options = {}
        name_options['--'] = 0
        if phase_seq_number == 0:
            return name_options

        for phase_status in research_flow_status:
            if phase_status._seq_number == phase_seq_number:
                for sf in phase_status._sub_flow_data:
                    name_options[sf._name] = sf._id

        return name_options


    def generate_parent_sub_flow_type_options(self, pahase_seq_number:int, research_flow_status:List[PhaseStatus]) -> dict:
        """親サブフロー種別を表示するメソッドです。

        Args:
            pahase_seq_number (int): 親サブフロー種別
            research_flow_status (List[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            dict: 親サブフロー種別の値
        """
        # 親サブフロー種別(フェーズ)オプション(表示名をKey、順序値をVauleとする)
        pahse_options = {}
        pahse_options['--'] = 0
        if pahase_seq_number == 0:
            return pahse_options
        else:
            for phase_status in research_flow_status:
                if phase_status._seq_number < pahase_seq_number:
                    pahse_options[msg_config.get('research_flow_phase_display_name',phase_status._name)] = phase_status._seq_number
        return pahse_options


    def generate_parent_sub_flow_options(self, pahase_seq_number:int, research_flow_status:List[PhaseStatus]) -> dict:
        """親サブフロー選択オプションで選択した値を表示するメソッドです。

        Args:
            pahase_seq_number (int): 親サブフロー選択オプション
            research_flow_status (List[PhaseStatus]): リサーチフローステータス管理情報

        Returns:
            dict: 親サブフロー選択オプションで選択した値を返す。
        """
        # 親サブフロー選択オプション(表示名をKey、サブフローIDをVauleとする)
        # createとrelinkで用いる
        pahse_options = {}
        if pahase_seq_number == 0:
            return pahse_options
        else:
            for phase_status in research_flow_status:
                if phase_status._seq_number == pahase_seq_number:
                    for sf in phase_status._sub_flow_data:
                        pahse_options[sf._name] = sf._id
        return pahse_options

    def change_submit_button_init(self, name:str):
        """処理開始ボタンのメソッドです。

        Args:
            name (str): メッセージ
        """
        self.submit_button.set_looks_init(name)

    def change_submit_button_processing(self, name:str):
        """新規作成ボタンを処理中ステータスに更新するメソッドです。

        Args:
            name (str): 実行中のメッセージ
        """
        self.submit_button.set_looks_processing(name)

    def change_submit_button_success(self, name:str):
        """ボタンを成功の状態に更新するメソッドです。

        Args:
            name (str): 成功したメッセージ
        """
        self.submit_button.set_looks_success(name)

    def change_submit_button_warning(self, name:str):
        """ボタンを警告の状態に更新するメソッドです。

        Args:
            name (str): 警告メッセージ
        """
        self.submit_button.set_looks_warning(name)

    def change_submit_button_error(self, name:str):
        """ボタンをエラーの状態に更新するメソッドです。

        Args:
            name (str): エラーメッセージ
        """
        self.submit_button.set_looks_error(name)

    ############
    # callback #
    ############

    def callback_menu_form(self, event):
        """ボタンを有効化させるメソッドです。"""
        # フォームコールバックファンクション
        try:
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_sub_flow_type_selector(self, event):
        """サブフロー種別(フェーズ)のボタンが操作できるように有効化するメソッドです。

        Raises:
            Exception: サブフローのセレクタタイプなし、内部エラー
        """
        # サブフロー種別(フェーズ):シングルセレクトコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = self.reserch_flow_status_operater.load_research_flow_status()

            selected_value = self._sub_flow_type_selector.value
            if selected_value is None:
                raise Exception('Sub Flow Type Selector has None')
            # サブフロー名称：シングルセレクトの更新
            sub_flow_name_options = self.generate_sub_flow_name_options(selected_value, research_flow_status)
            self._sub_flow_name_selector.options = sub_flow_name_options
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_sub_flow_name_selector(self, event):
        """サブフロー名称のボタンが操作できるように有効化するメソッドです"""
        # サブフロー名称：シングルセレクトコールバックファンクション
        # relinkとrenameで継承するため個別処理
        try:
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    def callback_parent_sub_flow_type_selector(self, event):
        """親サブフロー種別(フェーズ)のボタンが操作できるように有効化するメソッドです

        Raises:
            Exception: サブフローのセレクタタイプなし
        """
        # 親サブフロー種別(フェーズ)のコールバックファンクション
        try:
            # リサーチフローステータス管理情報の取得
            research_flow_status = self.reserch_flow_status_operater.load_research_flow_status()

            selected_value = self._parent_sub_flow_type_selector.value
            if selected_value is None:
                raise Exception('Parent Sub Flow Type Selector has None')

            parent_sub_flow_options = self.generate_parent_sub_flow_options(selected_value, research_flow_status)
            self._parent_sub_flow_selector.options = parent_sub_flow_options
            # 新規作成ボタンのボタンの有効化チェック
            self.change_disable_submit_button()
        except Exception as e:
            self._err_output.update_error(f'## [INTERNAL ERROR] : {traceback.format_exc()}')

    ############
    # validate #
    ############

    def change_disable_submit_button(self):
        """サブフロー新規作成フォームの必須項目が選択・入力が満たしている場合、新規作成ボタンを有効化するメソッドです。"""
        # 継承した先で実装する

    def validate_sub_flow_name(self, sub_flow_name:str):
        """サブフロー名称の値が存在するかを確認しているメソッドです。

        Args:
            sub_flow_name (str): サブフロー名称

        Raises:
            InputWarning: 入力不備のエラー
        """

        if StringManager.is_empty(sub_flow_name):
            # sub_flow_nameが未入力の場合、ユーザ警告
            message = msg_config.get('main_menu','not_input_subflow_name')
            raise InputWarning(message)

    def is_unique_subflow_name(self, sub_flow_name:str, phase_seq_number:int):
        """サブフローの名称がユニークの値になっているかどうかを確認しているメソッドです。

        Args:
            sub_flow_name (str): サブフロー名称
            phase_seq_number (int): サブフロー種別

        Raises:
            InputWarning: 値がユニークの値ではない時のエラー
        """

        if not self.reserch_flow_status_operater.is_unique_subflow_name(phase_seq_number, sub_flow_name):
            # サブフロー名がユニークでない場合、ユーザ警告
            message = msg_config.get('main_menu','must_not_same_subflow_name')
            raise InputWarning(message)

    def validate_data_dir_name(self, data_dir_name:str):
        """データフォルダ名の検証をする時に問題がないか確認するメソッドです。

        Args:
            data_dir_name (str): データフォルダ名

        Raises:
            InputWarning: 入力不備によるエラー
        """

        # データフォルダ名の検証
        if StringManager.is_empty(data_dir_name):
            # data_dir_nameが未入力の場合、ユーザ警告
            message = msg_config.get('main_menu','not_input_data_dir')
            raise InputWarning(message)

        if not StringManager.is_half(data_dir_name):
            # 半角文字でない時、ユーザ警告
            message = msg_config.get('main_menu','data_dir_pattern_error')
            raise InputWarning(message)

        if re.search(r'[\\/:\*\?"<>\|]', data_dir_name):
            # data_dir_nameに禁止文字列(\/:*?"<>|)が含まれる時、ユーザ警告
            message = msg_config.get('main_menu','data_dir_pattern_error')
            raise InputWarning(message)

    def is_unique_data_dir(self, data_dir_name:str, phase_seq_number:int):
        """データフォルダ名がユニークの値になっているかを確認するメソッドです。

        Args:
            data_dir_name (str): データフォルダ名
            phase_seq_number (int): サブフロー種別

        Raises:
            InputWarning: 値がユニークの値ではない時のエラー
        """

        if not self.reserch_flow_status_operater.is_unique_data_dir(phase_seq_number, data_dir_name):
            # data_dir_nameがユニークでない場合、ユーザ警告
            message = msg_config.get('main_menu','must_not_same_data_dir')
            raise InputWarning(message)