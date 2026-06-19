
import sys, json
from dataclasses import dataclass, field, fields, asdict
import pandas as pd

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from ..buttons.buttons import QLoadFileButton, QSaveFileButton
from ..spinboxes.spinboxes import QInt64SpinBox, QAnyDecimalDoubleSpinBox
from ..config import GLOBAL_WORKING_DIR, WorkingDir
from ..utils.decorators import block_signals, wait_cursor

class QJsonTreeWidget(QWidget):

    contentEdited = Signal(object)
    selectionChanged = Signal(object)

    selectedJsonItemsChanged = Signal(list)

    def __init__(self,
            init_json_path      : str= "" ,
            local_working_dir   : WorkingDir= None,
            # --- Selection Settings --- #
            selectable_row          : bool= True, 
            single_selection        : bool= False,
            # --- Other --- #
            scrollbar_on_the_left   : bool= False,
            header_labels           : list= [],
            parent:QWidget= None
            ):

        super().__init__(
            parent= parent,
            )

        self.setMinimumSize(350, 200)

        self._init_json_path = init_json_path

        global GLOBAL_WORKING_DIR
        self._local_working_dir = local_working_dir if local_working_dir is not None else GLOBAL_WORKING_DIR

        self._selectable_row        = selectable_row
        self._single_selection      = single_selection 
        self._scrollbar_on_the_left = scrollbar_on_the_left
        self._header_labels         = header_labels

        # --- Model --- #

        self.model = QJsonModel(
            init_json_path   = self._init_json_path,
            selectable_row   = self._selectable_row,
            single_selection = self._single_selection,
            header_labels    = self._header_labels,
            parent= self
            )
        
        self.model.contentEdited.connect(self.contentEdited.emit)
        self.model.selectionChanged.connect(self.selectionChanged.emit)
        self.model.selectedJsonItemsChanged.connect(self.selectedJsonItemsChanged.emit)

        # --- View --- #

        self.tree = QJsonTreeView(parent= self)
        self.tree.setModel(self.model)

        # --- #

        #self.model.appendRow("Option A", "Alpha", checked=True)
        #self.model.appendRow("Option B", "Beta", checked=False)
        #self.model.appendRow("Option C", "Gamma", checked=True)
        
        # --- Layout --- #

        layout_main_v = QVBoxLayout()
        layout_main_v.addWidget(self.tree)
        layout_main_v.setContentsMargins(1,1,1,1)

        self.setLayout(layout_main_v)

    def reloadFromFile(self):
        self.model.loadFromJsonFile(self._init_json_path)
        self.tree.resizeColumnToContents(0)
    
    def loadDict(self, input_dict:dict):
        self.model.loadFromJsonDict(data=input_dict.copy())
        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)

class QJsonKeyItem(QStandardItem):

    def __init__(self,
            key        : str,
            dataType   : type,
            checkable  : bool = False,
            checked    : bool = False,
            editable   : bool = False,
            selectable : bool = True,
            enabled    : bool = True,
            isTable    : bool = False,
            isTransposed : bool = False,
            ):

        if dataType not in (str, bool, int, float, list, dict, type(None)):
            raise TypeError(key, dataType)

        super().__init__()
    
        self.setText(key)
        self.setData(key, Qt.ItemDataRole.EditRole)

        self.dataType = dataType

        self.setCheckable(checkable)
        if checkable: self.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.setEditable(editable)
        self.setSelectable(selectable)
        self.setEnabled(enabled)

        self.isTable = isTable
        self.isTransposed = isTransposed 

class QJsonItem(QStandardItem):

    def __init__(self,
            value      : str|int|float|bool|None,
            checkable  : bool = False,
            checked    : bool = False,
            editable   : bool = False,
            selectable : bool = True,
            enabled    : bool = True,
            ):
        
        super().__init__()

        if isinstance(value, str):
            self.setText(value)
            self.setData(value, Qt.ItemDataRole.EditRole)

        elif isinstance(value, bool):
            #self.setText(str(value))
            self.setData(value, Qt.ItemDataRole.EditRole)

        elif isinstance(value, (int,float)):
            self.setText(str(value))
            self.setData(value, Qt.ItemDataRole.EditRole)

        if value is None:
            pass

        self.setCheckable(checkable)
        if checkable: self.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.setEditable(editable)
        self.setSelectable(selectable)
        self.setEnabled(enabled)
        
