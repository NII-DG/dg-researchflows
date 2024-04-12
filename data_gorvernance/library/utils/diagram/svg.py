# -*- coding: utf-8 -*-
import re
import sys
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
    # Notebookのヘッダ取得
    nb_headers = _get_notebook_headers(dir_util)

    # 雛形の読み込み
    tree = etree.parse(str(skeleton))

    # 雛形をNotebook情報で置き換え
    for elem in list(tree.findall(SVG_TEXT)):
        if _is_target_rect(elem, nb_headers.keys(), config):
            nb_name = _find_matching_notebook(nb_headers.keys(), elem.text, config)
            nb_headers = _update_notebook_link(nb_headers, nb_name, config[elem.text])
            _embed_info_in_one_rect(elem, nb_headers, nb_name, current_dir)

    # svgファイルを上書き
    with skeleton.open(mode='wb') as f:
        f.write(etree.tostring(tree, method='xml', pretty_print=True))

def _is_target_rect(elem, notebooks, config):
    return (
        elem.getprevious() is not None and
        #elem.getprevious().tag == SVG_RECT and
        len(elem.text) > 0 and
        _find_matching_notebook(notebooks, elem.text, config) is not None)

def _find_matching_notebook(notebooks, id, config):
    """ノードの表示名に対応したノートブックを探す

    Args:
        notebooks (List[str]): ノートブック名のリスト
        title (str): タスクの機能ID
        config (dict[str, dict]): IDをキーとした辞書

    Returns:
        str: ノートブック名
    """
    # IDからノートブック名(拡張子無し)を取得
    title = config.get(id, "")
    if title:
        title = title['name']
    else:
        return
    # 対応したノートブックを探す
    for nb in notebooks:
        if nb.startswith(title):
            return nb

def _update_notebook_link(nb_headers, nb_name, value):

    if not value['is_link']:
        nb_headers[nb_name]['path'] = ""
    elif value['init_nb']:
        link = nb_headers[nb_name]['path']
        nb_headers[nb_name]['path'] = link + "?init_nb=true"
    return nb_headers

def parse_headers(nb_path: Path):
    nb = read(str(nb_path), as_version=NO_CONVERT)

    # Notebookのセルからmarkdownの部分を取り出し、行ごとのリストにする
    lines = [
        line.strip()
        for line in chain.from_iterable(
            cell['source'].split('\n')
            for cell in nb.cells
            if cell['cell_type'] == 'markdown'
        )
        if len(line.strip()) > 0 and not line.startswith('---')
    ]

    # h1, h2 の行とその次行の最初の１文を取り出す
    headers = [
        (' '.join(line0.split()[1:]),
            line1.split("。")[0] if line1 is not None else '')
        for (line0, line1) in zip_longest(lines, lines[1:])
        if line0.startswith('# ') or line0.startswith('## ')
    ]
    # 最初の見出しはtitle, 残りはheadersとして返す
    return {
        'path': str(nb_path),
        'title': {
            'text': _to_title_text(nb_path, headers[0][0]),
            'summary': headers[0][1],
        },
        'headers': [
            {
                'text': text,
                'summary': (
                    summary if not re.match(r'(?:#|!\[)', summary) else ''),
            }
            for (text, summary) in headers[1:]
            if text[0].isdigit()
        ],
    }

def _to_title_text(nb_path, text):
    no = nb_path.name.split('-')[0]
    title = text if not text.startswith('About:') else text[6:]
    return f'{title}'

def _get_notebook_headers(nb_dir: Path):
    return dict([
        (nb.name, parse_headers(nb))
        for nb in nb_dir.glob("**/*.ipynb")
    ])

def notebooks_toc(nb_dir):
    nb_headers = sorted(
        _get_notebook_headers(Path(nb_dir)).items(),
        key=lambda x: x[0])

    return "\n".join(chain.from_iterable([
        [
            f'* [{headers["title"]["text"]}]({nb_dir}/{str(nb)})'
        ] + list(chain.from_iterable([
            [
                f'    - {header["text"]}',
                (f'      - {header["summary"]}'
                    if len(header["summary"]) > 0 else ''),
            ]
            for header in headers['headers']
        ]))
        for nb, headers in nb_headers
    ]))

def _embed_info_in_one_rect(elem, nb_headers, nb_name, current_dir):
    headers = nb_headers[nb_name]
    nb_file = nb_headers[nb_name]['path']
    if nb_file:
        nb_file = file.relative_path(nb_file, current_dir).replace("../", "./../")
    childpos = elem.getparent().index(elem)
    parent_elem = elem.getparent()
    title = headers['title']['text']
    insert_title(elem, parent_elem, childpos, title, str(nb_file))

def insert_title(elem, parent_elem, childpos, title, link):
    if link:
        font_color = title_font_color
    else:
        font_color = text_font_color

    text_elem = elem
    text_elem.attrib['fill'] = font_color
    text_elem.attrib['font-family'] = 'sans-serif'
    text_elem.attrib['font-size'] = str(title_font_size)
    text_elem.attrib['font-weight'] = 'bold'

    text_elems = [elem]

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