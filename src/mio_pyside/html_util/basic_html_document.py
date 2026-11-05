
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from PySide6.QtWebEngineWidgets import QWebEngineView

import os, logging

from ..settings import QMioAppSettingsManager
from ..buttons import QLoadFileButton, QSaveFileButton
from .content_list_functions import get_html_string_from_content_list

class QBasicHtmlDocumentWidget(QWidget):

    html_updated = Signal(str)

    def __init__(self,
            settings_manager : QMioAppSettingsManager,
            parent           : QWidget = None,
            *args, **kwargs
            ):

        super().__init__(
            parent = parent, 
            *args, **kwargs
            )

        self._settings_manager = settings_manager

        self.html_path = ""
        self.html_string = ""

        self.init_widgets()
        self.init_layout()
    
    def init_widgets(self):

        self.web_engine_view_widget = QWebEngineView(parent=self)
        self.web_engine_view_widget.loadFinished.connect(self.on_load_finished)

        self.label_html_path = QLabel(self.html_path)
        self.label_html_path.setWordWrap(True)

        self.button_load_html_file = QLoadFileButton(
            settings_manager   = self._settings_manager,
            button_text        = "Load from .html",
            update_working_dir = False,
            target_extension   = '.html',
            parent             = self,
            )
        self.button_load_html_file.file_abspath_selected.connect(self.load_html_file)

        self.button_save_html_file = QSaveFileButton(
            settings_manager   = self._settings_manager,
            button_text        = "Save to .html",
            update_working_dir = False,
            target_extension   = '.html',
            default_file_name  = "page",
            parent             = self,
            )
        self.button_save_html_file.file_abspath_selected.connect(self.save_html_file)

        self.button_reload_html_file = QPushButton('', parent=self)
        self.button_reload_html_file.clicked.connect(self.on_button_reload_html_file_click)
        self.button_reload_html_file.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)))
        
    def init_layout(self):

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.label_html_path, 1)
        layout_buttons.addStretch(0)
        layout_buttons.addWidget(self.button_save_html_file, alignment=Qt.AlignmentFlag.AlignRight)
        layout_buttons.addWidget(self.button_load_html_file, alignment=Qt.AlignmentFlag.AlignRight)
        layout_buttons.addWidget(self.button_reload_html_file, alignment=Qt.AlignmentFlag.AlignRight)
        layout_buttons.setAlignment(Qt.AlignmentFlag.AlignBottom)
        layout_buttons.setContentsMargins(5,5,5,5)

        layout_main_v = QVBoxLayout()
        layout_main_v.addWidget(self.web_engine_view_widget,1)
        layout_main_v.addLayout(layout_buttons)
        layout_main_v.setContentsMargins(0,0,0,0)
        self.setLayout(layout_main_v)

    @Slot()
    def on_button_reload_html_file_click(self):

        if self.html_path == '':
            return

        if self.html_string == '':
            return
        
        self.refresh_html_content()

    @Slot(str)
    def load_html_file(self, html_path:str):

        self.html_path = html_path
        
        self.label_html_path.setText(self.html_path)
        
        with open(self.html_path, 'r', encoding='utf-8') as file:
            self.html_string = file.read()

        self.set_html_file(self.html_path)

        self.html_updated.emit(self.html_string)

    @Slot(str)
    def save_html_file(self, html_path:str):

        self.html_path = html_path

        with open(self.html_path, 'w', encoding='utf-8') as file:
            file.write(self.html_string)

        self.set_html_file(self.html_path)

    @Slot(bool)
    def on_load_finished(self, success:bool):

        if not success:

            fail_string = f' HTML content larger than 2MB, can not display. Try saving it as a file'

            logging.info(fail_string)

            fail_html_str = get_html_string_from_content_list([fail_string])

            self.web_engine_view_widget.setHtml(fail_html_str)

    def set_html_string(self, html_string, html_path):
        
        self.html_string = html_string
        self.html_path = html_path
        self.label_html_path.setText(self.html_path)
        self.web_engine_view_widget.setHtml(self.html_string, baseUrl=QUrl.fromLocalFile(html_path))

    def set_html_file(self, html_path):

        self.html_path = html_path
        self.label_html_path.setText(self.html_path)
        self.web_engine_view_widget.setUrl(QUrl.fromLocalFile(self.html_path))

    def refresh_html_content(self):

        self.label_html_path.setText(self.html_path)
        self.web_engine_view_widget.setUrl(QUrl.fromLocalFile(self.html_path))

        self.html_updated.emit(self.html_string)
