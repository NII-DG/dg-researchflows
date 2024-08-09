""" 文字列を操作するモジュールです。"""
import re


class StringManager:
    """ 文字列を操作するクラスです。"""
    @staticmethod
    def is_empty(text: str) -> bool:
        """ 空文字もしくは空白文字かどうかを判定するメソッドです。

        Args:
            text (str): 判定する文字列を設定します。

        Returns:
            bool: 空文字もしくは空白文字かどうかを返す。

        """
        return bool(not text or text.isspace())

    @staticmethod
    def has_whitespace(text: str) -> bool:
        """ 空白文字が含まれるかどうかを判定するメソッドです。

        Args:
            text (str): 判定する文字列を設定します。

        Returns:
            bool: 空白文字が含まれるかどうかを返す。

        """
        return any(char.isspace() for char in text)

    @staticmethod
    def is_half(text: str) -> bool:
        """ 半角英数記号かどうかを判定するメソッドです。

        Args:
            text (str): 判定する文字列を設定します。

        Returns:
            bool: 半角英数記号かどうかを返す。

        """
        return bool(re.match(r'^[\x20-\x7E]*$', text))

    @staticmethod
    def strip(text:str, remove_empty: bool=True) -> str:
        """ 文字列の両端の空白文字を削除するメソッドです。

        remove_empty=Falseのとき、空白文字のみで構成された文字列が渡された場合にもとの文字列をそのまま返す。

        Args:
            text (str): 対象の文字列を設定します。
            remove_empty (bool): 空白文字のみの文字列が渡された場合にもとの文字列を返すかを設定します。

        Returns:
            str: 両端の空白文字を削除した文字列を返す。

        """
        if not text.strip() and not remove_empty:
            return text
        else:
            return text.strip()
