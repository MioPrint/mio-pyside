
from functools import wraps
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QObject, Slot

def block_signals(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):

        if not isinstance(self, QObject):
            raise TypeError("Not a QObject!")

        self.blockSignals(True)
        try:
            return func(self, *args, **kwargs)
        finally:
            self.blockSignals(self.signalsBlocked())

    return wrapper

def wait_cursor(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            return func(self, *args, **kwargs)
        finally:
            QApplication.restoreOverrideCursor()
        
    return wrapper

