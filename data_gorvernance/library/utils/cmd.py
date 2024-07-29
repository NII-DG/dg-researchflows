import subprocess

from .error import ExecCmdError


class Cmd():

    @classmethod
    def decode_exec_subprocess(cls, cmd: str, cwd:str='', raise_error=True):
        stdout, stderr, rt = Cmd.exec_subprocess(cmd, cwd, raise_error)
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        return stdout, stderr, rt

    @classmethod
    def exec_subprocess(cls, cmd: str, cwd:str='', raise_error=True):
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
