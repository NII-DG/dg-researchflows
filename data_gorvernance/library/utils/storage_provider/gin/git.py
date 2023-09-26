from ...cmd import Cmd

def get_remote_url():
    stdout, stderr, rt = Cmd.decode_exec_subprocess('git config --get remote.origin.url')
    return stdout.replace('\n', '')

def git_annex_untrust(cwd):
    stdout, stderr, rt = Cmd.exec_subprocess(cmd='git annex untrust here', cwd=cwd)
    result = stdout.decode('utf-8')
    return result

def git_annex_trust(cwd):
    stdout, stderr, rt = Cmd.exec_subprocess(cmd='git annex --force trust web', cwd=cwd)
    result = stdout.decode('utf-8')

def git_annex_lock(path:str):
    stdout, stderr, rt = Cmd.exec_subprocess(f'git annex lock {path}', raise_error=False)
    result = stdout.decode('utf-8')
    return result

def git_annex_unlock(path:str):
    stdout, stderr, rt = Cmd.exec_subprocess(f'git annex unlock {path}',raise_error=False)
    result = stdout.decode('utf-8')
    return result

def git_annex_metadata_add_minetype_sha256_contentsize(file_path, mime_type, sha256, content_size, exec_path):
    Cmd.exec_subprocess(f'git annex metadata "{file_path}" -s mime_type={mime_type} -s sha256={sha256} -s content_size={content_size}', cwd=exec_path)

def git_annex_metadata_add_sd_date_published(file_path, sd_date_published, exec_path):
    Cmd.exec_subprocess(f'git annex metadata "{file_path}" -s sd_date_published={sd_date_published}', cwd=exec_path)

def git_commmit(msg:str, cwd):
    stdout, stderr, rt = Cmd.exec_subprocess('git commit -m "{}"'.format(msg), cwd=cwd,raise_error=False)
    result = stdout.decode('utf-8')
    return result

def exec_git_status(cwd):
    """execute 'git status' commands

    RETURN
    ---------------
    Returns output result

    EXCEPTION
    ---------------

    """
    stdout, stderr, rt = Cmd.exec_subprocess('git status', cwd)
    result = stdout.decode('utf-8')
    return result

def is_conflict(cwd) -> bool:
    result = exec_git_status(cwd)
    lines = result.split('\n')
    for l in lines:
        if 'both modified:' in l or 'both added:' in l:
            return True
    return False
