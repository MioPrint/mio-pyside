
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class QMioMainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(f"")

        # --- Widgets --- #

        # --- Layout --- #

        layout_main = QVBoxLayout()

        self.mainwidget = QWidget(parent=self)
        self.mainwidget.setLayout(layout_main)

        self.setCentralWidget(self.mainwidget)
        self.show()











