""" SVGファイル操作のモジュールです。"""
# -*- coding: utf-8 -*-
from pathlib import Path

from lxml import etree

from library.utils import file


title_font_size = 10
title_font_color = 'rgb(255,140,0)'
text_font_color = 'rgb(0,0,0)'

SVG_TEXT = '{http://www.w3.org/2000/svg}text'


def init_config(id:str, name:str) -> dict:
    """ 初期設定を行う関数です。

    Args:
        id (str): 識別子を設定します。
        name (str): 名前を設定します。

    Returns:
        dict: 初期設定を含む辞書を返す。

    """
    return {
        id : {
            'name': name,
            'is_link': True
        }
    }


def update_svg(output:str, current_dir:str, config:dict) -> None:
    """ svgファイルを更新する関数です。

    Args:
        output (str): 出力先のパスを設定します。
        current_dir (str): 作業ディレクトリを設定します。
        config (dict): 設定情報の辞書を設定します。

    """
    _embed_detail_information(current_dir, Path(output), config)


def _embed_detail_information(current_dir:str, skeleton:Path, config:dict) -> None:
    """ 詳細情報を埋め込む関数です。

    Args:
        current_dir (str): 作業ディレクトリを設定します。
        skeleton (Path): 雛形のパスを設定します。
        config (dict): 設定情報を含む辞書を設定します。

    """
    # 雛形の読み込み
    tree = etree.parse(str(skeleton))

    # 雛形をNotebook情報で置き換え
    for elem in list(tree.findall(SVG_TEXT)):
        _embed_info_in_one_rect(elem, current_dir, config)

    # svgファイルを上書き
    with skeleton.open(mode='wb') as f:
        f.write(etree.tostring(tree, method='xml', pretty_print=True))


def _embed_info_in_one_rect(elem:etree.Element, current_dir:str, config:dict) -> None:
    """ 一つの矩形に情報を埋め込む関数です。

    Args:
        elem (etree.Element): svgファイルの要素を設定します。
        current_dir (str): 作業ディレクトリを設定します。
        config (dict): 設定情報を含む辞書を設定します。

    """
    for key, value in config.items():
        # タスクタイトルと一致していない場合処理をスキップする
        if value['text'] != elem.text:
            continue

        parent_elem = elem.getparent()
        childpos = elem.getparent().index(elem)

        text_elem = elem
        text_elem.attrib['font-family'] = 'sans-serif'
        text_elem.attrib['font-size'] = str(title_font_size)
        text_elem.attrib['font-weight'] = 'bold'
        inseet_elem = None
        # is_linkがTrueだった場合、リンクを付与する処理に進む
        if value['is_link']:
            text_elem.attrib['fill'] = title_font_color
            link = value['path']
            link = file.relative_path(link, current_dir).replace("../", "./../")
            inseet_elem = create_anchor([text_elem], link)
        else:
            text_elem.attrib['fill'] = text_font_color
            inseet_elem = text_elem
        parent_elem.insert(childpos, inseet_elem)


def create_anchor(elems:list, link:str):
    """リンクを付与する関数です。

    Args:
        elems (list): リンクを付与する要素のリストを設定します。
        link (str): リンクのURLを設定します。

    Returns:
        etree.Element: リンクを付与した要素を返す。

    """
    a_elem = etree.Element('a')
    a_elem.attrib['{http://www.w3.org/1999/xlink}href'] = link
    for elem in elems:
        a_elem.append(elem)
    return a_elem
