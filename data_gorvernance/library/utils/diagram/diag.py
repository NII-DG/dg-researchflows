from pathlib import Path
import traceback
from subprocess import run

from blockdiag.command import BlockdiagApp
from blockdiag.utils.logging import error

from ..file import File


class DiagManager:

    def __init__(self, file_path: str) -> None:
        self.path = Path(file_path)
        # 以下暫定措置としてファイル書き変えのために用いる
        self.content = File(str(self.path)).read()

    def change_node_property(self, node_id: str, key:str, value: str):
        find = f'{node_id}['
        replace = f'{node_id}[{key} = {value}, '
        update_content = self.content.replace(find, replace)
        if update_content == self.content:
            find = f'{node_id}'
            replace = f'{node_id}[{key} = {value}] '
            update_content = self.content.replace(find, replace)
        self.content = update_content

    def update_node_color(self, node_id: str, color: str):
        self.change_node_property(node_id, "color", color)

    def update_node_icon(self, node_id: str, path: str):
        self.change_node_property(node_id, "icon", path)

    def update_node_style(self, node_id, style):
        self.change_node_property(node_id, "style", style)

    def delete_node(self, node_id):
        pass

    def generate_svg(self, tmp_diag: str, output: str, font: str):
        File(str(tmp_diag)).write(self.content)
        diag = tmp_diag
        run(['blockdiag', '-f', font, '-Tsvg', '-o', output, diag], check=True)

    # 仮置き
    def run(self, output, diag, font):
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

