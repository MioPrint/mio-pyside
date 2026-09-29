
import os

from mio_pyside.config import GLOBAL_WORKING_DIR, WorkingDir

from PySide6.QtCore import Signal, Slot, QDir, QFile, QSaveFile
from PySide6.QtWidgets import QWidget, QPushButton, QStyle, QFileDialog
from PySide6.QtGui import QIcon

class QLoadFolderButton(QPushButton):

    folder_abspath_selected = Signal(str)
    folder_QDir_selected = Signal(QDir)

    def __init__(self,
            local_working_dir : WorkingDir= None,
            button_text : str= "",
            parent:QWidget= None
            ):
        
        button_text = " " + button_text if button_text else ""

        super().__init__( text= button_text, parent= parent )

        self._local_working_dir = local_working_dir 
        self.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)))
        self.clicked.connect(self.on_button_click)

    @Slot()
    def on_button_click(self):

        target_dir = self._local_working_dir.abspath() if self._local_working_dir is not None else GLOBAL_WORKING_DIR.abspath()

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file_dialog.setDirectory(target_dir)

        if file_dialog.exec_():
            
            selected_directory = file_dialog.selectedFiles()
            selected_directory = os.path.normpath(selected_directory[0])

            if self._local_working_dir is not None:
                self._local_working_dir.setPath(selected_directory)

            self.folder_abspath_selected.emit(selected_directory)
            self.folder_QDir_selected.emit(QDir(selected_directory))

class QLoadFileButton(QPushButton):

    file_abspath_selected = Signal(str)
    file_QFile_selected = Signal(QFile)

    def __init__(self,
            target_extension  : str|list= "",
            local_working_dir : WorkingDir= None,
            button_text : str= "",
            parent:QWidget= None
            ):
        
        button_text = " " + button_text if button_text else ""

        super().__init__( text= button_text, parent= parent )

        self._target_extension = target_extension
        self._local_working_dir = local_working_dir 
        self.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)))
        self.clicked.connect(self.on_button_click)
    
    @Slot()
    def on_button_click(self):

        target_dir = self._local_working_dir.abspath() if self._local_working_dir is not None else GLOBAL_WORKING_DIR.abspath()

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file_dialog.setDirectory(target_dir)

        if self._target_extension:
            file_dialog.setNameFilter(f'(*{self._target_extension})')

        if file_dialog.exec_():
            
            selected_file = file_dialog.selectedFiles()
            selected_file = os.path.normpath(selected_file[0])
            
            if self._local_working_dir is not None:
                self._local_working_dir.setPath(os.path.dirname(selected_file))

            self.file_abspath_selected.emit(selected_file)
            self.file_QFile_selected.emit(QFile(selected_file))

class QSaveFileButton(QPushButton):

    file_abspath_selected = Signal(str)
    file_QSaveFile_selected = Signal(QSaveFile)

    def __init__(self,
            default_file_name : str= "",
            target_extension  : str|list= "",
            local_working_dir : WorkingDir= None,
            button_text:str= "",
            parent:QWidget= None
            ):

        button_text = " " + button_text if button_text else ""

        super().__init__(text= button_text, parent= parent)

        self._default_file_name = default_file_name
        self._target_extension = target_extension
        self._local_working_dir = local_working_dir
        self.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)))
        self.clicked.connect(self.on_button_click)
    
    @Slot()
    def on_button_click(self):

        target_dir = self._local_working_dir.abspath() if self._local_working_dir is not None else GLOBAL_WORKING_DIR.abspath()

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file_dialog.setDirectory(target_dir)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        if self._default_file_name:
            file_dialog.selectFile(f'{self._default_file_name}')

        if self._target_extension:

            if isinstance(self._target_extension, list):

                #name_filters = f'(*{",*".join([ext for ext in self._target_extension])})'
                name_filters = f'(*)'
                default_suffix = f'{self._target_extension[0]}'

            elif isinstance(self._target_extension, str):

                name_filters = f'(*{self._target_extension})'
                default_suffix = f'{self._target_extension}'

            else:
                raise

            file_dialog.setNameFilter(name_filters)
            file_dialog.setDefaultSuffix(default_suffix)

        if file_dialog.exec_():
            
            selected_file = file_dialog.selectedFiles()
            selected_file = os.path.normpath(selected_file[0])
            
            if self._local_working_dir is not None:
                self._local_working_dir.setPath(os.path.dirname(selected_file))
            
            self.file_abspath_selected.emit(selected_file)
            self.file_QSaveFile_selected.emit(QSaveFile(selected_file))







