
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class QScrollAreaForCollapsibleBoxes(QScrollArea):

    def __init__(self,
            parent : QWidget = None,
            ):

        super().__init__(parent)

        self.container_widget = QWidget()
        self.setWidget(self.container_widget)
        self.setWidgetResizable(True)
        #self.setFrameShape(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def set_contents_layout(self, layout:QBoxLayout):

        lay = self.container_widget.layout()
        del lay
        self.container_widget.setLayout(layout)
        self.adjust_scroll_area_width()

    def adjust_scroll_area_width(self):

        container_widget_width = self.container_widget.sizeHint().width()
        scroll_bar_width = self.verticalScrollBar().sizeHint().width()
        self.setFixedWidth(container_widget_width + scroll_bar_width + 5)
        
    def wheelEvent(self, event:QWheelEvent):

        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            self.horizontalScrollBar().wheelEvent(event)
            
        else:
            self.verticalScrollBar().wheelEvent(event)
