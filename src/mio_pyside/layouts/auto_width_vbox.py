
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class AutoWidthVBoxLayout(QVBoxLayout):

    """
    A custom layout that automatically adjusts the width of all child widgets
    based on the largest widget width.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setGeometry(self, rect):

        super().setGeometry(rect)

        # Find the maximum width of all widgets
        max_width = 0
        for i in range(self.count()):
            item = self.itemAt(i)
            if item and item.widget():
                max_width = max(max_width, item.widget().sizeHint().width())

        # Set the width of all widgets to the maximum width
        for i in range(self.count()):
            item = self.itemAt(i)
            if item and item.widget():
                item.widget().setFixedWidth(max_width)
