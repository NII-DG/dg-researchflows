import re

class PatternMatcher:

    @staticmethod
    def is_empty(value: str):
        """空文字もしくは空白文字かどうかを判定する"""
        return bool(not value or value.isspace())

    @staticmethod
    def is_half(value: str):
        """半角英数記号かどうかを判定"""
        return bool(re.match(r'^[\x20-\x7E]*$', value))