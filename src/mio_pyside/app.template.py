
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import mio_pyside

def main(): 

    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)
    
    #print(QStyleFactory.keys()) # ['windows11', 'windowsvista', 'Windows', 'Fusion']
    app.setStyle("Fusion")
    style = QStyleFactory.create("Fusion")
    app.setPalette(style.standardPalette())
    
    app.setWindowIcon(QIcon(":/bluemarble.png"))
    
    mainwindow = QMainWindow()
    mainwindow.show()

    sys.exit(app.exec())