class QJsonModel(QStandardItemModel):

    contentEdited = Signal(object)
    selectionChanged = Signal(object)

    selectedJsonItemsChanged = Signal(list)

    def __init__(self, 
            init_json_path   : str= "" ,
            selectable_row   : bool= True, 
            single_selection : bool= False,
            header_labels    : list[str]= [],
            transpose_arrays : bool= True,
            editable_keys    : bool= False,
            editable_values  : bool= True,
            parent= None,
            ):
    
        super().__init__(
            parent= parent,
            )

        self._selectable_row    = selectable_row
        self._single_selection  = single_selection
        self._header_labels     = header_labels if header_labels else ["", ""]
        self._column_count      = len(self._header_labels)
        self._transpose_arrays  = transpose_arrays
        self._editable_keys     = editable_keys
        self._editable_values   = editable_values

        self._last_index: QModelIndex | None = None

        if init_json_path:
            self.loadFromJsonFile(init_json_path)
    
    @wait_cursor
    def loadFromJsonFile(self, path:str):

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.loadFromJsonDict(data)

    @wait_cursor
    def loadFromJsonDict(self, data:dict):
        
        self.clear()
        
        self._column_count = len(self._header_labels)
        
        self.addItem("", data, None)
        
        if self._column_count > len(self._header_labels):
            self._header_labels = self._header_labels + [""]*(self._column_count - len(self._header_labels))
        
        self.setHorizontalHeaderLabels(self._header_labels)
        
    def addItem(self, key:str, value:dict|list|str|int|float|bool|None, parent:QJsonKeyItem=None):

        if parent is None: # root
            if not isinstance(value, dict):
                raise TypeError
            for k, v in value.items():
                self.addItem(k,v,self)
            return

        if isinstance(value, dict):
            key_item = QJsonKeyItem(key, dict, checkable=self._selectable_row, editable=self._editable_keys)
            parent.appendRow(key_item)
            for k, v in value.items():
                self.addItem(k,v,key_item)
            return
        
        if isinstance(value, list):
    
            if not value:
                key_item = QJsonKeyItem(key, list, checkable=self._selectable_row, editable=self._editable_keys)
                parent.appendRow(key_item)
                return 
            
            if all([ isinstance(v, (str,int,float,bool,type(None))) for v in value ]):
                key_item = QJsonKeyItem(key, list, checkable=self._selectable_row, editable=self._editable_keys)
                items_list = [ QJsonItem(v, editable=self._editable_values) for v in value ]
                self._column_count = max(1 + len(items_list), self._column_count)
                parent.appendRow([key_item] + items_list)
                return 

            if all([ isinstance(v, dict) for v in value ]):
                try: 
                    key_item = QJsonKeyItem(key, list, checkable=self._selectable_row, editable=self._editable_keys, isTable=True, isTransposed=self._transpose_arrays)
                    parent.appendRow(key_item)
                    df = pd.DataFrame(value)
                    self.addItemsFromDataFrame(df, key_item)
                    return
                except:
                    pass

            key_item = QJsonKeyItem(key, list, checkable=self._selectable_row, editable=self._editable_keys)
            parent.appendRow(key_item)
            for e, v in enumerate(value):
                self.addItem(e,v,key_item)
            return 
        

        if isinstance(value, (str, bool, int, float)):
            key_item = QJsonKeyItem(key, type(value), checkable=self._selectable_row, editable=self._editable_keys)
            value_item = QJsonItem(value, editable=self._editable_values)
            parent.appendRow([key_item, value_item])
            return
    
        if isinstance(value, type(None)):
            key_item = QJsonKeyItem(key, type(value), checkable=self._selectable_row, editable=self._editable_keys)
            value_item = QJsonItem(value, editable=self._editable_values)
            parent.appendRow([key_item, value_item])
            return

    def addItemsFromDataFrame(self, df:pd.DataFrame, parent:QJsonKeyItem):
        
        if self._transpose_arrays:
            items_list = [None]
            items_list.extend(df.columns.to_list())
            items_list = [ QJsonItem(value, selectable=False, enabled=False) for value in items_list ]
            parent.appendRow(items_list)
            
            df = df.T

        for column_name, series in df.items():
            items_list = []
            key_item = QJsonItem(column_name, checkable=self._selectable_row, editable=self._editable_keys)
            items_list.append(key_item)
            for index, value in series.items():
                value_item = QJsonItem(value, editable=self._editable_values)
                items_list.append(value_item)
            parent.appendRow(items_list)

    def flags(self, index: QModelIndex):

        if self._selectable_row and index.column() == 0:
            return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable

        return super().flags(index)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):

        #if self._selectable_row and index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:
        #    return self.itemData(index)[Qt.ItemDataRole.CheckStateRole]

        return super().data(index, role)

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole):
        
        if role == Qt.ItemDataRole.EditRole:

            self.contentEdited.emit(self.getModelAsDict())

        if index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:

            if self._single_selection:

                if self._last_index is not None:
                    
                    super().setData(self._last_index, Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)

                    self.dataChanged.emit(self._last_index, self._last_index, [Qt.ItemDataRole.DisplayRole])

                    self._last_index = None if self._last_index == index else index

                else:
                    self._last_index = index
            
            else:

                if self.hasChildren(index):
                    for child_row in range(self.itemFromIndex(index).rowCount()):
                        child_index = self.itemFromIndex(index).child(child_row,0).index()
                        super().setData(child_index, value, Qt.ItemDataRole.CheckStateRole)
                        self.dataChanged.emit(child_index, child_index, [Qt.ItemDataRole.DisplayRole])

            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

            self.selectionChanged.emit({})
            #self.selectedJsonItemsChanged.emit( self.getSelectedJsonItems() )
        
        return super().setData(index, value, role)

    def getModelAsDict(self, parent:QModelIndex=QModelIndex()) -> dict:

        model_as_dict = {}

        for row in range(self.rowCount(parent)):

            key_index  = self.index(row, 0, parent)
            key_string = self.data(key_index, Qt.ItemDataRole.EditRole)
            key_item:QJsonKeyItem = self.itemFromIndex(key_index)
        
            if key_item.dataType == list: 
                
                if key_item.isTable:

                    pass

                else:

                    values = []
                    for column in range(1, self.columnCount(parent)):
                        index = self.index(row, column, parent)
                        value = self.data(index, Qt.ItemDataRole.EditRole)
                        if value is None:
                            continue

                        values.append(value)

                    model_as_dict[key_string] = values

            else:

                if self.hasChildren(key_index):

                    model_as_dict[key_string] = self.getModelAsDict(key_index) #child_dict

                else:

                    index = self.index(row, 1, parent)
                    value = self.data(index, Qt.ItemDataRole.EditRole)
                    model_as_dict[key_string] = value

        return model_as_dict

    def getSelectedJsonItems(self) -> list[str]:

        return [ path for path, json_info in self._data.items() if json_info.checkState == 2 and not json_info.isBranch ]

