""" ガバナンスシートやメタデータの設定値を扱うモジュールです。"""
def need_govrun_token(govsheet:dict, metadata:dict):
    """ Governed Runのトークンが必要かどうかを判定する関数です。

    Args:
        govsheet (dict): ガバナンスシートを設定します。
        metadata (dict): メタデータを設定します。

    Returns:
        bool: Governed Runのトークンが必要かを返す。
    """
    if govsheet.get("rerun", {}).get("rerunLevel") == "設定しない":
        return False
    if not metadata.get("runCrate"):
        return False
    return True