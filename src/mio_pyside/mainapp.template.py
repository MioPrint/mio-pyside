
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import mio_pyside

def main(): 
    
    mio_pyside.GLOBAL_WORKING_DIR.setPath(QDir.currentPath())

    app = QApplication.instance()

    if app is None:
    
        app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    style = QStyleFactory.create("Fusion")
    app.setPalette(style.standardPalette())
    
    app.setWindowIcon(QIcon(":/bluemarble.png"))
    
    mainwindow = QMainWindow()

    sys.exit(app.exec())






