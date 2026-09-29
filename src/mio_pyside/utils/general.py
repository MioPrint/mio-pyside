
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

def delete_layout(layout:QLayout):

    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                delete_layout(item.layout())
