""" ダイアグラムの管理を行うモジュールです。"""
import traceback
import os
import logging
import subprocess

from graphviz import Digraph


class DiagManager:
    """ダイアグラムの管理を行うクラスです。

    Attributes:
        class:
            node_attr(dict): 全てのノードで共通となる設定
        instance:
            dot(Digraph): ダイアグラムの情報を保持するオブジェクト
            path(Path): ファイルのパス
            content(str): ファイルの内容

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

    def __init__(self):
        """ クラスのインスタンスの初期化処理を実行するメソッドです。"""
        self.dot = Digraph(format='svg', node_attr= self.node_attr)
        self.dot.attr(ranksep='0.4')

    def add_node(self, node_group, node_id: str, node_label: str, **kwargs):
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

    def create_left_subgraph(self, tasks: list, node_config: dict):
        """左側に配置される実行順の決まっているタスクのノード群を作成するメソッドです。

        args:
            tasks(list): 追加するノードの一覧
            node_config(dict): ノードの設定に用いる情報

        """
        with self.dot.subgraph(name='cluster_left') as left_group:
            left_group.attr(style='filled', color='#FFE6CC')
            for task in tasks:
                kwargs = node_config[task]["task_parameter"]
                self.add_node(left_group, task, node_config[task]['text'], **kwargs)

    def create_right_subgraph(self, tasks: list, node_config: dict):
        """右側に配置されるいつ実行しても構わないタスクのノード群を作成するメソッドです。

        args:
            tasks(list): 追加するノードの一覧
            node_config(dict): ノードの設定に用いる情報

        """
        with self.dot.subgraph(name='cluster_right') as right_group:
            right_group.attr(style='invis')
            right_group.edge_attr.update(style='invis')
            for task in tasks:
                kwargs = node_config[task]["task_parameter"]
                self.add_node(right_group, task, node_config[task]['text'], **kwargs)

    def generate_svg(self, output: str) -> None:
        """ diagファイルからsvgファイルを生成するメソッドです。

        Args:
            output (str): 出力するパスを設定します。

        """
        svg_data = self.dot.pipe(format='svg').decode('utf-8')

        with open(output, 'w', encoding='utf-8') as file:
            file.write(svg_data)
            print(svg_data)
