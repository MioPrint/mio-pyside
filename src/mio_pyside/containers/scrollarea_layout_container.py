
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class QScrollAreaLayoutContainer(QScrollArea):

    def __init__(self, 
            layout : QLayout,
            parent : QWidget = None,
            ):
        
        super().__init__(parent=parent)

        self.setWidgetResizable(True) 
        self.setFrameShape(QFrame.Shape.NoFrame)

        palette = self.palette() # QPalette()
        window_color = palette.color(QPalette.ColorRole.Window)
        window_color.setAlpha(0)
        palette.setColor(QPalette.ColorRole.Window, window_color)
        self.setPalette(palette)

        self.container_widget = QWidget(self)
        self.container_widget.setLayout(layout)
        self.setWidget(self.container_widget)

    def wheelEvent(self, event:QWheelEvent):

        step = 20

        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            #self.horizontalScrollBar().wheelEvent(event)
            if event.angleDelta().y() > 0:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - step)
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + step)
        
            if self.horizontalScrollBar().isVisible():
                event.accept()
        else:
            #self.verticalScrollBar().wheelEvent(event)
            if event.angleDelta().y() > 0:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - step)
            else:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + step)
    
            if self.verticalScrollBar().isVisible():
                event.accept()
