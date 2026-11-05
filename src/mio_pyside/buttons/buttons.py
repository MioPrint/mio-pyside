
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
from typing import Any

from ..settings import QMioAppSettingsManager

class QLoadFolderButton(QPushButton):

    folder_abspath_selected = Signal(str)
    folder_QDir_selected = Signal(QDir)

    def __init__(self,
            settings_manager   : QMioAppSettingsManager,
            settings_key       : str  = "working_dir",
            settings_default   : Any  = None,
            button_text        : str  = "",
            update_working_dir : bool = False,
            parent             : QWidget = None,
            ):

        super().__init__( 
            text   = f" {button_text}", 
            parent = parent,
            )

        self._settings_manager   = settings_manager
        self._settings_key       = settings_key
        self._settings_default   = settings_default
        self._update_working_dir = update_working_dir

        self.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)))
        self.clicked.connect(self.on_button_click)

    @Slot()
    def on_button_click(self):

        target_dir = self._settings_manager.get(self._settings_key, self._settings_default)
        
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file_dialog.setDirectory(target_dir)

        if file_dialog.exec_():
            
            selected_directory = file_dialog.selectedFiles()
            selected_directory = os.path.normpath(selected_directory[0])

            self.folder_abspath_selected.emit(selected_directory)
            self.folder_QDir_selected.emit(QDir(selected_directory))

            if self._update_working_dir:
                self._settings_manager.set(self._settings_key, selected_directory)

class QLoadFileButton(QPushButton):

    file_abspath_selected = Signal(str)
    file_QFile_selected = Signal(QFile)

    def __init__(self,
            settings_manager   : QMioAppSettingsManager,
            settings_key       : str  = "working_dir",
            settings_default   : Any  = None,
            button_text        : str  = "",
            update_working_dir : bool = False,
            target_extension   : str|list[str] = "", # with a dot
            parent             : QWidget = None,
            ):

        super().__init__( 
            text   = f" {button_text}", 
            parent = parent,
            )

        self._settings_manager   = settings_manager
        self._settings_key       = settings_key
        self._settings_default   = settings_default
        self._update_working_dir = update_working_dir
        self._target_extension   = target_extension

        self.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)))
        self.clicked.connect(self.on_button_click)
    
    @Slot()
    def on_button_click(self):

        target_dir = self._settings_manager.get(self._settings_key, self._settings_default)
        
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file_dialog.setDirectory(target_dir)

        if self._target_extension:
            if isinstance(self._target_extension, str):
                name_filters = f"(*{self._target_extension})"
                file_dialog.setNameFilter(name_filters)
            elif isinstance(self._target_extension, list):
                name_filters = f"({", ".join([f'*{ext}' for ext in self._target_extension])})"
                file_dialog.setNameFilter(name_filters)

        if file_dialog.exec_():
            
            selected_file = file_dialog.selectedFiles()
            selected_file = os.path.normpath(selected_file[0])

            self.file_abspath_selected.emit(selected_file)
            self.file_QFile_selected.emit(QFile(selected_file))

            if self._update_working_dir:
                self._settings_manager.set(self._settings_key, os.path.dirname(selected_file))
                
class QSaveFileButton(QPushButton):

    file_abspath_selected = Signal(str)
    file_QSaveFile_selected = Signal(QSaveFile)

    def __init__(self,
            settings_manager   : QMioAppSettingsManager,
            settings_key       : str  = "working_dir",
            settings_default   : Any  = None,
            button_text        : str = "",
            update_working_dir : bool = False,
            target_extension   : str|list[str] = "", # with a dot
            default_file_name  : str = "",
            parent             : QWidget = None,
            ):

        super().__init__(
            text   = f" {button_text}", 
            parent = parent,
            )

        self._settings_manager   = settings_manager
        self._settings_key       = settings_key
        self._settings_default   = settings_default
        self._update_working_dir = update_working_dir
        self._target_extension   = target_extension
        self._default_file_name  = default_file_name

        self.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)))
        self.clicked.connect(self.on_button_click)
    
    @Slot()
    def on_button_click(self):

        target_dir = self._settings_manager.get(self._settings_key, self._settings_default)
        
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file_dialog.setDirectory(target_dir)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        if self._default_file_name:
            file_dialog.selectFile(f'{self._default_file_name}')

        if self._target_extension:
            if isinstance(self._target_extension, str):
                name_filters = f"(*{self._target_extension})"
                file_dialog.setNameFilter(name_filters)
                default_suffix = f'{self._target_extension[0]}'
                file_dialog.setDefaultSuffix(default_suffix)
            elif isinstance(self._target_extension, list):
                name_filters = f"({", ".join([f'*{ext}' for ext in self._target_extension])})"
                file_dialog.setNameFilter(name_filters)
                default_suffix = f"{self._target_extension}"
                file_dialog.setDefaultSuffix(default_suffix)

        if file_dialog.exec_():
            
            selected_file = file_dialog.selectedFiles()
            selected_file = os.path.normpath(selected_file[0])
            
            self.file_abspath_selected.emit(selected_file)
            self.file_QSaveFile_selected.emit(QSaveFile(selected_file))

            if self._update_working_dir:
                self._settings_manager.set(self._settings_key, os.path.dirname(selected_file))
