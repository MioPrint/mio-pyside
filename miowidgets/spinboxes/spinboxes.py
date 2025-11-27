
import sys 
import numpy as np 

from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
from PySide6.QtGui import QValidator

class QInt64SpinBox(QDoubleSpinBox):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        #self.setRange(-9223372036854775808, 9223372036854775807)
        self.setRange(-2**63, 2**63-1)
        self.setDecimals(0)
        self.setSingleStep(1)

    def valueFromText(self, text:str) -> int:

        try:
            return int(float(text))
        except ValueError:
            return -1

    def textFromValue(self, value:int) -> str:

        return str(int(value))

    def validate(self, text:str, pos:int):

        if text == "":
            return (QValidator.State.Intermediate, text, pos)
        try:
            val = int(float(text))
            if self.minimum() <= val <= self.maximum():
                return (QValidator.State.Acceptable, text, pos)
            else:
                return (QValidator.State.Invalid, text, pos)
        except ValueError:
            return (QValidator.State.Invalid, text, pos)
    
    def value(self):

        return int(super().value())

class QAnyDecimalDoubleSpinBox(QDoubleSpinBox):
    
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setDecimals(16)
        self.setRange(-sys.float_info.max, sys.float_info.max)

    def validate(self, text, pos):
        
        if text == "":
            return (QValidator.State.Intermediate, text, pos)
        try:
            float(text)
            return (QValidator.State.Acceptable, text, pos)
        except ValueError:
            return (QValidator.State.Invalid, text, pos)

    def textFromValue(self, value):
        return str(value)

    def valueFromText(self, text):
        return float(text)

class QNumpyUIntSpinBox(QDoubleSpinBox):

    def __init__(self, dtype:np.dtype, parent=None, *args, **kwargs):
    
        super().__init__(parent, *args, **kwargs)

        self.dtype = dtype

        self.setRange(0, np.iinfo(dtype).max)
        self.setDecimals(0)
        
    def textFromValue(self, value):

        value = self.dtype.type(value)

        return str(value)
    
    def valueFromText(self, text: str):

        try:
            value = self.dtype.type(int(text))

            if 0 <= value <= np.iinfo(self.dtype).max:
                return value
            
            else:
                self.setValue(self.minimum())  # Reset to minimum if out of range
                return self.minimum()

        except ValueError:

            return self.minimum()  # Reset to minimum on invalid input
        
    def numpyUintValue(self):
        
        return self.dtype.type(self.value())

class QNumpyInt64SpinBox(QDoubleSpinBox):

    def __init__(self, dtype:np.dtype, parent=None, *args, **kwargs):
    
        super().__init__(parent, *args, **kwargs)

        self.dtype = dtype

        min_value = np.iinfo(self.dtype).min
        max_value = np.iinfo(self.dtype).max
        self.setRange(min_value, max_value)
        self.setDecimals(0)
        
    def textFromValue(self, value):

        value = self.dtype.type(value)

        return str(value)
    
    def valueFromText(self, text: str):

        try:
            value = self.dtype.type(int(text))

            if np.iinfo(self.dtype).min <= value <= np.iinfo(self.dtype).max:
                return value
            
            else:
                self.setValue(self.minimum())  # Reset to minimum if out of range
                return self.minimum()

        except ValueError:

            return self.minimum()  # Reset to minimum on invalid input
        
    def numpyIntValue(self):
        
        return self.dtype.type(self.value())


