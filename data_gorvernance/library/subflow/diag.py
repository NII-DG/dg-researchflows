""" ダイアグラムの管理を行うモジュールです。"""

import os
from graphviz import Digraph

from library.utils import file
from library.utils.setting.status import SubflowTask


#現在のスクリプトのディレクトリパス
script_dir = os.path.dirname(os.path.abspath(__file__))

class DiagManager:
    """ダイアグラムの管理を行うクラスです。

    Attributes:
        class:
            node_attr(dict): 全てのノードで共通となる設定
            left_group_style(str): 左側に表示する実行順の決まっているグループのスタイル
            left_group_color(str): 左側に表示する実行順の決まっているグループの色
            invisible_status(str): スタイルやエッジなどの要素を表示しない場合のステータス
            rank_sep(str): ランクの異なるノード間の距離の設定
            multiple_icon(str): 複数回実行可能なタスクに付与するアイコン
            unfeasible_font_color(str): 実行不可能なタスクのフォントの色
            unfeasible_fill_color(str): 実行不可能なタスクの塗りつぶしの色

        instance:
            dot(Digraph): ダイアグラムの情報を保持するオブジェクト

    """
    #全てのノードで共通となる設定
    node_attr = {
        'shape': 'box',
        'width': '2.5',
        'height': '0.6',
        'fixedsize': 'true',
        'style': 'filled',
        'fillcolor': 'white',
        'color': 'black',
        'fontname': 'sans-serif',
        'fontcolor': '#FF8C00',
        'fontsize': '9'
    }
    left_group_style = 'filled'
    left_group_color = '#FFE6CC'
    invisible_status = 'invis'
    rank_sep = '0.4'
    multiple_icon = '　\U0001F501'
    unfeasible_font_color = 'black'
    unfeasible_fill_color = '#e6e5e3'

    def __init__(self):
        """ クラスのインスタンスの初期化処理を実行するメソッドです。"""
        self.dot = Digraph(format='svg', node_attr= self.node_attr)
        self.dot.attr(ranksep=self.rank_sep)

    def update(self, current_dir: str, tasks: list[SubflowTask], order: dict, node_config: dict) -> None:
        """ タスクの状態に基づいてダイアグラムを更新するメソッドです。

        Args:
            current_dir(str): サブフローメニューの親ディレクトリ
            tasks(list[SubflowTask]): サブフローのタスクの設定値
            order(dict): サブフローのタスクの順序情報
            node_config(dict): ダイアグラムのノード設定用の辞書

        """
        #実行順が決まっているタスクの更新
        order_sequence = order.get("sequence")
        active_tasks = order_sequence
        for task in tasks:
            if task.id in order_sequence:
                if task.active:
                    self._adjust_by_status(current_dir, node_config, task)
                else:
                    active_tasks.remove(task.id)
        if active_tasks:
            self._create_left_subgraph(active_tasks, node_config)

        #いつ実行しても構わないタスクの更新
        order_whenever = order.get("whenever")
        active_tasks = order_whenever
        for task in tasks:
            if task.id in order_whenever:
                if task.active:
                    self._adjust_by_status(current_dir, node_config, task)
                else:
                    active_tasks.remove(task.id)
        if active_tasks:
            self._create_right_subgraph(active_tasks, node_config)

    def _adjust_by_status(self, current_dir: str, node_config: dict, task: SubflowTask):
        """ フロー図の見た目をタスクの状態によって変えるメソッドです。

        Args:
            current_dir(str): サブフローメニューの親ディレクトリ
            node_config(dict): ダイアグラムのノード設定用の辞書
            task (SubflowTask): 調整するタスクを設定します。

        """
        task_parameter = {}

        icon_dir = "../data/icon"
        icon_dir = os.path.abspath(os.path.join(script_dir, icon_dir))
        icon_dir = file.relative_path(icon_dir, current_dir)

        if task.is_multiple:
            node_config[task.id]["text"] += self.multiple_icon

        if task.status == task.STATUS_UNFEASIBLE:
            task_parameter["fontcolor"] = self.unfeasible_font_color
            task_parameter["fillcolor"] = self.unfeasible_fill_color
            task_parameter["image"] = os.path.join(icon_dir, "lock.png")
            node_config[task.id]["task_parameter"] = task_parameter
            return

        if task.status == task.STATUS_DONE:
            task_parameter["image"] = os.path.join(icon_dir, "check_mark.png")
            node_config[task.id]['path'] += "?init_nb=true"

        elif task.status == task.STATUS_DOING:
            task_parameter["image"] = os.path.join(icon_dir, "loading.png")

        #実行不可以外のタスクにURLを埋め込む
        link = file.relative_path(
            str(node_config[task.id]['path']), current_dir).replace("../", "./../")
        task_parameter["URL"] = link
        node_config[task.id]["task_parameter"] = task_parameter

    def _add_node(self, node_group, node_id: str, node_label: str, **kwargs):
        """新たにノードを追加するメソッドです。

        Args:
            node_group(subgraph): ノードを追加するサブグラフのオブジェクト
            node_id (str): ノードIDを設定します。
            node_label (str): ノードの名前を設定します。
            **kwargs(dict): ノードに設定する情報

        """
        node_group.node(node_id, label=node_label, **kwargs)

        #ノードが複数ある場合、エッジを作成する。
        node_list = node_group.body
        node_lines = [line for line in node_list if 'label' in line]
        if len(node_lines) >= 2:
            prev_node_id = node_lines[-2].split(' ')[0].strip()  # ひとつ前のノードID
            node_group.edge(prev_node_id, node_id)

    def _create_left_subgraph(self, tasks: list, node_config: dict):
        """左側に配置される実行順の決まっているタスクのノード群を作成するメソッドです。

        args:
            tasks(list): 追加するノードの一覧
            node_config(dict): ノードの設定に用いる情報

        """
        with self.dot.subgraph(name='cluster_left') as left_group:
            left_group.attr(style=self.left_group_style, color=self.left_group_color)
            for task in tasks:
                kwargs = node_config[task]["task_parameter"]
                self._add_node(left_group, task, node_config[task]['text'], **kwargs)

    def _create_right_subgraph(self, tasks: list, node_config: dict):
        """右側に配置されるいつ実行しても構わないタスクのノード群を作成するメソッドです。

        args:
            tasks(list): 追加するノードの一覧
            node_config(dict): ノードの設定に用いる情報

        """
        with self.dot.subgraph(name='cluster_right') as right_group:
            right_group.attr(style=self.invisible_status)
            right_group.edge_attr.update(style=self.invisible_status)
            for task in tasks:
                kwargs = node_config[task]["task_parameter"]
                self._add_node(right_group, task, node_config[task]['text'], **kwargs)

    def generate_svg(self) -> str:
        """ ダイアグラムをsvg形式に変換し、文字列で出力するメソッドです。

        Returns:
            str: svg形式で書かれたダイアグラムデータの文字列

        """
        svg_data = self.dot.pipe(format='svg').decode('utf-8')

        return svg_data
