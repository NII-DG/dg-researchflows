"""このモジュールはメタデータを取得します。
    プロジェクトメタデータを整形したり、メタデータのテンプレートを取得したり、メタデータをフォーマットして返却する関数があります。
"""
import json
import requests

def format_metadata(metadata):
    """Gakunin RDMから取得したプロジェクトメタデータを整形する関数です。
    
    Args:メタデータの値

    Returns:
        Dmpの値を返す。

    
    
    """

    datas = metadata['data']
    # {'dmp': first_value}
    first_value = []
    for data in datas:
        url = data["relationships"]["registration_schema"]["links"]["related"]["href"]
        schema = get_schema(url)

        # first_value = [second_layer, ...]
        second_layer = {'title': data['attributes']['title']}
        registration = data['attributes']['registration_responses']
        for key, value in registration.items():
            if key != 'grdm-files':
                second_layer[key] = format_display_name(schema, "page1", key, value)

        files = json.loads(registration['grdm-files'])
        # grdm-files > value
        file_values = []
        for file in files:
            file_datas = {}
            file_datas['path'] = file['path']
            file_metadata = {}
            for key, item in file['metadata'].items():
                file_metadata[key] = item['value']
            file_datas['metadata'] = file_metadata
            file_values.append(file_datas)

        second_layer['grdm-files'] = format_display_name(schema, "page2", 'grdm-files', file_values)
        first_value.append(second_layer)

    return {'dmp': first_value}


def get_schema(url):
    """メタデータのテンプレートを取得する関数です
            リクエストされたURLに接続し、その接続に問題がないかを確認してテンプレートを取得する。
    Args:メタデータのURL

    Returns:
        メタデータのテンプレートの値を返す。
    
    """
    response = requests.get(url=url)
    response.raise_for_status()
    return response.json()


def format_display_name(schema: dict, page_id: str, qid: str, value=None):
    """メタデータをフォーマットして返却する

    Args:
        schema (dict): メタデータのテンプレート
        page_id (str): プロジェクトメタデータ("page1")、ファイルメタデータ("page2")
        qid (str): メタデータのqid
        value (optional): メタデータに設定された値. Defaults to None.

    Returns:
        dict: フォーマットされたメタデータの値
    """
    pages = schema["data"]["attributes"]["schema"]["pages"]
    items = {}
    for page in pages:
        if page.get("id") != page_id:
            continue

        questions = page["questions"]
        for question in questions:
            if question.get("qid") != qid:
                continue

            items['label_jp'] = question.get("nav")
            if value is None:
                break
            items['value'] = value

            options = question.get("options", [])
            for option in options:
                if option.get("text") != value:
                    continue
                items['field_name_jp'] = option.get("tooltip")
                break
            break
        break

    return items