"""PDFファイルのメタデータに関するモジュールです。

PDFファイルのメタデータの取得や更新を行う機能を記載しています。

"""
import os

import panel as pn
import pikepdf
from IPython.core.display import Javascript
from IPython.display import display

from library.task_director import TaskDirector
from library.utils.config import message as msg_config
from library.utils.widgets import Button, MessageBox



class PdfMetaData(TaskDirector):
    """PDFのメタデータを扱うクラスです。

    Attributes:
        instance:
            author_input(pn.widgets.TextInput): 著者名を入れる用のテキストボックス
            title_input(pn.widgets.TextInput): タイトルを入れる用のテキストボックス
            subject_input(pn.widgets.TextInput): サブタイトルを入れる用のテキストボックス
            output_message(MessageBox): 表示用のメッセージボックス
            form_section(pn.WidgetBox): フォームやメッセージを表示するためのセクション
            pdf_select(pn.widgets.Select): pdfを選択するためのセレクトボックス

    """

    def __init__(self, working_path: str, notebook_name: str):
        """PdfMetaDataのコンストラクタです。

        Args:
            working_path (str): 実行ノートブックパス
            notebook_name (str): 実行ノートブック名

        """
        super().__init__(working_path, notebook_name)

        pn.extension()
        self.author_input = pn.widgets.TextInput(name='Author', value='')
        self.title_input = pn.widgets.TextInput(name='Title', value='')
        self.subject_input = pn.widgets.TextInput(name='subject', value='')


        self.output_message = MessageBox()
        self.output_message.width = 900

        self.form_section = pn.WidgetBox()

    def generate_pdf_metadata_form(self, dir_path: str):
        """pdfを選択してメタデータをと登録するためのフォームを生成します。

        Args:
            dir_path (str): pdfファイルの保存されているディレクトリ名

        """
        self.doing_task()

        self.log.info('呼び出されました')
        form = pn.Column(self.author_input, self.title_input)

        pdf_files = self.get_pdf_files(dir_path)
        pdf_files[msg_config.get('form', 'selector_default')] = 'default'
        self.pdf_select = pn.widgets.Select(name=msg_config.get('register_paper_metadata', 'form_title'), options=pdf_files, value= "default")
        self.pdf_select.param.watch(self.on_select_change, 'value')

        registrate_button_title = msg_config.get('form', 'registrate')
        registrate_button = Button(width=500, disabled=True)
        registrate_button.set_looks_init(registrate_button_title)
        registrate_button.on_click(self.on_click_registrate)

        self.done_task()
        self.form_section.append(self.pdf_select)
        self.form_section.append(form)
        self.form_section.append(registrate_button)
        display(self.form_section)
        display(Javascript('IPython.notebook.save_checkpoint();'))

    def get_pdf_files(self, dir_path: str) -> dict:
        """指定されたディレクトリ内のpdfファイルを取得するメソッドです。

        Args:
            dir_path (str): pdfファイルを取得するディレクトリ名

        Returns:
            dict: キーがファイル名、値がファイルまでのフルパスの辞書
        """
        # ファイル名だけを表示するためにファイル名リストを作成
        pdf_files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
        # セレクトボックス用にファイル名とフルパスの辞書を作成
        return {file: os.path.join(dir_path, file) for file in pdf_files}

    def on_select_change(self, event):
        """セレクトボックスでpdfが選択された際にメタデータを取得するメソッドです。"""

        # ファイル選択後、絶対パスを使用して開く
        pdf_path = self.pdf_select.value  # ここでファイルの絶対パスが渡される
        with pikepdf.open(pdf_path) as pdf:
            # docinfo を使用してメタデータを取得
            metadata = pdf.docinfo
            author = metadata.get('/Author', '')
            title = metadata.get('/Title', '')
            subject = metadata.get('/Subject', '')

            self.author_input.value = author
            self.title_input.value = title
            self.subject_input.value = subject

        if not pdf_path == msg_config.get('form', 'selector_default'):
            self.registrate_button.disabled = False
        else:
            self.author_input.value = ""
            self.title_input.value = ""
            self.subject_input.value = ""

    def on_click_registrate(self, event):
        """登録ボタンが押下された際にメタデータを入力値で更新するメソッドです。"""

        self.log.info("クリックされました")
        author = self.author_input.value
        title = self.title_input.value
        subject = self.subject_input.value

        # 保存時も絶対パスを使用
        pdf_path = self.pdf_select.value
        with pikepdf.open(pdf_path) as pdf:
            pdf.docinfo.update({
                '/Author': author,
                '/Title': title,
                '/Subject': subject
            })
        pdf.save(pdf_path)  # 修正したファイルの場所に保存

        self.output_message.update_success("成功しました")
        self.form_section.append(self.output_message)
