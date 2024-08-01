""" コマンドを実行するモジュールです。"""
import subprocess
from typing import Tuple
from ..utils.error import ExecCmdError

class Cmd():
    """ シェルコマンド実行のクラスです。"""

    @classmethod
    def decode_exec_subprocess(cls, cmd: str, cwd: str='', raise_error: bool=True)->Tuple[str, str, int]:
        """ コマンドの実行結果をデコードするメソッドです。

        引数で指定したコマンドを実行させ、その実行結果をデコードするメソッドです。

        Args:
            cmd(str): 実行するコマンドを設定します。
            cwd(str): プロセスの作業ディレクトリを設定します。デフォルト値は''です。
            raise_error(bool): コマンド実行失敗したときに例外を発生させるかを設定します。

        Returns:
            str: コマンドの標準出力を返す。
            str: コマンドの標準エラーを返す。
            int: コマンド実行の戻り値を返す。

        """
        stdout, stderr, rt = Cmd.exec_subprocess(cmd, cwd, raise_error)
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        return stdout, stderr, rt

    @classmethod
    def exec_subprocess(cls, cmd: str, cwd: str='', raise_error: bool=True)->Tuple[bytes, bytes, int]:
        """ 指定されたコマンドを新しいプロセスで実行するメソッドです。

        Args:
            cmd(str): 実行するコマンドを設定します。
            cwd(str): プロセスの作業ディレクトリを設定します。
            raise_error(bool): コマンド実行失敗したときに例外を発生させるかを設定します。

        Returns:
            bytes: コマンドの標準出力を返す。
            bytes: コマンドの標準エラーを返す。
            int: コマンド実行の戻り値を返す。

        Raises:
            ExecCmdError: コマンドの実行結果がエラー

        """
        if cwd == '':
            child = subprocess.Popen(cmd, shell=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            child = subprocess.Popen(cmd, shell=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        stdout, stderr = child.communicate()
        rt = child.returncode
        if rt != 0 and raise_error:
            raise ExecCmdError(f"command return code is not 0. got {rt}. stderr = {stderr}")

        return stdout, stderr, rt