""" メタデータの整形、取得、返却を行うモジュールです。

このモジュールはメタデータに必要な値を用意します。
プロジェクトメタデータを整形したり、メタデータのテンプレートを取得したり、メタデータをフォーマットして返却するメソッドがあります。
"""
import json
import requests
from typing import Union


class Metadata():
    """ 取得したメタデータを表示するためのクラスです。"""

    def format_metadata(self, metadata:dict) -> dict[str, list]:
        """ Gakunin RDMから取得したプロジェクトメタデータを整形するメソッドです。
            Args:
                metadata(dict):メタデータの値
            Returns:
                list:Dmpの値を返す。
        """

        datas = metadata['data']
        # {'dmp': first_value}
        first_value = []
        for data in datas:
            url = data["relationships"]["registration_schema"]["links"]["related"]["href"]
            schema = self.get_schema(url)

            # first_value = [second_layer, ...]
            second_layer = {'title': data['attributes']['title']}
            registration = data['attributes']['registration_responses']
            for key, value in registration.items():
                if key != 'grdm-files':
                    second_layer[key] = self.format_display_name(schema, "page1", key, value)

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

            second_layer['grdm-files'] = self.format_display_name(schema, "page2", 'grdm-files', file_values)
            first_value.append(second_layer)

        return {'dmp': first_value}

    def get_schema(self, url:str) -> dict:
        """ メタデータのプロトコル名を取得するメソッドです。

        リクエストされたURLに接続し、その接続に問題がないかを確認してプロトコル名を取得する。

        Args:
            url(str):メタデータのURL

        Returns:
            dict:メタデータのプロトコル名の値を返す。
        """
        response = requests.get(url=url)
        response.raise_for_status()
        return response.json()

    def format_display_name(self, schema: dict, page_id: str, qid: str, value: Union[str, list, None] = None) -> dict:
        """ メタデータをフォーマットして返却するメソッドです。

        Args:
            schema (dict): メタデータのプロトコル名
            page_id (str): プロジェクトメタデータ("page1")、ファイルメタデータ("page2")
            qid (str): メタデータのqid
            value (str, list): メタデータに設定された値. Defaults to None.

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