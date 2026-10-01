
import base64, imghdr

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWebEngineWidgets import QWebEngineView

import numpy as np
import pandas as pd

from .basic_html_document import BasicHtmlDocumentWidget
from .content_list_functions import get_html_string_from_content_list

class ContentListHtmlDocumentWidget(BasicHtmlDocumentWidget):

    def __init__(self,
            parent:QWidget= None,
            *args, **kwargs
            ):

        super().__init__(
            parent= parent, 
            *args, **kwargs
            )

        self.html_content_list = []

    ### SETs ###

    @Slot(list)
    def set_html_content_list(self, html_content_list:list):

        self.html_content_list = html_content_list

        self.html_string = get_html_string_from_content_list(self.html_content_list)

        self.web_engine_view_widget.setHtml(self.html_string)

        self.html_updated.emit(self.html_string)
