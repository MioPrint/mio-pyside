
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

class ElideLabel(QLabel):

    def __init__(self,
        text:str,
        elide_mode:Qt.TextElideMode= Qt.TextElideMode.ElideMiddle,
        max_width:int= 1000, 
        parent:QWidget= None,
        ):

        super(ElideLabel, self).__init__(text=text, parent=parent)

        self.elide_mode = elide_mode
        self.max_width = max_width

    def set_max_width(self, new_max_width:int):

        self.max_width = new_max_width

    def elideMode(self):

        return self.elide_mode

    def setElideMode(self, mode):
        
        if self.elide_mode != mode: # and mode != Qt.ElideNone:
        
            self.elide_mode = mode
            self.updateGeometry()

    def minimumSizeHint(self):
        
        return self.sizeHint()

    def sizeHint(self):

        hint = self.fontMetrics().boundingRect(self.text()).size()
        l, t, r, b = self.getContentsMargins()
        margin = self.margin() * 2
        
        w = min(self.max_width, hint.width()) + l + r + margin
        h = min(self.fontMetrics().height(), hint.height()) + t + b + margin

        if w < self.max_width:

            self.elide_mode = Qt.TextElideMode.ElideNone
            self.setElideMode(self.elide_mode)

        else:

            self.setElideMode(self.elide_mode)

        return QSize(w, h)

    def paintEvent(self, event):

        qp = QPainter(self)
        opt = QStyleOptionFrame()
        self.initStyleOption(opt)
        self.style().drawControl(QStyle.CE_ShapedFrame, opt, qp, self)
        l, t, r, b = self.getContentsMargins()
        margin = self.margin()

        try:
            # since Qt >= 5.11
            m = self.fontMetrics().horizontalAdvance('x') #/ 2 - margin
        except:
            m = self.fontMetrics().width('x') #/ 2 - margin

        m = int(m)

        r = self.contentsRect()

        qp.drawText(
            r, 
            self.alignment(), 
            self.fontMetrics().elidedText(
                self.text(), 
                self.elideMode(), 
                r.width()
                )
            )
