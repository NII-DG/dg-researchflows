import subprocess

class Cmd():

    @classmethod
    def decode_exec_subprocess(cls, cmd: str, raise_error=True):
        stdout, stderr, rt = Cmd.exec_subprocess(cmd, raise_error)
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        return stdout, stderr, rt

    @classmethod
    def exec_subprocess(cls, cmd: str, raise_error=True):
        child = subprocess.Popen(cmd, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = child.communicate()
        rt = child.returncode
        if rt != 0 and raise_error:
            raise Exception(f"command return code is not 0. got {rt}. stderr = {stderr}")

        return stdout, stderr, rt