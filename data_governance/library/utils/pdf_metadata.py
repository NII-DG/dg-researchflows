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
    """PDFのメタデータを扱うクラスです。"""

    def __init__(self, working_path: str, notebook_name: str):
        super().__init__(working_path, notebook_name)

        pn.extension()
        self.author_input = pn.widgets.TextInput(name='Author', value='')
        self.title_input = pn.widgets.TextInput(name='Title', value='')
        self.subject_input = pn.widgets.TextInput(name='Subject', value='')

        self.output_message = MessageBox()
        self.output_message.width = 900

        self.form_section = pn.WidgetBox()

    def generate_pdf_metadata_form(self, dir_path: str):
        """pdfを選択してメタデータを登録するためのフォームを生成します。"""

        self.doing_task()

        form = pn.Column(self.author_input, self.title_input, self.subject_input)

        pdf_files = self.get_pdf_files(dir_path)
        pdf_files[msg_config.get('register_paper_metadata', 'form_title')] = 'default'  # Default
        self.pdf_select = pn.widgets.Select(name=msg_config.get('register_paper_metadata', 'form_name'), options=pdf_files, value="default")
        self.pdf_select.param.watch(self.on_select_change, 'value')

        registrate_button_title = msg_config.get('form', 'registrate')
        self.registrate_button = Button(width=500, disabled=True)
        self.registrate_button.set_looks_init(registrate_button_title)
        self.registrate_button.on_click(self.on_click_registrate)

        self.done_task()
        self.form_section.append(self.pdf_select)
        self.form_section.append(form)
        self.form_section.append(self.registrate_button)
        display(self.form_section)
        display(Javascript('IPython.notebook.save_checkpoint();'))

    def get_pdf_files(self, dir_path: str) -> dict:
        """指定されたディレクトリ内のpdfファイルを取得するメソッドです。"""
        pdf_files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
        return {file: os.path.join(dir_path, file) for file in pdf_files}

    def on_select_change(self, event):
        """PDFが選択された際にメタデータを取得するメソッドです。"""
        pdf_path = self.pdf_select.value
        if pdf_path != 'default':
            with pikepdf.open(pdf_path) as pdf:
                metadata = pdf.docinfo
                author = metadata.get('/Author', '')
                title = metadata.get('/Title', '')
                subject = metadata.get('/Subject', '')

            self.author_input.value = author
            self.title_input.value = title
            self.subject_input.value = subject

            self.registrate_button.disabled = False
        else:
            # デフォルト選択のときは入力欄をクリアし、ボタンを無効にする
            self.author_input.value = ""
            self.title_input.value = ""
            self.subject_input.value = ""
            self.registrate_button.disabled = True

    def on_click_registrate(self, event):
        """メタデータを登録するメソッドです。"""
        author = self.author_input.value
        title = self.title_input.value
        subject = self.subject_input.value

        pdf_path = self.pdf_select.value
        if pdf_path != 'default':
            with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
                # メタデータを直接更新
                self.log.info(f"Updating metadata for {pdf_path}")
                pdf.docinfo['/Author'] = author
                pdf.docinfo['/Title'] = title
                pdf.docinfo['/Subject'] = subject

                # PDFを保存（元のファイルに上書き）
                pdf.save(pdf_path)

            self.output_message.update_success(msg_config.get('register_paper_metadata','complete'))
            self.form_section.append(self.output_message)