
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os

class QMioAppSettingsManager(QObject):

    working_dir_changed = Signal(str)
    settings_changed = Signal(str, object)

    _instance = None

    def __init__(self,
            company_name : str,
            app_name     : str,
            default_dir  : str = str(os.path.expanduser("~")),
            ):

        if self._initialized:
            return

        super().__init__()

        self.company_name = company_name
        self.app_name     = app_name
        self.app_settings = QSettings(company_name, app_name)
        self.default_dir  = default_dir

        self._initialized = True

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    # --- geometry --- #

    @property
    def window_geometry(self):

        return self.app_settings.value("window_geometry", QByteArray())

    @window_geometry.setter
    def window_geometry(self, value:QByteArray):

        self.app_settings.setValue("window_geometry", value)

    # --- window state --- #

    @property
    def window_state(self):

        return self.app_settings.value("window_state", QByteArray())

    @window_state.setter
    def window_state(self, value:QByteArray):

        self.app_settings.setValue("window_state", value)

    # --- working directory --- #

    @property
    def working_dir(self) -> str:

        if self.app_settings.value("working_dir") is None:
            self.app_settings.setValue("working_dir", self.default_dir)

        return self.app_settings.value("working_dir", self.default_dir, type=str)

    @working_dir.setter
    def working_dir(self, value:str):

        if not os.path.isdir(value):
            return

        new_working_dir = os.path.abspath(value)

        if self.working_dir != new_working_dir:

            self.app_settings.setValue("working_dir", new_working_dir)
            self.working_dir_changed.emit(new_working_dir)

    # --- get set settings --- #

    def get(self, key:str, default=None):

        if key == "working_dir":
            return self.working_dir

        if not self.app_settings.contains(key):
            self.app_settings.setValue(key, default)

        return self.app_settings.value(key, default)

    def set(self, key:str, value):

        self.app_settings.setValue(key, value)
        self.settings_changed.emit(key, value)
