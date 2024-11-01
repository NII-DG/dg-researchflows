""" ダイアグラムの管理を行うモジュールです。"""
import traceback

from graphviz import Digraph


class DiagManager:
    """ダイアグラムの管理を行うクラスです。

    Attributes:
        class:
            node_attr(dict): 全てのノードで共通となる設定
        instance:
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

        self.left_group = self.dot.subgraph(name='cluster_left')
        self.left_group.attr(style='filled',color='#FFE6CC')

        self.right_group = self.dot.subgraph(name='cluster_right')
        self.right_group.attr()
        self.right_group.edge_attr.update(style='invis')

    def add_node(self, node_id: str, node_label: str, node_group):
        """新たにノードを追加するメソッドです。

        Args:
            node_id (str): ノードIDを設定します。
            node_label (str): ノードの名前を設定します。
            node_group(subgraph): ノードを追加するサブグラフのオブジェクト

        """
        node_group.node(node_id, node_label)

        node_list = self.left_group.body
        if len(node_list) >= 2:
            self.left_group.edge(node_list[-1].split(' ')[0] , node_id)

    def embed_url(self, node_id: str,url: str) -> None:
        """ ノードにURLを埋め込むメソッドです。

        Args:
            node_id (str): ノードIDを設定します。
            url (str): 押下された際に遷移するノートブックのパス

        """
        self.dot.node(node_id, URL=url)

    def update_node_color(self, node_id: str, color: str) -> None:
        """ ノードの色を設定するメソッドです。

        Args:
            node_id (str): ノードIDを設定します。
            color (str): 追加する色を設定します。

        """
        self.dot.node(node_id, fontcolor='black', fillcolor=color )

    def update_node_icon(self, node_id: str, path: str) -> None:
        """ ノードのアイコンを設定するメソッドです。

        Args:
            node_id (str): ノードIDを設定します。
            path (str): アイコンのパスを設定します。

        """
        self.dot.node(node_id, image = path)

    #def update_node_style(self, node_id: str, style: str) -> None:
        #""" ノードのスタイルを設定するメソッドです。一回も呼び出されていない

        #Args:
            #node_id (str): ノードIDを設定します。
            #style (str): 新しいスタイルを設定します。

        #"""
        #self.add_node_property(node_id, f'style={style}')

    #def update_node_stacked(self, node_id: str) -> None:
        #""" ノードの重ね合わせのメソッドです。代替案が出るまで放置

        #Args:
            #node_id (str): ノードIDを設定します。

        #"""
        #self.add_node_property(node_id, f'stacked')

    def generate_svg(self, output: str, font: str) -> None:
        """ diagファイルからsvgファイルを生成するメソッドです。

        Args:
            output (str): 出力するパスを設定します。
            font (str): フォントを設定します。

        """
        self.dot.attr('node', fontname=str(font))
        self.dot.render(output, cleanup=True)
