
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import mio_pyside

class QMioMainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(f"MioPrint")

        self._settings_manager = QMioAppSettingsManager_template()
        self.read_settings()

        self.init_widgets()
        self.init_layout()

        self.show()

    def init_widgets(self):

        pass

    def init_layout(self): 

        layout_main = QVBoxLayout()

        self.mainwidget = QWidget(parent=self)
        self.mainwidget.setLayout(layout_main)

        self.setCentralWidget(self.mainwidget)        

    def read_settings(self):

        self.restoreGeometry(self._settings_manager.window_geometry)
        self.restoreState(self._settings_manager.window_state)

    def write_settings(self):

        self._settings_manager.window_geometry = self.saveGeometry()
        self._settings_manager.window_state = self.saveState()

    def closeEvent(self, event:QCloseEvent):

        self.write_settings()
        return super().closeEvent(event)

class QMioAppSettingsManager_template(mio_pyside.QMioAppSettingsManager):

    def __init__(self):

        company_name = "MioPrint"
        app_name     = "MioApp"
        default_dir  = "~/"

        super().__init__(
            company_name = company_name, 
            app_name     = app_name,
            default_dir  = default_dir
            )
