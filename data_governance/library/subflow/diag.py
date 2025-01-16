""" ダイアグラムの管理を行うモジュールです。"""

import copy
import os
from typing import Optional

from graphviz import Digraph

from library.utils import file
from library.utils.setting.status import SubflowTask


#現在のスクリプトのディレクトリパス
script_dir = os.path.dirname(os.path.abspath(__file__))

class DiagManager:
    """ダイアグラムの管理を行うクラスです。

    Attributes:
        class:
            rank_sep(str): ランクの異なるノード間の距離の設定
            node_attr(dict): 全てのノードで共通となる設定
            left_group_status(dict): 左側に表示する実行順の決まっているグループの設定
            unfeasible_status(dict): 実行不可能なタスクの設定

        instance:
            dot(Digraph): ダイアグラムの情報を保持するオブジェクト

    """
    #全てのノードで共通となる設定
    rank_sep = '0.4'
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
    #左側に配置するグループの設定
    left_group_status = {
        'style': 'filled',
        'color': '#FFE6CC'
    }
    #実行不能な場合の設定
    unfeasible_status = {
        "fontcolor": 'black',
        "fillcolor": '#e6e5e3'
    }

    def __init__(self):
        """ クラスのインスタンスの初期化処理を実行するメソッドです。"""
        self.dot = Digraph(node_attr=self.node_attr)
        self.dot.attr(ranksep=self.rank_sep)

    def _set_task_status(self, current_dir: str, node_config: dict, task: SubflowTask) -> dict:
        """ フロー図の見た目をタスクの状態によって変えるための情報を設定するメソッドです。

        Args:
            current_dir(str): サブフローメニューの親ディレクトリ
            node_config(dict): ダイアグラムのノード設定用の辞書
            task (SubflowTask): 調整するタスクを設定します。

        Returns:
            dict: ノードに設定する情報

        """
        task_parameter = {}

        icon_dir = "../data/icon"
        icon_dir = os.path.abspath(os.path.join(script_dir, icon_dir))
        icon_dir = file.relative_path(icon_dir, current_dir)

        if task.is_multiple:
            node_config[task.id]["text"] += '　\U0001F501'

        if task.status == task.STATUS_UNFEASIBLE:
            task_parameter = copy.copy(self.unfeasible_status)
            task_parameter["image"] = os.path.join(icon_dir, "lock.png")
            return task_parameter

        if task.status == task.STATUS_DONE:
            task_parameter["image"] = os.path.join(icon_dir, "check_mark.png")
            node_config[task.id]['path'] += "?init_nb=true"

        elif task.status == task.STATUS_DOING:
            task_parameter["image"] = os.path.join(icon_dir, "loading.png")

        #実行不可以外のタスクにURLを埋め込む
        link = file.relative_path(
            str(node_config[task.id]['path']), current_dir).replace("../", "./../")
        task_parameter["URL"] = link
        return task_parameter

    def _add_node(self, node_group: Digraph, node_id: str, node_label: str, prev_id: Optional[str], **kwargs):
        """新たにノードを追加するメソッドです。

        Args:
            node_group(Digraph): ノードを追加するサブグラフのオブジェクト
            node_id (str): ノードIDを設定します。
            node_label (str): ノードの名前を設定します。
            prev_id(str): 表示した際にひとつ上に並ぶタスクのid。デフォルトはNone
            **kwargs(dict): ノードに設定する情報

        """
        node_group.node(node_id, label=node_label, **kwargs)

        #ノードが複数ある場合、エッジを作成する
        if prev_id:
            node_group.edge(prev_id, node_id)

    def create_left_subgraph(self, current_dir: str, tasks: list[SubflowTask], node_config: dict, order_sequence: list):
        """左側に配置される実行順の決まっているタスクのノード群を作成するメソッドです。

        args:
            current_dir(str): サブフローメニューの親ディレクトリ
            tasks(list[SubflowTask]): サブフローのタスクの設定値
            node_config(dict): ダイアグラムのノード設定用の辞書
            order_sequence(list): 左側に配置される実行順の決まっているタスクの順序情報

        """
        with self.dot.subgraph(name='cluster_left') as left_group:
            left_group.attr(**self.left_group_status)
            prev_id = None
            for task_id in order_sequence:
                for task in tasks:
                    if task_id == task.id:
                        if task.active:
                            kwargs = self._set_task_status(current_dir, node_config, task)
                            self._add_node(left_group, task.id, node_config[task.id]['text'], prev_id, **kwargs)
                            prev_id = task.id
                        break
                else:
                    # This is intentional: Raise an error to ensure developers are alerted
                    raise Exception(f"The ID '{task_id}' is not defined in the tasks.")

    def create_right_subgraph(self, current_dir: str, tasks: list[SubflowTask], node_config: dict, order_whenever: list):
        """右側に配置されるいつ実行しても構わないタスクのノード群を作成するメソッドです。

        args:
            current_dir(str): サブフローメニューの親ディレクトリ
            tasks(list[SubflowTask]): サブフローのタスクの設定値
            node_config(dict): ダイアグラムのノード設定用の辞書
            order_sequence(list): 右側に配置される実行順の決まっていないタスクの順序情報

        """
        with self.dot.subgraph(name='cluster_right') as right_group:
            right_group.attr(style='invis')
            right_group.edge_attr.update(style='invis')
            prev_id = None
            for task_id in order_whenever:
                for task in tasks:
                    if task_id == task.id:
                        if task.active:
                            kwargs = self._set_task_status(current_dir, node_config, task)
                            self._add_node(right_group, task.id, node_config[task.id]['text'], prev_id, **kwargs)
                            prev_id = task.id
                        break
                else:
                    # This is intentional: Raise an error to ensure developers are alerted
                    raise Exception(f"The ID '{task_id}' is not defined in the tasks.")

    def generate_diagram(self, current_dir: str, tasks: list[SubflowTask], node_config: dict, order:dict) -> str:
        """"ダイアグラムを生成するメソッドです。

        args:
            current_dir(str): サブフローメニューの親ディレクトリ
            tasks(list[SubflowTask]): サブフローのタスクの設定値
            node_config(dict): ダイアグラムのノード設定用の辞書
            order_sequence(list): 右側に配置される実行順の決まっていないタスクの順序情報

        Returns:
            str: svg形式で書かれたダイアグラムデータの文字列

        """
        order_sequence = order["sequence"]
        self.create_left_subgraph(current_dir, tasks, node_config, order_sequence)
        order_whenever = order["whenever"]
        self.create_right_subgraph(current_dir, tasks, node_config, order_whenever)

        svg_data = self.dot.pipe(format='svg').decode('utf-8')

        return svg_data
