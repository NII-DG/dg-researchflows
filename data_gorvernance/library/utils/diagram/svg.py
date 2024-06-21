# -*- coding: utf-8 -*-
import sys
from pathlib import Path

from lxml import etree

from .. import file

title_font_size = 10
title_font_color = 'rgb(255,140,0)'

SVG_TEXT = '{http://www.w3.org/2000/svg}text'

def init_config(id, name):
    return {
        id : {
            'name': name,
            'is_link': True,
            'init_nb': True
        }
    }

def update_svg(output: str, current_dir:str, config):
    _embed_detail_information(current_dir, Path(output), config)

def _embed_detail_information(current_dir, skeleton, config):
    # 雛形の読み込み
    tree = etree.parse(str(skeleton))

    # 雛形をNotebook情報で置き換え
    for elem in list(tree.findall(SVG_TEXT)):
        _embed_info_in_one_rect(elem, current_dir, config)

    # svgファイルを上書き
    with skeleton.open(mode='wb') as f:
        f.write(etree.tostring(tree, method='xml', pretty_print=True))

def _embed_info_in_one_rect(elem, current_dir, config):
    for key, value in config.items():
        # is_linkがFalseの場合、リンク付与せず処理をスキップする
        if not value['is_link']:
            text_elem = elem
            text_elem.attrib['font-weight'] = 'bold'
            continue
        if value['text'] == elem.text:
            # タスクタイトルと一致したらリンクを付与する
            link = value['path']
            link = file.relative_path(link, current_dir).replace("../", "./../")

            parent_elem = elem.getparent()
            childpos = elem.getparent().index(elem)

            text_elem = elem
            text_elem.attrib['fill'] = title_font_color
            text_elem.attrib['font-family'] = 'sans-serif'
            text_elem.attrib['font-size'] = str(title_font_size)
            text_elem.attrib['font-weight'] = 'bold'
            text_elems = create_anchor([text_elem], link)
            parent_elem.insert(childpos, text_elems)

def create_anchor(elems, link):
    """リンクを付与する"""
    a_elem = etree.Element('a')
    a_elem.attrib['{http://www.w3.org/1999/xlink}href'] = link
    for elem in elems:
        a_elem.append(elem)
    return a_elem