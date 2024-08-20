""" ダイアグラムの管理を行うモジュールです。"""
from pathlib import Path
from subprocess import run
import traceback

from blockdiag.command import BlockdiagApp
from blockdiag.utils.logging import error

from library.utils.file import File


class DiagManager:
    """ダイアグラムの管理を行うクラスです。

    Attributes:
        instance:
            path(Path): ファイルのパス
            content(str): ファイルの内容

    """

    def __init__(self, file_path:str) -> None:
        """ クラスのインスタンスの初期化処理を実行するメソッドです。

        Args:
            file_path (str): ファイルパスを設定します。

        """
        self.path = Path(file_path)
        # 以下暫定措置としてファイル書き変えのために用いる
        self.content = File(str(self.path)).read()

    def add_node_property(self, node_id:str, custom:str) -> None:
        """ノードに属性を追加するメソッドです。

        Args:
            node_id (str): ノードIDを設定します。
            custom (str): 追加する属性を設定します。

        """
        lines = self.content.splitlines()
        new_lines = []
        is_replaced = True
        for line in lines:
            if is_replaced and node_id in line:
                find = f'{node_id}['
                replace = f'{node_id}[{custom}, '
                update_content = line.replace(find, replace, 1)
                if update_content == line:
                    find = f'{node_id}'
                    replace = f'{node_id}[{custom}]'
                    update_content = line.replace(find, replace, 1)
                new_lines.append(update_content)
                is_replaced = False
            else:
                new_lines.append(line)
        self.content = '\n'.join(new_lines)

    def update_node_color(self, node_id:str, color:str) -> None:
        """ ノードの色を設定するメソッドです。

        Args:
            node_id (str): ノードIDを設定します。
            color (str): 追加する色を設定します。

        """
        self.add_node_property(node_id, f'color="{color}"')

    def update_node_icon(self, node_id:str, path:str) -> None:
        """ ノードのアイコンを設定するメソッドです。

        Args:
            node_id (str): ノードIDを設定します。
            path (str): アイコンのパスを設定します。

        """
        self.add_node_property(node_id, f'background="{path}"')

    def update_node_style(self, node_id:str, style:str) -> None:
        """ ノードのスタイルを設定するメソッドです。

        Args:
            node_id (str): ノードIDを設定します。
            style (str): 新しいスタイルを設定します。

        """
        self.add_node_property(node_id, f'style={style}')

    def update_node_stacked(self, node_id:str) -> None:
        """ ノードの重ね合わせのメソッドです。

        Args:
            node_id (str): ノードIDを設定します。

        """
        self.add_node_property(node_id, f'stacked')

    def generate_svg(self, tmp_diag:str, output:str, font:str) -> None:
        """ diagファイルからsvgファイルを生成するメソッドです。

        Args:
            tmp_diag (str): 一時的なダイアグラムのパスを設定します。
            output (str): 出力するパスを設定します。
            font (str): フォントを設定します。

        """
        File(str(tmp_diag)).write(self.content)
        diag = tmp_diag
        run(['blockdiag', '-f', font, '-Tsvg', '-o', output, diag], check=True)

    # 仮置き
    def run(self, output:str, diag:str, font:str) -> int:
        """ 新しいプロセスでなくダイアグラムを生成するメソッドです。

        Args:
            output (str): 出力するパスを設定します。
            diag (str): ダイアグラムを設定します。
            font (str): フォントを設定します。

        Returns:
            int: 実行結果を返す。

        """
        app = BlockdiagApp()
        args = ['-f', font, '-Tsvg', '-o', output, diag]

        try:
            app.parse_options(args)
            app.create_fontmap()
            app.setup()

            parsed = app.parse_diagram()
            # TODO: ここで書き変えられるといい
            return app.build_diagram(parsed)
        except SystemExit as e:
            return e
        except UnicodeEncodeError:
            error("UnicodeEncodeError caught (check your font settings)")
            return -1
        except Exception as e:
            if app.options and app.options.debug:
                traceback.print_exc()
            else:
                error("%s" % e)
            return -1
        finally:
            app.cleanup()
