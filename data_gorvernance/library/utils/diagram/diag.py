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

    def add_node_property(self, node_id: str, custom: str):
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



    def update_node_color(self, node_id: str, color: str):
        self.add_node_property(node_id, f'color="{color}"')

    def update_node_icon(self, node_id: str, path: str):
        self.add_node_property(node_id, f'background="{path}"')

    def update_node_style(self, node_id, style):
        self.add_node_property(node_id, f'style={style}')

    def update_node_stacked(self, node_id):
        """ノードの重ね合わせ"""
        self.add_node_property(node_id, f'stacked')

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

