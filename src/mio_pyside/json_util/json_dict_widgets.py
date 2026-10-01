
import json, logging

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from collections import namedtuple

from ..config import GLOBAL_WORKING_DIR, WorkingDir
from ..buttons import QLoadFileButton, QSaveFileButton
from ..utils import wait_cursor

DictWidgetElement = namedtuple(
    typename= "WidgetElement", 
    field_names= ['default', 'items', 'min', 'max', 'enabled'], 
    defaults= [None, [], None, None, True],
    )

class QJsonArrayWidget(QWidget):

    array_changed = Signal(list)

    def __init__(self,
            element:DictWidgetElement,
            parent:QWidget= None,
            ):
        
        super().__init__(parent)

        self.element = element
        self.groupbox_main = QGroupBox("Array")
        self.widgets_list:list[QWidget] = []
        self.remove_buttons_list:list[QPushButton] = []
        self.values_list = []
        self.value_type = None

        for e, value in enumerate(self.element.default):
            if e == 0:
                self.value_type = type(value)
                continue
            if not isinstance(value, self.value_type):
                valueerror_message = f"Values in an array / list have to be of the same type!"
                raise ValueError(valueerror_message)

        if self.element.items and self.element.default and self.value_type != str:
            valueerror_message = f"If items are provided, values must be strings!"
            raise ValueError(valueerror_message)

        self.init_widgets(values_list= self.element.default)
        self.init_layout()

    def init_widgets(self, values_list:list):

        if self.element.items:

            layout_groupbox = QVBoxLayout(self.groupbox_main)
            layout_groupbox.setSpacing(3)

            for item in self.element.items:

                widget_element = QCheckBox(str(item), parent=self.groupbox_main)
                widget_element.setChecked(item in values_list)
                widget_element.clicked.connect(self.on_widget_changed)

                layout_groupbox.addWidget(widget_element)
                self.widgets_list.append(widget_element)

        else: 

            layout_groupbox = QGridLayout(self.groupbox_main)
            layout_groupbox.setSpacing(3)
            layout_groupbox.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

            self.button_add_item = QPushButton("Add", parent=self.groupbox_main)
            self.button_add_item.clicked.connect(self.add_widget)

            layout_groupbox.addWidget(self.button_add_item, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
            
            for e, value in enumerate(values_list):

                self.blockSignals(True)
                widget_element = self.add_widget()
                self.blockSignals(False)

                widget_element.blockSignals(True)
               
                if isinstance(widget_element, QLineEdit):
                    widget_element.setText(value)
                elif isinstance(widget_element, QCheckBox):
                    widget_element.setChecked(value)
                elif isinstance(widget_element, QSpinBox):
                    widget_element.setValue(value)
                elif isinstance(widget_element, QDoubleSpinBox):
                    widget_element.setValue(value)
                else:
                    valueerror_message = f"Unsupported value type: {self.value_type}"
                    raise ValueError(valueerror_message)

                widget_element.blockSignals(False)
        
        self.update_values_list()

    def init_layout(self):

        layout_main_v = QVBoxLayout(self)
        layout_main_v.addWidget(self.groupbox_main)
        layout_main_v.setContentsMargins(0,0,0,0)

    def on_widget_changed(self, *args, **kwargs):

        self.update_values_list()

        self.array_changed.emit(self.values_list)

    @wait_cursor
    def update_values_list(self):

        self.values_list = []

        if self.element.items:

            self.values_list = [widget_element.text() for widget_element in self.widgets_list if widget_element.isChecked()]

        else:

            for widget_element in self.widgets_list:

                if isinstance(widget_element, QLineEdit):
                    self.values_list.append(widget_element.text())

                elif isinstance(widget_element, QCheckBox):
                    self.values_list.append(widget_element.isChecked())

                elif isinstance(widget_element, QSpinBox):
                    self.values_list.append(widget_element.value())

                elif isinstance(widget_element, QDoubleSpinBox):
                    self.values_list.append(widget_element.value())

                else:
                    valueerror_message = f"Unsupported widget type: {type(widget_element)}"
                    raise ValueError(valueerror_message)

    def add_widget(self) -> QWidget:

        if self.value_type == str:
            widget_element = QLineEdit(parent=self.groupbox_main)
            widget_element.editingFinished.connect(self.on_widget_changed)

        elif self.value_type == bool:
            widget_element = QCheckBox(parent=self.groupbox_main)
            widget_element.clicked.connect(self.on_widget_changed)
        
        elif self.value_type == int:
            widget_element = QSpinBox(parent=self.groupbox_main)
            if self.element.min is not None and self.element.max is not None:
                widget_element.setRange(self.element.min, self.element.max)
            widget_element.valueChanged.connect(self.on_widget_changed)

        elif self.value_type == float:
            widget_element = QDoubleSpinBox(parent=self.groupbox_main)
            if self.element.min is not None and self.element.max is not None:
                widget_element.setRange(self.element.min, self.element.max)
            widget_element.valueChanged.connect(self.on_widget_changed)

        else:
            valueerror_message = f"Unsupported value type: {self.value_type}"
            raise ValueError(valueerror_message)

        button_remove_item = QPushButton("Remove", parent=self.groupbox_main)
        button_remove_item.clicked.connect(lambda: self.remove_widget( widget_element ))

        row_position = len(self.widgets_list)
        
        layout_groupbox:QGridLayout = self.groupbox_main.layout()
        layout_groupbox.addWidget(QLabel(f"{row_position}:"), row_position+1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        layout_groupbox.addWidget(widget_element, row_position+1, 1)
        layout_groupbox.addWidget(button_remove_item, row_position+1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.widgets_list.append(widget_element)
        self.remove_buttons_list.append(button_remove_item)

        self.on_widget_changed()

        return widget_element

    def remove_widget(self, widget_to_remove:QWidget):

        index_of_widget_to_remove = self.widgets_list.index(widget_to_remove)
        self.widgets_list.pop(index_of_widget_to_remove)
        self.remove_buttons_list.pop(index_of_widget_to_remove)

        new_layout_groupbox = QGridLayout()
        new_layout_groupbox.setSpacing(3)
        new_layout_groupbox.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.button_add_item.setParent(self.groupbox_main)
        new_layout_groupbox.addWidget(self.button_add_item, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        
        for e, (widget_element, button_remove_item) in enumerate(zip(self.widgets_list, self.remove_buttons_list)):

            widget_element.setParent(self.groupbox_main)
            button_remove_item.setParent(self.groupbox_main)

            new_layout_groupbox.addWidget(QLabel(f"{e}:"), e+1, 0, alignment=Qt.AlignmentFlag.AlignRight)
            new_layout_groupbox.addWidget(widget_element, e+1, 1)
            new_layout_groupbox.addWidget(button_remove_item, e+1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        
        old_layout_groupbox:QGridLayout = self.groupbox_main.layout()
        QWidget().setLayout(old_layout_groupbox)
        self.groupbox_main.setLayout(new_layout_groupbox)

        self.on_widget_changed()

    def set_values_list(self, values_list:list):

        old_layout_groupbox:QGridLayout = self.groupbox_main.layout()
        QWidget().setLayout(old_layout_groupbox)

        self.widgets_list:list[QWidget] = []
        self.remove_buttons_list:list[QPushButton] = []

        self.init_widgets(values_list= values_list)

class QJsonDictWidget(QWidget):

    dict_changed = Signal(dict)

    def __init__(self,
            init_dict:dict,
            default_file_name:str= "settings.json",
            local_working_dir:WorkingDir= None,
            parent:QWidget= None,
            *args, **kwargs
            ):
        
        super().__init__(parent=parent, *args, **kwargs)

        self.init_dict = init_dict
        self.default_file_name = default_file_name
        self._local_working_dir = local_working_dir

        self.widgets_dict = {}
        self.values_dict = {}

        self.init_widgets()
        self.init_layout()

        self.update_values_dict()

    def init_widgets(self):

        self.button_load_values_from_json_file = QLoadFileButton(
            target_extension='.json',
            local_working_dir=self._local_working_dir,
            button_text= "Load from JSON file",
            parent= self,
            )
        self.button_load_values_from_json_file.file_abspath_selected.connect(self.load_from_file)

        self.button_save_values_to_json_file = QSaveFileButton(
            default_file_name= self.default_file_name,
            target_extension='.json',
            local_working_dir=self._local_working_dir,
            button_text= "Save to JSON file",
            parent= self,
        )
        self.button_save_values_to_json_file.file_abspath_selected.connect(self.save_to_file)

        self.container_widget, self.widgets_dict = self._init_widgets_recursively(
            init_dict= self.init_dict,
            parent= self,
            )

    def _init_widgets_recursively(self, 
            init_dict:dict[str,DictWidgetElement|dict], 
            group_key:str= "Dict Widget",
            parent:QWidget= None,
            ) -> tuple[QWidget,dict]:

        widgets_dict = {}

        new_parent = QWidget() if parent == self else QGroupBox("Object")

        form_layout_element = QFormLayout(new_parent)
        form_layout_element.setSpacing(5)

        for key, value in init_dict.items():

            if isinstance(value, dict):

                container_widget, container_widgets_dict = self._init_widgets_recursively(
                    init_dict= value,
                    group_key= key,
                    parent= new_parent,
                    )
                
                widgets_dict[key] = container_widgets_dict
                
                form_layout_element.addRow(key, container_widget)

            elif isinstance(value, DictWidgetElement):

                if isinstance(value.default, str) and value.items:
                    widget_element = QComboBox(parent=new_parent)
                    widget_element.addItems(value.items)
                    widget_element.setCurrentText(value.default)
                    widget_element.setEnabled(value.enabled)
                    widget_element.currentIndexChanged.connect(self.on_widget_changed)
                
                elif isinstance(value.default, str):
                    widget_element = QLineEdit(parent=new_parent)
                    widget_element.setText(value.default)
                    widget_element.setEnabled(value.enabled)
                    widget_element.editingFinished.connect(self.on_widget_changed)

                elif isinstance(value.default, bool):
                    widget_element = QCheckBox(parent=new_parent)
                    widget_element.setChecked(value.default)
                    widget_element.setEnabled(value.enabled)
                    widget_element.clicked.connect(self.on_widget_changed)
                
                elif isinstance(value.default, int):
                    widget_element = QSpinBox(parent=new_parent)
                    if value.min is not None and value.max is not None:
                        widget_element.setRange(value.min, value.max)
                    widget_element.setValue(value.default)
                    widget_element.setEnabled(value.enabled)
                    widget_element.valueChanged.connect(self.on_widget_changed)

                elif isinstance(value.default, float):
                    widget_element = QDoubleSpinBox(parent=new_parent)
                    widget_element.setDecimals(8)
                    widget_element.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
                    if value.min is not None and value.max is not None:
                        widget_element.setRange(value.min, value.max)
                    widget_element.setValue(value.default)
                    widget_element.setEnabled(value.enabled)
                    widget_element.valueChanged.connect(self.on_widget_changed)

                elif isinstance(value.default, list):
                    widget_element = QJsonArrayWidget(element= value, parent=new_parent)
                    widget_element.setEnabled(value.enabled)
                    widget_element.array_changed.connect(self.on_widget_changed)
                
                else:
                    valueerror_message = f"Unsupported default type: {type(value.default)}"
                    raise ValueError(valueerror_message)
                
                form_layout_element.addRow(key, widget_element)

                widgets_dict[key] = widget_element

            else:
                valueerror_message = f"Unsupported value type: {type(value)}"
                raise ValueError(valueerror_message)

        return new_parent, widgets_dict

    def init_layout(self):

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_load_values_from_json_file)
        layout_buttons.addWidget(self.button_save_values_to_json_file)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.container_widget)

        layout_main_v = QVBoxLayout()
        layout_main_v.addLayout(layout_buttons)
        layout_main_v.addWidget(scroll_area)
        layout_main_v.setContentsMargins(1,1,1,1)

        self.setLayout(layout_main_v)

    def on_widget_changed(self, *args, **kwargs):

        self.update_values_dict()

        self.dict_changed.emit(self.values_dict)

    @wait_cursor
    def update_values_dict(self) -> dict:

        self.values_dict = self._get_values_dict_recursively(
            widgets_dict= self.widgets_dict,
            )
        
    def _get_values_dict_recursively(self, 
            widgets_dict:dict,
            ) -> dict:

        values_dict = {}

        for key, widget_element in widgets_dict.items():

            if isinstance(widget_element, dict):
                values_dict[key] = self._get_values_dict_recursively(widget_element)
            
            elif isinstance(widget_element, QLineEdit):
                values_dict[key] = widget_element.text()

            elif isinstance(widget_element, QComboBox):
                values_dict[key] = widget_element.currentText()

            elif isinstance(widget_element, QCheckBox):
                values_dict[key] = widget_element.isChecked()

            elif isinstance(widget_element, QSpinBox):
                values_dict[key] = widget_element.value()

            elif isinstance(widget_element, QDoubleSpinBox):
                values_dict[key] = widget_element.value()
            
            elif isinstance(widget_element, QJsonArrayWidget):
                values_dict[key] = widget_element.values_list

            else:
                valueerror_message = f"Unsupported widget type: {type(widget_element)}"
                raise ValueError(valueerror_message)
        
        return values_dict

    @wait_cursor
    def set_widget_values(self, values_dict:dict):
        
        self._set_widget_values_recursively(
            values_dict= values_dict,
            widgets_dict= self.widgets_dict,
            )

        self.update_values_dict()

        self.dict_changed.emit(self.values_dict)

    def _set_widget_values_recursively(self, 
            values_dict:dict, 
            widgets_dict:dict,
            ):

        widget_keys = widgets_dict.keys()
        value_keys = values_dict.keys()

        for key in widget_keys - value_keys:
            logging.warning(f"Key '{key}' from widget structure not found in values dictionary.")

        for key in widget_keys & value_keys:
            widget_element = widgets_dict[key]
            value = values_dict[key]

            if isinstance(widget_element, dict):
                if isinstance(value, dict):
                    self._set_widget_values_recursively(value, widget_element)
                else:
                    logging.warning(f"Mismatched types for key '{key}': expected dict in values, got {type(value)}.")
            
            elif isinstance(widget_element, QLineEdit):
                widget_element.setText(str(value))
            
            elif isinstance(widget_element, QComboBox):
                if widget_element.findText(str(value)) != -1:
                    widget_element.setCurrentText(str(value))
                else:
                    logging.warning(f"Value '{value}' not found in QComboBox for key '{key}'.")
            
            elif isinstance(widget_element, QCheckBox):
                widget_element.setChecked(bool(value))
            
            elif isinstance(widget_element, (QSpinBox, QDoubleSpinBox)):
                widget_element.setValue(value)

            elif isinstance(widget_element, QJsonArrayWidget):
                widget_element.set_values_list(value)
            
            else:
                logging.warning(f"Unsupported widget type: {type(widget_element)} for key '{key}'")

    def load_from_file(self, file_abspath: str):
        
        with open(file_abspath, 'r') as json_file:
            values_dict = json.load(json_file)

        self.set_widget_values(values_dict)

    def save_to_file(self, file_abspath: str):

        self.update_values_dict()
        
        with open(file_abspath, 'w') as json_file:
            json.dump(self.values_dict, json_file, indent=4)
