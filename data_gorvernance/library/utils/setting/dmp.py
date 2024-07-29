"""DMPを操作する機能のモジュールです。
DMPデータの検索や並べ替えを行うクラスが記載されています。
"""
from ..file import JsonFile


class DMPManager(JsonFile):
    """DMPデータの操作を行うクラスです。

    DMPデータの検索や並べ替えを行うメソッドを記載しています。
       
    """
    def __init__(self, file_path: str):
        """クラスのインスタンスの初期化を行うメソッドです。コンストラクタ

        引数として受け取ったファイルパスで親クラスのコンストラクタを呼び出します。

        Args:
            file_path (str): ファイルパスを表す文字列
        
        Example:
            >>> DMPManager.__init__()
        
        Note:
            特にありません。

        """
        super().__init__(file_path)

    @staticmethod
    def create_dmp_options(contents):
        """データを解析し、オプションの辞書を作成する静的なメソッドです。

        引数として受け取ったデータからdmpのタイトルを抽出し、その辞書を作成します。

        Args:
            contents (_type_): dmpデータを含むデータ群

        Returns:
            dict:dmpのタイトル一覧
        
        Example:
            >>> DMPManager.create_dmp_options(contents)
            dict

        Note:
            特にありません。
        
        """
        dmps = contents['dmp']
        options = {}
        for i, dmp in enumerate(dmps):
            title = dmp['title']
            options[title] = i
        return options

    @staticmethod
    def get_dmp(contents, index):
        """指定したdmpを取得するための静的なメソッドです。

        引数として受け取ったcontentsから同じく引数であるindexに対応したdmpを取得し、辞書型で返します。

        Args:
            contents (Any):dmpデータを含むデータ群
            index (Any):索引

        Returns:
            dict[str, list]:Indexで指定したdmpのデータ
        
        Example:
            >>> DMPManager.get_dmp(contents, index)
            dict

        Note:
            特にありません。

        """
        return {"dmp": [contents['dmp'][index]]}

    @staticmethod
    def display_format(content):
        """dmpデータの表示フォーマットを作成する静的メソッドです。

        引数として受けとったデータからdmpの情報を取り出し、表示する際のフォーマットに合うよう成形します。

        Args:
            content (Any):dmpデータを含むデータ群

        Returns:
            str:表示する際のフォーマットに整えたdmpデータ

        Example:
            >>> DMPManager.display_format(content)
            dmp_str

        Note:
            特にありません。
        
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

