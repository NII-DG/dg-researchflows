"""PDFファイルのメタデータに関するモジュールです。

PDFファイルのメタデータの取得や更新を行う機能を記載しています。

"""
import os

import panel as pn
import pikepdf
from IPython.core.display import Javascript
from IPython.display import display

from config import message as msg_config
from setting import get_data_dir
from widgets import Button


class PdfMetaData:

    def generate_pdf_select_box(self, dir_path:str):

        pn.extension()
        self.author_input = pn.widgets.TextInput(name='Author', value='')
        self.title_input = pn.widgets.TextInput(name='Title', value='')
        self.subject_input = pn.widgets.TextInput(name='subject', value='')

        form = pn.Column(self.author_input, self.title_input)

        pdf_files = self.get_pdf_files(dir_path)

        self.pdf_select = pn.widgets.Select(name="Select a PDF file", options=pdf_files, value = msg_config.get('form', 'selector_default'))
        self.pdf_select.param.watch(self.on_select_change, 'value')

        self.registrate_button_title = msg_config.get('form', 'registrate')
        self.registrate_button = Button(width=500, disabled=True)
        self.registrate_button.set_looks_init(self.registrate_button_title)
        self.registrate_button.on_click(self.on_click_registrate)

        pn.extension()
        form_section = pn.WidgetBox()
        form_section.append(self.pdf_select)
        form_section.append(form)
        form_section.append(self.registrate_button)
        display(form_section)
        display(Javascript('IPython.notebook.save_checkpoint();'))

    def get_pdf_files(self, dir_path:str) -> list:

        pdf_files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
        return pdf_files

    def on_select_change(self, event):

        with pikepdf.open(self.pdf_select.value) as pdf:
            metadata = pdf.metadata
            author = metadata.get('/Author', '')
            title = metadata.get('/Title', '')
            subject = metadata.get('/Subject', '')

            self.author_input.value = author
            self.title_input.value = title
            self.subject_input.value = subject

        if not self.pdf_select.value == msg_config.get('form', 'selector_default'):
            self.registrate_button.disabled = False

        else:
            self.author_input.value = ""
            self.title_input.value = ""
            self.subject_input.value = ""

    def on_click_registrate(self, event):

        author = self.author_input.value
        title = self.title_input.value
        subject = self.subject_input.value

        with pikepdf.open(self.pdf_select.value) as pdf:
            pdf.metadata.update({
                '/Author': author,
                '/Title': title,
                '/Subject': subject
        })
        pdf.save(self.pdf_select.value)
