from ...cmd import Cmd

def get_remote_url():
    stdout, stderr, rt = Cmd.decode_exec_subprocess('git config --get remote.origin.url')
    return stdout.replace('\n', '')
