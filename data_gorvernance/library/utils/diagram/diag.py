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

    def change_group_color(self, group_id: str, color: str):
        pass

    def update_mark(self, node_id: str, value: str):
        pass

    def change_node_style(self, node_id, style):
        pass

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

