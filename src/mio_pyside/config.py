
import os
from pathlib import Path
from PySide6.QtCore import QObject, QDir, Signal

class WorkingDir(QObject):

    changed = Signal(str)

    def __init__(self, 
            path:str= None
            ):
        
        super().__init__()

        self._dir = QDir(path) if path is not None else QDir(Path.home())

    def setPath(self, path:str):

        if path == self._dir.path():
            return

        self._dir.setPath(path)
        self.changed.emit(path)

    def abspath(self) -> str:

        return self._dir.absolutePath()
    
    def dir(self) -> QDir:

        return self._dir
    
    def refresh(self):

        self.changed.emit(self._dir.absolutePath())

    def parentDir(self):

        return QDir(self._dir.absoluteFilePath("..")).absolutePath()

GLOBAL_WORKING_DIR = WorkingDir()






