# -*- coding: utf-8 -*-
import re
import sys
import os

from pathlib import Path
from itertools import chain, zip_longest

from lxml import etree
from nbformat import read, NO_CONVERT

from .. import file


title_font_size = 10
item_font_size = 7
head_margin = 2
text_margin = 1
title_font_color = 'rgb(255,140,0)'
text_font_color = 'rgb(0,0,0)'

SVG_TEXT = '{http://www.w3.org/2000/svg}text'
SVG_RECT = '{http://www.w3.org/2000/svg}rect'


def init_config(id, name):
    return {
        id : {
            'name': name,
            'is_link': True,
            'init_nb': True
        }
    }


def update_svg(output: str, current_dir:str, notebook_dir:str, config):
    _embed_detail_information(current_dir, Path(output), Path(notebook_dir), config)

def setup_python_path():
    ver = sys.version_info
    lib_path = f'~/.local/lib/python{ver.major}.{ver.minor}/site-packages'
    lib_path = str(Path(lib_path).expanduser())
    if lib_path not in sys.path:
        sys.path.append(lib_path)

def _embed_detail_information(current_dir, skeleton, dir_util, config):
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
        if not value['is_link']:
            continue
        if value['text'] == elem.text:
            link = value['path']
            link = file.relative_path(link, current_dir).replace("../", "./../")
            if link:
                font_color = title_font_color
            else:
                font_color = text_font_color

            parent_elem = elem.getparent()
            childpos = elem.getparent().index(elem)
            text_elem = elem
            text_elem.attrib['fill'] = font_color
            text_elem.attrib['font-family'] = 'sans-serif'
            text_elem.attrib['font-size'] = str(title_font_size)
            text_elem.attrib['font-weight'] = 'bold'
            text_elems = [text_elem]
            if link:
                text_elems = create_anchor(text_elems, link)
                parent_elem.insert(childpos, text_elems)
            else:
                for text_elem in text_elems:
                    parent_elem.insert(childpos, text_elem)

def create_anchor(elems, link):
    a_elem = etree.Element('a')
    a_elem.attrib['{http://www.w3.org/1999/xlink}href'] = link
    for elem in elems:
        a_elem.append(elem)
    return a_elem