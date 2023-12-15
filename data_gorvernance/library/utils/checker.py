import re

class StringManager:

    @staticmethod
    def is_empty(text: str):
        """空文字もしくは空白文字かどうかを判定する"""
        return bool(not text or text.isspace())

    @staticmethod
    def has_whitespace(text: str):
        """空白文字が含まれるかどうかを判定する"""
        return any(char.isspace() for char in text)

    @staticmethod
    def is_half(text: str):
        """半角英数記号かどうかを判定する"""
        return bool(re.match(r'^[\x20-\x7E]*$', text))

    @staticmethod
    def strip(text:str, remove_empty=False)->str:
        """文字列の両端の空白文字を削除する

        remove_empty=Trueのとき、空白文字のみで構成された文字列が渡された場合にもとの文字列をそのまま返す
        """
        if not text.strip() and remove_empty:
            return text
        else:
            return text.strip()