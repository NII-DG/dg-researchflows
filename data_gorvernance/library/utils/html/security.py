import html


# HTMLエンティティエスケープを行う
def escape_html_text(original_string)->str:
    return html.escape(original_string)