"""DMPデータを操作するクラスが記載されたモジュールです。"""
from ..file import JsonFile


class DMPManager(JsonFile):
    """DMPデータの操作を行うクラスです。

    """
    def __init__(self, file_path: str):
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        Args:
            file_path (str): ファイルパスを表す文字列

        """
        super().__init__(file_path)

    @staticmethod
    def create_dmp_options(contents:dict)->dict:
        """dmpのタイトルを抽出し、オプションの一覧を作成するメソッドです。

        Args:
            contents (dict): dmpデータ群

        Returns:
            dict:dmpのタイトル一覧

        """
        dmps = contents['dmp']
        options = {}
        for i, dmp in enumerate(dmps):
            title = dmp['title']
            options[title] = i
        return options

    @staticmethod
    def get_dmp(contents:dict, index:int)->dict[str, list]:
        """指定したdmpを取得するためのメソッドです。

        Args:
            contents (dict):dmpデータ群
            index (int):索引

        Returns:
            dict[str, list]:Indexで指定したdmpのデータ

        """
        return {"dmp": [contents['dmp'][index]]}

    @staticmethod
    def display_format(content:dict)->str:
        """dmpデータの表示フォーマットを作成するメソッドです。

        Args:
            content (dict):dmpデータ群

        Returns:
            str:表示する際のフォーマットに整えたdmpデータ

        """
        dmp = content['dmp'][0]
        dmp_str = f"### {dmp['title']}<br><hr><br>"
        for key, value in dmp.items():
            if key != "title" and key != 'grdm-files':
                if 'field_name_jp' in value.keys():
                    dmp_str += f'{value.get("label_jp")} : {value.get("field_name_jp")}<br>'
                else:
                    dmp_str += f'{value.get("label_jp")} : {value.get("value")}<br>'
        files = dmp['grdm-files']
        dmp_str += f'{files.get("label_jp")} :<br>'
        value = files.get("value")
        for file in value:
            dmp_str += f'&emsp;{file.get("path")}<br>'
        return dmp_str

