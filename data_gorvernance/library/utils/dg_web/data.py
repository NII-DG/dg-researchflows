"""ガバナンスシートやメタデータの設定値を扱う"""
def need_govrun_token(govsheet:dict, metadata:dict):

    if govsheet.get("rerun", {}).get("rerunLevel") == "設定しない":
        return False
    if not metadata.get("runCrate"):
        return False
    return True