class QJsonTreeView(QTreeView):

    def __init__(self,
            parent:QWidget= None,
            ):

        super().__init__(
            parent= parent,
            )

        self.setAnimated(True)
        self.setAlternatingRowColors(True)

        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setAllColumnsShowFocus(True)

        #self.setSortingEnabled(True)

        self.header().setSectionsClickable(True)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    def setModel(self, model: QStandardItemModel | QSortFilterProxyModel):

        super().setModel(model)

        #self.setColumnWidth(0, 250)
        #self.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self.expandAll()
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.resizeColumnToContents(0)

        self.setItemDelegate(QJsonItemDelegate(self))

    def setRootIndex(self, index:QModelIndex):

        model = self.model()

        if isinstance(model, QSortFilterProxyModel):
            
            index = model.mapFromSource(index)

        return super().setRootIndex(index)

    def wheelEvent(self, event:QWheelEvent):

        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            if event.angleDelta().y() > 0:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - 10)# row_height)
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + 10)# row_height)
        
            if self.horizontalScrollBar().isVisible():
                event.accept()

        else:
            if event.angleDelta().y() > 0:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 1)# row_height)
            else:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 1)# row_height)
    
            if self.verticalScrollBar().isVisible():
                event.accept()

class QJsonItemDelegate(QStyledItemDelegate):
    
    def initStyleOption(self, option:QStyleOptionViewItem, index:QModelIndex):

        super().initStyleOption(option, index)
        
        value = index.data(Qt.ItemDataRole.EditRole)

        if isinstance(value, bool):
            option.displayAlignment = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
            
        elif isinstance(value, (int, float)):
            option.displayAlignment = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight

    def displayText(self, value, locale:QLocale):

        if isinstance(value, bool):
            return "✔" if value else "✖"
        
        if isinstance(value, float):
            return f"{value:.2f}" if str(value).split(".") == 1 else str(value)

        return super().displayText(value, locale)
    
    def createEditor(self, parent:QWidget, option:QStyleOptionViewItem, index:QModelIndex):

        value = index.data(Qt.ItemDataRole.EditRole)

        if isinstance(value, str):
            editor = QLineEdit(parent)
            return editor

        if isinstance(value, bool):
            editor = QCheckBox(parent)
            editor.setAutoFillBackground(True)
            return editor
        
        if isinstance(value, int):
            editor = QInt64SpinBox(parent, alignment= Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            #editor.setRange(-2147483648, 2147483647)
            return editor

        if isinstance(value, float):
            editor = QAnyDecimalDoubleSpinBox(parent, alignment= Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            editor.setSingleStep(0.1)
            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor:QWidget, index:QModelIndex):

        value = index.data(Qt.ItemDataRole.EditRole)

        if isinstance(editor, QLineEdit):
            editor.setText(value)
            return

        if isinstance(editor, QCheckBox):
            editor.setChecked(value)
            return
        
        if isinstance(editor, QInt64SpinBox):
            editor.setValue(value)
            return

        if isinstance(editor, QAnyDecimalDoubleSpinBox):
            editor.setValue(value)
            return

        return super().setEditorData(editor, index)
        
    def setModelData(self, editor:QWidget, model:QAbstractItemModel, index:QModelIndex):

        if isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
            return

        if isinstance(editor, QCheckBox):
            model.setData(index, editor.isChecked(), Qt.ItemDataRole.EditRole)
            return
        
        if isinstance(editor, QInt64SpinBox):
            model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)
            return

        if isinstance(editor, QAnyDecimalDoubleSpinBox):            
            model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)
            return

        return super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor:QWidget, option:QStyleOptionViewItem, index:QModelIndex):

        rect: QRect = option.rect

        if isinstance(editor, QCheckBox):

            checkbox_size = editor.sizeHint() #40  # Adjust the size of the checkbox as needed
            x = rect.x() + (rect.width() - checkbox_size.width()) // 2
            y = rect.y() + (rect.height() - checkbox_size.height()) // 2
            checkbox_rect = QRect(x, y, checkbox_size.width(), checkbox_size.height())
            editor.setGeometry(checkbox_rect)
            return

        if isinstance(editor, (QLineEdit, QInt64SpinBox, QAnyDecimalDoubleSpinBox)):

            rect = rect.adjusted(-2, -2, 2, 2)
            editor.setGeometry(rect)
            return

        #editor.setGeometry(option.rect)

        super().updateEditorGeometry(editor, option, index)


# class QDataDictWrapper(QJsonTreeWidget):

#     def __init__(self,
#             init_data_dict : dict,
#             # --- Selection Settings --- #
#             selectable_row          : bool= True, 
#             single_selection        : bool= False,
#             # --- Other --- #
#             scrollbar_on_the_left   : bool= False,
#             parent:QWidget= None
#             ):

#         super().__init__(
#             selectable_row= selectable_row,
#             single_selection= single_selection,
#             scrollbar_on_the_left= scrollbar_on_the_left,
#             parent= parent,
#             )

















