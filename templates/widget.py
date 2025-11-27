
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class QMioWidget(QWidget):

    def __init__(self,
            parent:QWidget= None
            ):

        super().__init__(
            parent= parent,
            )
        
        self.init_widgets()
        self.init_layout()

    def init_widgets(self):

        # --- Widgets --- #

        pass

    def init_layout(self):

        # --- Layout --- #

        layout_main_v = QVBoxLayout()
        
        self.setLayout(layout_main_v)

