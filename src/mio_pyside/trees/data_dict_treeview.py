
import sys, os, json, logging

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

import numpy as np

from mio_pyside.spinboxes.spinboxes import QNumpyUIntSpinBox, QNumpyInt64SpinBox
from mio_pyside.colors.palette import color_amber_70p

# ----------------- #
# --- Tree View --- #
# ----------------- #

class DataDictTreeView(QTreeView):

    content_edited = Signal(dict)
    checkbox_selection_changed = Signal(dict)
    single_selection_changed = Signal(list)

    """  DataDictTreeView description 

        Attributes: 
            data_dict : Dictionary containitg data for visualization / editing, see bellow 
            headers_list : Column names list
            editing_enabled_list : Bollean list which maps 1:1 with headers_list and defines weather editing is enabled for that column 
            selectable_row : Bollean that defines weather checkboxes will be set up for selection of rows 
            spinbox_limits_dict : Dictinary containing range specification for SpinBoxes and DoubleSpinBoxes,
                Keys of this dict need to be column headers, and values are dictionaries with min and max values e.g: {'min':0, 'max':'100'}
                min and max values can also be specified with 'by_value' sitring, in which case the values from data_dict at init will be used as limits 

        data_dict has to be in this format:

            key of a dict is always column 0 element
            if value of a dict is a dict,
                value shall be treated as a child element and processed recursivly
            if value of a dict is a list, 
                elements of the list become column values for that row 
            if value of a dict is a tuple, 
                first tuple element shall be a list and its elements will become column values
                second tuple element shall be a dict and it shall be treated as a child element and processed recursivly
                
        data_dict_example = {

            'top_lvl_1': [ attr_1, attr_2, attr_3, ... ],
            'top_lvl_2': {
                'first_child_lvl_1': [ attr_1, attr_2, attr_3, ... ],
                'first_child_lvl_2': [ attr_1, attr_2, attr_3, ... ],
                ...
            },
            'top_lvl_3': {
                'first_child_lvl_1': [ attr_1, attr_2, attr_3, ... ],
                'first_child_lvl_2': {
                    'second_child_lvl_1': [ attr_1, attr_2, attr_3, ... ],
                    'second_child_lvl_2': [ attr_1, attr_2, attr_3, ... ],
                    ...
                },
            },
            'top_lvl_4': ( 
                [ attr_1, attr_2, attr_3, ... ], 
                {
                'first_child_lvl_1': [ attr_1, attr_2, attr_3, ... ],
                ...
                }, 
            ), 
        } 

        """

    def __init__(self,
            data_dict:dict= {},
            headers_list:list= [],
            editing_enabled_list:list= [],
            spinbox_limits_dict:dict= {},

            selectable_row:bool= False,
            single_selection:bool= False,
            select_parents_only:bool= False,
            select_children_only:bool= False,

            right_click_menu:bool= True,
            default_row_list:list= [],
            
            money_format:bool= False,

            parent:QWidget= None,
            *args, **kwargs,
            ):
        
        super(DataDictTreeView, self).__init__(parent)

        self.data_dict = data_dict.copy()
        self.headers_list = headers_list.copy()
        self.editing_enabled_list = editing_enabled_list.copy()
        self.spinbox_limits_dict = spinbox_limits_dict.copy()

        self.selectable_row = selectable_row
        self.single_selection = single_selection
        self.select_parents_only = select_parents_only
        self.select_children_only = select_children_only

        self.right_click_menu = right_click_menu
        self.default_row_list = default_row_list

        self.money_format = money_format
        
        QScroller.grabGesture(self.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setAnimated(True)
        self.setAllColumnsShowFocus(True)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.setStyleSheet("""
            QTreeView::item { border-right: 1px solid lightgray;  /* Vertical lines between columns */ }
            QTreeView::item:selected { color: black; }
            """)
        #QTreeView::item:selected { color: blue; background-color: lightblue; }

        self.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.header().setStretchLastSection(False)
        self.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header().setSectionsClickable(True)
        self.header().sectionDoubleClicked.connect(self.edit_header)
        self.header().setStyleSheet(f"""
            QHeaderView::section:hover { ' { background-color:' + color_amber_70p['hex'].replace('#', '#44') + '; } ' }
            """)
        
        self.init_model(
            data_dict= self.data_dict, 
            headers_list= self.headers_list, 
            editing_enabled_list= self.editing_enabled_list,
            spinbox_limits_dict= spinbox_limits_dict,
            selectable_row= self.selectable_row,
            single_selection= self.single_selection,
            money_format= self.money_format,
            *args, **kwargs,
            )

    def init_model(self, *args, **kwargs) -> None:
        
        self.data_dict =            kwargs.get('data_dict', self.data_dict).copy()
        self.headers_list =         kwargs.get('headers_list', self.headers_list).copy()
        self.editing_enabled_list = kwargs.get('editing_enabled_list', self.editing_enabled_list)
        self.spinbox_limits_dict =  kwargs.get('spinbox_limits_dict', self.spinbox_limits_dict)

        self.selectable_row =       kwargs.get('selectable_row', self.selectable_row)
        self.single_selection =     kwargs.get('single_selection', self.single_selection)
        self.select_parents_only =  kwargs.get('select_parents_only', self.select_parents_only)
        self.select_children_only = kwargs.get('select_children_only', self.select_children_only)

        self.right_click_menu =     kwargs.get('right_click_menu', self.right_click_menu)
        self.default_row_list =     kwargs.get('default_row_list', self.default_row_list)

        self.money_format =         kwargs.get('money_format', self.money_format)

        self.tree_model:TreeModel = TreeModel(
            data_dict= self.data_dict, 
            headers_list= self.headers_list, 
            editing_enabled_list= self.editing_enabled_list,
            spinbox_limits_dict= self.spinbox_limits_dict,

            selectable_row= self.selectable_row,
            single_selection= self.single_selection,
            select_parents_only= self.select_parents_only,
            select_children_only= self.select_children_only,
            
            parent_treeview= self,
            )
        
        #self.tree_model.dataChanged.connect(self.data_changed)
        self.tree_model.content_changed.connect(self.content_changed)
        self.tree_model.checkbox_changed.connect(self.checkbox_changed)
        self.tree_model.single_item_selected.connect(self.single_item_selected)

        self.setModel(self.tree_model)

        self.delegate = generic_treeview_delegate(
            money_format= self.money_format,
            parent= self,
            )
        self.setItemDelegate(self.delegate)

        self.expandAll()

        if self.right_click_menu:
            self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self.open_menu)

        self.adjust_column_widths()

    ### Signals ### 

    def content_changed(self):

        self.adjust_column_widths()
        model:TreeModel = self.model()
        self.data_dict = model.get_as_dict()
        self.content_edited.emit(self.data_dict.copy())

    def checkbox_changed(self):

        model:TreeModel = self.model()
        selected_data_dict = model.get_as_dict(only_selected=True)
        self.checkbox_selection_changed.emit(selected_data_dict.copy())

    def single_item_selected(self, item_data:list):

        self.single_selection_changed.emit(item_data)

    ### Util ###

    def clear_treeview(self) -> None:

        self.tree_model.removeColumns(0, self.tree_model.columnCount())
        self.data_dict = {}

    def adjust_column_widths(self):

        for column in range(self.tree_model.columnCount()):
            if self.sizeHintForColumn(column) > 300:
                self.setColumnWidth(column, 300)
            else:
                self.resizeColumnToContents(column)

    ### GETs ###

    def get_data_dict(self) -> dict:

        model:TreeModel = self.model()
        return model.get_as_dict().copy()

    def get_selected_data_dict(self) -> dict:

        model:TreeModel = self.model()
        return model.get_as_dict(only_selected=True).copy()

    def get_headers_list(self) -> list:
        
        return self.headers_list.copy()

    ### Save ###

    def on_button_save_to_png_click(self):

        provided_path = '' 
        
        if provided_path != '':
            self.save_as_image(
                image_file_path= provided_path,
                )
            logging.info(f' treeview saved to {provided_path}')

        else:
            logging.info(f' saving treeview cancelled')

    def save_as_image(self, image_file_path:str, close_on_save:bool=True):

        save_treeview = DataDictTreeView(
            data_dict = self.data_dict,
            headers_list = self.headers_list,
            editing_enabled_list = self.editing_enabled_list,
            selectable_row = self.selectable_row,
            spinbox_limits_dict = self.spinbox_limits_dict,
            )
        
        save_treeview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        save_treeview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        save_treeview.setFixedSize(
            save_treeview.sizeHint().width() + 20,
            save_treeview.sizeHint().height() + 20,
            )
        
        save_pixmap = QPixmap(
            save_treeview.sizeHint().width() + 20,
            save_treeview.sizeHint().height() + 20,
            )
        save_pixmap.fill()

        save_painter = QPainter(save_pixmap)
        save_treeview.render(save_painter)
        save_painter.end()

        save_pixmap.save(image_file_path)

        if close_on_save:
            save_treeview.close()
        else:
            save_treeview.show()

    ### Events ###

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

    ### Menu ###

    def open_menu(self, position:QPoint):
        
        if self.viewport().mapFromGlobal(self.cursor().pos()) != position:
            return
        
        selected_index = self.indexAt(position)

        model:QAbstractItemModel = self.model()
        item:TreeItem = selected_index.internalPointer()

        row_index:int = selected_index.row()
        column_index:int = selected_index.column()

        row_key = item.data(column=0) if item is not None else ''
        column_name = model.headerData(section= column_index, orientation=Qt.Orientation.Horizontal)

        cell_value = selected_index.data()

        menu = QMenu(self)

        insert_child_action               = QAction('Insert Child', self)
        insert_child_with_defaults_action = QAction('Insert Child (with Default values)', self)
        insert_row_above_action           = QAction('Insert Row - Above', self)
        insert_row_below_action           = QAction('Insert Row - Below', self)
        remove_row_action                 = QAction(f'Remove Row / Child : {row_key}', self)
        insert_column_left_action         = QAction('Insert Column - Left', self)
        insert_column_right_action        = QAction('Insert Column - Right', self)
        remove_column_action              = QAction(f'Remove Column : {column_name}', self)
        copy_value_to_all_columns         = QAction(f'Copy Value to all Columns : {cell_value}', self)

        if not selected_index.isValid():
            insert_row_above_action.setEnabled(False)
            insert_row_below_action.setEnabled(False)
            remove_row_action.setEnabled(False)
            insert_column_left_action.setEnabled(False)
            insert_column_right_action.setEnabled(False)
            remove_column_action.setEnabled(False)
            copy_value_to_all_columns.setEnabled(False)
        else:
            if column_index == 0:
                insert_column_left_action.setEnabled(False)
                remove_column_action.setEnabled(False)
                copy_value_to_all_columns.setEnabled(False)
            else:
                insert_child_action.setEnabled(False)

            if not self.default_row_list:
                insert_child_with_defaults_action.setEnabled(False)

        insert_child_action.triggered.connect(lambda: self.insert_child(parent_index=selected_index))
        insert_child_with_defaults_action.triggered.connect(lambda: self.insert_child(parent_index=selected_index, defaults_on=True))
        insert_row_above_action.triggered.connect(lambda: self.insert_row(index=selected_index, index_offset=0))
        insert_row_below_action.triggered.connect(lambda: self.insert_row(index=selected_index, index_offset=1))
        remove_row_action.triggered.connect(lambda: self.remove_row(index=selected_index))
        insert_column_left_action.triggered.connect(lambda: self.insert_column(index=selected_index, index_offset=0))
        insert_column_right_action.triggered.connect(lambda: self.insert_column(index=selected_index, index_offset=1))
        remove_column_action.triggered.connect(lambda: self.remove_column(index=selected_index))
        copy_value_to_all_columns.triggered.connect(lambda: self.copy_value_to_all_columns(index=selected_index, cell_value=cell_value))

        menu.addAction(insert_child_action)
        menu.addAction(insert_child_with_defaults_action)
        menu.addSeparator()
        menu.addAction(insert_row_above_action)
        menu.addAction(insert_row_below_action)
        menu.addAction(remove_row_action)
        menu.addSeparator()
        menu.addAction(insert_column_left_action)
        menu.addAction(insert_column_right_action)
        menu.addAction(remove_column_action)
        menu.addSeparator()
        menu.addAction(copy_value_to_all_columns)

        menu.exec_(self.viewport().mapToGlobal(position))

        #self.selectionModel().clearCurrentIndex()
    
    ### Child ###

    def insert_child(self, parent_index:QModelIndex, defaults_on:bool=False) -> None:

        model:TreeModel = self.model()
        parent_item:TreeItem = parent_index.internalPointer() if parent_index.internalPointer() is not None else model.root_item

        unavailable_names = [parent_item.child(number=idx).data(column=0) for idx in range(parent_item.child_count())]

        child_dialog = NewChildDialog(
            unavailable_names= unavailable_names,
            parent= self,
            )
        if child_dialog.exec_() == QDialog.DialogCode.Accepted:
            child_name = child_dialog.get_child_name()
        else:
            return
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        data_list = [child_name] + self.default_row_list if self.default_row_list and defaults_on else [child_name]

        child_inserted:bool = model.insertRows(
            position= 0 if parent_index.isValid() else parent_item.child_count(), 
            rows= 1, 
            parent= parent_index, 
            data_list= data_list, #[child_name],
            )

        self.expand(parent_index)

        self.content_changed()
        self.checkbox_changed()

        QApplication.restoreOverrideCursor()

    ### Rows ###

    def insert_row(self, index:QModelIndex, index_offset:int) -> None:
        
        model:TreeModel = self.model()
        parent_index:QModelIndex = index.parent()
        parent_item:TreeItem = parent_index.internalPointer() if parent_index.internalPointer() is not None else model.root_item
        row_index:int = index.row() + index_offset

        unavailable_names = [parent_item.child(number=idx).data(column=0) for idx in range(parent_item.child_count())]

        row_dialog = NewRowDialog(
            unavailable_names= unavailable_names,
            parent= self,
            )
        if row_dialog.exec_() == QDialog.DialogCode.Accepted:
            row_name = row_dialog.get_row_name()
        else:
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        data_list = [row_name] if not self.default_row_list else [row_name] + self.default_row_list

        row_inserted:bool = model.insertRows(
            position= row_index, 
            rows= 1, 
            parent= parent_index, 
            data_list= data_list,
            )

        self.content_changed()
        self.checkbox_changed()

        QApplication.restoreOverrideCursor()

    def remove_row(self, index:QModelIndex) -> None:

        model:TreeModel = self.model()
        parent_index:QModelIndex = index.parent()
        row_index:int = index.row()

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        row_removed:bool = model.removeRows(
            position= row_index,
            rows= 1, 
            parent= parent_index,
            )

        self.content_changed()
        self.checkbox_changed()
        
        QApplication.restoreOverrideCursor()

    ### Columns ###

    def insert_column(self, index:QModelIndex, index_offset:int) -> None:

        model:TreeModel = self.model()
        column_index:int = index.column() + index_offset

        column_dialog = NewColumnDialog(parent=self)
        if column_dialog.exec_() == QDialog.DialogCode.Accepted:
            column_name = column_dialog.get_column_name()
        else:
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        column_inserted:bool = model.insertColumns(
            position= column_index, 
            columns= 1,
            )

        if column_inserted:
            model.setHeaderData(column_index, Qt.Orientation.Horizontal, column_name, Qt.ItemDataRole.EditRole)

        self.content_changed()
        self.checkbox_changed()

        QApplication.restoreOverrideCursor()

    def remove_column(self, index:QModelIndex) -> None:
        
        model:TreeModel = self.model()
        column_index:int = index.column()

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        column_removed:bool = model.removeColumns(
            position= column_index, 
            columns= 1,
            )

        self.content_changed()
        self.checkbox_changed()

        QApplication.restoreOverrideCursor()

    ### Cell ###

    def copy_value_to_all_columns(self, index:QModelIndex, cell_value) -> None:

        model:TreeModel = self.model()
        parent_index:QModelIndex = index.parent()
        row_index:int = index.row()

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        model.blockSignals(True)

        for column in range(1, model.columnCount()):

            cell_index:QModelIndex = model.index(row_index, column, parent_index)
            model.setData(cell_index, cell_value, Qt.ItemDataRole.EditRole)

        model.blockSignals(False)

        self.content_changed()
        self.checkbox_changed()

        QApplication.restoreOverrideCursor()

    ### Header ###

    def edit_header(self, section:int):

        model:TreeModel = self.model()

        current_header_text = model.headerData(section, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)

        lineedit_header = QLineEdit(self)
        lineedit_header.setText(current_header_text)
        lineedit_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lineedit_header.setSelection(0, len(current_header_text))

        ax = self.header().sectionViewportPosition(section)
        ay = 0
        aw = self.header().sectionSize(section)
        ah = self.header().height()
        lineedit_header.setGeometry(ax, ay, aw, ah)
        
        lineedit_header.setFocus()

        lineedit_header.editingFinished.connect(lambda: self.set_header_data(section, lineedit_header))

        lineedit_header.show()

    def set_header_data(self, section:int, editor:QLineEdit):

        model:TreeModel = self.model()

        new_header_text = editor.text()
        model.setHeaderData(section, Qt.Orientation.Horizontal, new_header_text, Qt.ItemDataRole.EditRole)

        editor.deleteLater()

# ------------------- #
# --- Menu Dialogs -- #
# ------------------- #

class NewChildDialog(QDialog):

    def __init__(self,
        unavailable_names:list=[],
        parent:QWidget= None,
        ):

        super(NewChildDialog, self).__init__(parent)

        self.unavailable_names = unavailable_names

        self.setWindowTitle('New Child Name')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.lineedit_new_child_name = QLineEdit(self)
        self.lineedit_new_child_name.textChanged.connect(self.on_lineedit_new_child_name_changed)

        #self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, parent=self)
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        #self.dialog_buttons.rejected.connect(self.reject)

        layout_main_h = QHBoxLayout()
        #layout_main_h.addWidget(QLabel('New Column Name:'))
        layout_main_h.addWidget(self.lineedit_new_child_name)
        layout_main_h.addWidget(self.dialog_buttons)

        #layout_main_v = QVBoxLayout()
        #layout_main_v.addLayout(layout_main_h)
        #layout_main_v.addWidget(self.dialog_buttons)

        self.setLayout(layout_main_h)
    
    def on_lineedit_new_child_name_changed(self):

        test_name = self.lineedit_new_child_name.text()

        if test_name in self.unavailable_names:
            self.lineedit_new_child_name.setStyleSheet("QLineEdit { color: red; }")
            self.dialog_buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        
        else:
            self.lineedit_new_child_name.setStyleSheet("QLineEdit { color: black; }")
            self.dialog_buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

    def get_child_name(self):
        
        return self.lineedit_new_child_name.text()
    
class NewRowDialog(QDialog):

    def __init__(self,
        unavailable_names:list=[],
        parent:QWidget= None,
        ):

        super(NewRowDialog, self).__init__(parent)

        self.unavailable_names = unavailable_names

        self.setWindowTitle('New Row Name')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.lineedit_new_row_name = QLineEdit(self)
        self.lineedit_new_row_name.textChanged.connect(self.on_lineedit_new_row_name_changed)

        #self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, parent=self)
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        #self.dialog_buttons.rejected.connect(self.reject)

        layout_main_h = QHBoxLayout()
        #layout_main_h.addWidget(QLabel('New Column Name:'))
        layout_main_h.addWidget(self.lineedit_new_row_name)
        layout_main_h.addWidget(self.dialog_buttons)

        #layout_main_v = QVBoxLayout()
        #layout_main_v.addLayout(layout_main_h)
        #layout_main_v.addWidget(self.dialog_buttons)

        self.setLayout(layout_main_h)
    
    def on_lineedit_new_row_name_changed(self):

        test_name = self.lineedit_new_row_name.text()

        if test_name in self.unavailable_names:
            self.lineedit_new_row_name.setStyleSheet("QLineEdit { color: red; }")
            self.dialog_buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        
        else:
            self.lineedit_new_row_name.setStyleSheet("QLineEdit { color: black; }")
            self.dialog_buttons.button(QDialogButtonBox.Ok).setEnabled(True)

    def get_row_name(self):
        
        return self.lineedit_new_row_name.text()
    
class NewColumnDialog(QDialog):

    def __init__(self,
        parent:QWidget = None,
        ):

        super(NewColumnDialog, self).__init__(parent)

        self.setWindowTitle('New Column Name')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.lineedit_new_column_name = QLineEdit(self)

        #self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, parent=self)
        self.dialog_buttons.accepted.connect(self.accept)
        #self.dialog_buttons.rejected.connect(self.reject)

        layout_main_h = QHBoxLayout()
        #layout_main_h.addWidget(QLabel('New Column Name:'))
        layout_main_h.addWidget(self.lineedit_new_column_name)
        layout_main_h.addWidget(self.dialog_buttons)

        #layout_main_v = QVBoxLayout()
        #layout_main_v.addLayout(layout_main_h)
        #layout_main_v.addWidget(self.dialog_buttons)

        self.setLayout(layout_main_h)
    
    def get_column_name(self):

        return self.lineedit_new_column_name.text()

# --------------------------- #
# --- Abstract Item Model --- #
# --------------------------- #

class TreeModel(QAbstractItemModel):

    content_changed = Signal()
    checkbox_changed = Signal()
    single_item_selected = Signal(list)

    def __init__(self,
            data_dict:dict,
            headers_list:list = ['',''],
            editing_enabled_list:list= [],
            spinbox_limits_dict:dict= {},

            selectable_row:bool= False,
            single_selection:bool= False,
            select_parents_only:bool= False,
            select_children_only:bool= False,

            parent_treeview:'DataDictTreeView'= None,
            ):

        super(TreeModel, self).__init__(parent_treeview)

        self.data_dict = data_dict.copy()
        self.headers_list = headers_list.copy()
        self.editing_enabled_list = editing_enabled_list.copy()
        self.spinbox_limits_dict = spinbox_limits_dict.copy()

        self.selectable_row = selectable_row
        self.single_selection = single_selection
        self.select_parents_only = select_parents_only
        self.select_children_only = select_children_only

        self.parent_treeview = parent_treeview

        if not self.editing_enabled_list:
            self.editing_enabled_list = [False for column in self.headers_list]

        # self.is_file_system_model = isinstance(parent_treeview, src.file_system_treeview)

        self.last_checked_item_index:QModelIndex = None

        self.root_item = TreeItem(
            data_list= self.headers_list, 
            selectable_row= self.selectable_row,
            select_parents_only = self.select_parents_only,
            select_children_only = self.select_children_only,
            )
        
        self.setup_model_via_data_dict(
            data_dict= self.data_dict, 
            parent= self.root_item, 
            root_tree_item= self.root_item
            )

    def setup_model_via_data_dict(self, 
            data_dict:dict, 
            parent:'TreeItem'= None, 
            root_tree_item:'TreeItem'= None,
            ):
    
        def setup_row_via_list(self:TreeModel, tree_item:TreeItem, row_list:list):

            if len(row_list) > self.root_item.column_count():

                number_of_missing_columns = len(row_list) - self.root_item.column_count()
                column_positions = list(range(self.root_item.column_count(), number_of_missing_columns))

                for column_pos in column_positions:

                    self.insertColumns(
                        position= column_pos, 
                        columns= 1
                        )
                    self.setHeaderData(column_pos, Qt.Orientation.Horizontal, '', Qt.ItemDataRole.EditRole)

            if len(self.editing_enabled_list) < len(row_list)+1:
                self.editing_enabled_list.extend([self.editing_enabled_list[-1] for r in range(len(row_list)+1 - len(self.editing_enabled_list))])

            for column, cell_value in enumerate(row_list):

                column_name = self.headerData(column+1, Qt.Orientation.Horizontal)

                tree_item.set_item_enabled(column=column+1, is_enabled=self.editing_enabled_list[column+1])

                if column_name in self.spinbox_limits_dict.keys():
                    
                    min_value = self.spinbox_limits_dict[column_name]['min']
                    if min_value == 'by_value':
                        min_value = cell_value
                    elif min_value == 'by_value-1':
                        min_value = int(cell_value-1) if isinstance(cell_value, (int, np.unsignedinteger, np.signedinteger)) else cell_value-1

                    max_value = self.spinbox_limits_dict[column_name]['max']
                    if max_value == 'by_value':
                        max_value = cell_value
                    elif max_value == 'by_value-1':
                        max_value = int(cell_value-1) if isinstance(cell_value, (int, np.unsignedinteger, np.signedinteger)) else cell_value-1
                        cell_value = int(cell_value-1) if isinstance(cell_value, (int, np.unsignedinteger, np.signedinteger)) else cell_value-1

                    if min_value < max_value:
                        tree_item.set_item_data(column=column+1, value=cell_value)
                    else:
                        tree_item.set_item_data(column=column+1, value=None)
                    
                    tree_item.set_item_limits(column=column+1, min_value=min_value, max_value=max_value)

                else:                            
                    tree_item.set_item_data(column=column+1, value=cell_value)

        for key, value in data_dict.items():

            top_tree_item = TreeItem(
                data_list= [key], 
                parent= parent, 
                selectable_row= self.selectable_row,
                select_parents_only = self.select_parents_only,
                select_children_only = self.select_children_only,
                )

            parent.insert_children(position=parent.child_count(), count=1, columns=root_tree_item.column_count())
            top_tree_item = parent.last_child()
            top_tree_item.set_item_data(column=0, value=key)
            top_tree_item.set_item_enabled(column=0, is_enabled=self.editing_enabled_list[0])
            
            if isinstance(value, dict):

                sub_tree_item = self.setup_model_via_data_dict(
                    data_dict= value, 
                    parent= top_tree_item, 
                    root_tree_item= root_tree_item,
                    )

            elif isinstance(value, list):

                setup_row_via_list(
                    self= self, 
                    tree_item= top_tree_item, 
                    row_list= value,
                    )

            elif isinstance(value, tuple):

                setup_row_via_list(
                    self= self, 
                    tree_item= top_tree_item, 
                    row_list= value[0],
                    )
                
                sub_tree_item = self.setup_model_via_data_dict(
                    data_dict= value[1], 
                    parent= top_tree_item, 
                    root_tree_item= root_tree_item,
                    )

            else:

                setup_row_via_list(
                    self= self, 
                    tree_item= top_tree_item, 
                    row_list= [value],
                    )

        return root_tree_item
        
    def get_as_dict(self, only_selected:bool=False) -> dict:

        return self.root_item.get_as_dict(only_selected=only_selected)
    
    ### header ###

    def headerData(self, section:int, orientation:Qt.Orientation, role:int=Qt.ItemDataRole.DisplayRole):

        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.root_item.data(section)
        
        return None

    def setHeaderData(self, section:int, orientation:Qt.Orientation, value, role:int=None) -> bool:

        if role != Qt.ItemDataRole.EditRole or orientation != Qt.Orientation.Horizontal:
            return False

        result:bool = self.root_item.set_item_data(section, value, role)

        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    ### column ###

    def columnCount(self, parent:QModelIndex=None) -> int:

        return self.root_item.column_count()

    def insertColumns(self, position:int, columns:int, parent:QModelIndex=QModelIndex()) -> bool:

        self.beginInsertColumns(parent, position, position + columns - 1)
        success:bool = self.root_item.insert_column(position, columns)
        self.endInsertColumns()

        return success

    def removeColumns(self, position:int, columns:int, parent:QModelIndex=QModelIndex()) -> bool:

        self.beginRemoveColumns(parent, position, position + columns - 1)
        success:bool = self.root_item.remove_column(position, columns)
        self.endRemoveColumns()

        if self.root_item.column_count() == 0:
            self.removeRows(0, self.rowCount())

        return success

    ### row ###

    def rowCount(self, parent:QModelIndex=QModelIndex()) -> int:

        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item:TreeItem = self.get_item(parent)

        if not parent_item:
            return 0

        return parent_item.child_count()

    def insertRows(self, position:int, rows:int, parent:QModelIndex=QModelIndex(), data_list:list=[]) -> bool:

        parent_item:TreeItem = self.get_item(parent)

        if not parent_item:
            return False

        self.beginInsertRows(parent, position, position + rows - 1)

        column_count = self.root_item.column_count()
        if column_count == 0:
            parent_item.insert_column(0, 1)
            column_count = self.root_item.column_count()        
        success:bool = parent_item.insert_children(position, rows, column_count)

        self.endInsertRows()

        if success and data_list:
            child_item:TreeItem = parent_item.child(position)

            for column, cell_value in enumerate(data_list):
                child_item.set_item_data(column, cell_value)

        return success

    def removeRows(self, position:int, rows:int, parent:QModelIndex=QModelIndex()) -> bool:

        parent_item:TreeItem = self.get_item(parent)

        if not parent_item:
            return False

        self.beginRemoveRows(parent, position, position + rows - 1)
        success:bool = parent_item.remove_children(position, rows)
        self.endRemoveRows()

        return success

    ### fun stuff ###

    def get_item(self, index:QModelIndex=QModelIndex()) -> 'TreeItem':

        if index.isValid():

            item:TreeItem = index.internalPointer()

            if item:
                return item

        return self.root_item

    def index(self, row:int, column:int, parent:QModelIndex=QModelIndex()) -> QModelIndex:

        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item:TreeItem = self.get_item(parent)
        if not parent_item:
            return QModelIndex()

        child_item:TreeItem = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        
        return QModelIndex()

    def parent(self, index:QModelIndex=QModelIndex()) -> QModelIndex:

        if not index.isValid():
            return QModelIndex()

        child_item:TreeItem = self.get_item(index)

        if child_item:
            parent_item:TreeItem = child_item.parent()
        else:
            parent_item = None

        if parent_item == self.root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def flags(self, index:QModelIndex) -> Qt.ItemFlag:

        if not index.isValid():
            print(index)
            return Qt.ItemFlag.NoItemFlags
        
        flags = QAbstractItemModel.flags(self, index)

        item:TreeItem = self.get_item(index)

        if item.is_editable(index.column()):

            if item.get_min_value(index.column()) is not None and item.get_max_value(index.column()) is not None:
            
                if item.get_min_value(index.column()) < item.get_max_value(index.column()):
                    flags |= Qt.ItemFlag.ItemIsEditable

            else:
                flags |= Qt.ItemFlag.ItemIsEditable

        if self.selectable_row:

            if self.select_parents_only and item.child_count() == 0:
                return flags
            
            if self.select_children_only and item.child_count() > 0:
                return flags

            flags |= Qt.ItemFlag.ItemIsUserCheckable 
            flags |= Qt.ItemFlag.ItemIsAutoTristate

        return flags

    def data(self, index:QModelIndex, role:int=None):

        if not index.isValid():
            return None

        # if role == Qt.ItemDataRole.DecorationRole and self.is_file_system_model:
        #     if index.column() != 0:
        #         return None 
        #     item:TreeItem = self.get_item(index)
        #     return item.data(column=4, role=Qt.ItemDataRole.DecorationRole)

        if role != Qt.ItemDataRole.DisplayRole and role != Qt.ItemDataRole.EditRole and role != Qt.ItemDataRole.CheckStateRole:
            return None
        
        item:TreeItem = self.get_item(index)

        value = item.data(index.column(), role)

        return value
    
    def setData(self, index:QModelIndex, value, role:int, check_parent:bool=True, emit_checkbox_changed:bool=True) -> bool:

        if role != Qt.ItemDataRole.EditRole and role != Qt.ItemDataRole.CheckStateRole:
            return False

        item:TreeItem = self.get_item(index)

        result:bool = item.set_item_data(index.column(), value, role)

        if result:

            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.CheckStateRole])

            if role == Qt.ItemDataRole.EditRole:

                self.content_changed.emit()

                if item.is_checked() and emit_checkbox_changed:

                    self.checkbox_changed.emit()

            elif role == Qt.ItemDataRole.CheckStateRole:

                if self.single_selection:

                    if self.last_checked_item_index is not None:

                        if self.last_checked_item_index == index:
                            self.last_checked_item_index = None
                            self.single_item_selected.emit([])

                        else:

                            if value == Qt.CheckState.Checked:

                                last_checked_item = self.get_item(self.last_checked_item_index)
                                last_checked_item.set_item_data(self.last_checked_item_index.column(), Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
                                self.dataChanged.emit(self.last_checked_item_index, self.last_checked_item_index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.CheckStateRole])
                                self.last_checked_item_index = index
                                self.single_item_selected.emit(item.get_item_data())

                    else:
                        self.last_checked_item_index = index
                        self.single_item_selected.emit(item.get_item_data())

                else:
                    
                    for row in range(self.rowCount(index)):

                        self.setData(index.child(row, 0), value, Qt.ItemDataRole.CheckStateRole, check_parent=False, emit_checkbox_changed=False)

                    if check_parent:

                        self.check_parent(index.parent())

                    if value == Qt.CheckState.Checked:
                        self.single_item_selected.emit(item.get_item_data())
                    else:
                        self.single_item_selected.emit([])
                
                if emit_checkbox_changed:

                    self.checkbox_changed.emit()

        return result
    
    def check_parent(self, parent_index:QModelIndex):

        if not parent_index.isValid():
            return

        parent_item = self.get_item(parent_index)

        children_states = [self.get_item(self.index(row, 0, parent_index)).checked for row in range(self.rowCount(parent_index))]

        new_state = Qt.CheckState.Checked if all(children_states) else Qt.CheckState.Unchecked
        old_state = parent_item.checked

        if new_state != old_state:

            parent_item.set_item_data(0, new_state, Qt.ItemDataRole.CheckStateRole)

            self.dataChanged.emit(parent_index, parent_index)
        
        self.check_parent(parent_index.parent())

    def _repr_recursion(self, item:'TreeItem', indent:int=0) -> str:

        result = " " * indent + repr(item) + "\n"

        for child in item.child_items:
            result += self._repr_recursion(child, indent + 2)

        return result

    def __repr__(self) -> str:

        return self._repr_recursion(self.root_item)

# ----------------- #
# --- Tree Item --- #
# ----------------- #

class TreeItem:
    
    def __init__(self, 
            data_list:list= None, 
            parent:'TreeItem'= None,
            selectable_row:bool= False,
            select_parents_only:bool= False,
            select_children_only:bool= False,
            ):

        self.item_data = data_list
        self.parent_item = parent
        self.selectable_row = selectable_row
        self.select_parents_only = select_parents_only
        self.select_children_only = select_children_only

        self.child_items:list['TreeItem'] = []
        self.checked = False
        self.editing_enabled_list = [True for element in self.item_data]
        self.min_values = [None for element in self.item_data]
        self.max_values = [None for element in self.item_data]
        
    def __repr__(self) -> str:
        
        result = f"<treeitem.TreeItem at 0x{id(self):x}"
        
        for d in self.item_data:
            result += f' "{d}"' if d else " <None>"
        
        result += f", {len(self.child_items)} children>"
        
        return result

    ### Edit Children ###

    def insert_children(self, position:int, count:int, columns:int) -> bool:
        
        if position < 0 or position > len(self.child_items):
            return False

        for row in range(count):
        
            data = [None] * columns

            item = TreeItem(
                data_list= data.copy(), 
                parent= self,
                selectable_row= self.selectable_row,
                select_parents_only= self.select_parents_only,
                select_children_only= self.select_children_only,
                )
            
            self.child_items.insert(position, item)

        return True

    def remove_children(self, position:int, count:int) -> bool:
        
        if position < 0 or position + count > len(self.child_items):
            return False

        for row in range(count):

            self.child_items.pop(position)

        return True

    ### Edit Columns ###

    def insert_column(self, position:int, columns:int) -> bool:

        if position < 0 or position > len(self.item_data):
            return False

        for column in range(columns):
            self.item_data.insert(position, None)
            self.editing_enabled_list.insert(position, True)
            self.min_values.insert(position, None)
            self.max_values.insert(position, None)

        for child in self.child_items:
            child.insert_column(position, columns)

        return True

    def remove_column(self, position:int, columns:int) -> bool:
        
        if position < 0 or position + columns > len(self.item_data):
            return False

        for column in range(columns):
            self.item_data.pop(position)
            self.editing_enabled_list.pop(position)
            self.min_values.pop(position)
            self.max_values.pop(position)

        for child in self.child_items:
            child.remove_column(position, columns)

        return True

    ### SETs ###

    def set_item_data(self, column:int, value, role:int=None):
        
        if column < 0 or column >= len(self.item_data):
            return False
        
        if role == Qt.ItemDataRole.CheckStateRole:
        
            if self.selectable_row and column == 0:

                self.checked = value
                return True
        
        self.item_data[column] = value
        
        return True
    
    def set_item_enabled(self, column:int, is_enabled:bool):

        if column < 0 or column >= len(self.item_data):
            return False

        self.editing_enabled_list[column] = is_enabled
        return True

    def set_item_limits(self, column:int, min_value=None, max_value=None):

        if column < 0 or column >= len(self.item_data):
            return False
        
        self.min_values[column] = min_value 
        self.max_values[column] = max_value 

        return True

    ### GETs ###

    def data(self, column:int, role:int=None):

        if column < 0 or column >= len(self.item_data):
            return None
        
        if role == Qt.ItemDataRole.CheckStateRole:

            if column != 0:
                return None

            if not self.selectable_row:
                return None

            if self.select_parents_only and self.child_count() == 0:
                return None
            
            if self.select_children_only and self.child_count() > 0:
                return None

            return self.checked 
        
        if role == Qt.ItemDataRole.DecorationRole:

            if self.data(column=4): 
                if os.path.exists(self.data(column=4)):
                    return QFileIconProvider().icon(QFileInfo(self.data(column=4)))
            
            return None 

        return self.item_data[column]
    
    def is_checked(self) -> bool:

        return self.checked
    
    def is_editable(self, column:int) -> bool:

        return self.editing_enabled_list[column]

    def get_min_value(self, column:int):

        return self.min_values[column]

    def get_max_value(self, column:int):

        return self.max_values[column]
    
    def column_count(self) -> int:
        
        return len(self.item_data)

    def parent(self):
        
        return self.parent_item

    def child(self, number:int) -> 'TreeItem':

        if number < 0 or number >= len(self.child_items):
            return None
        
        return self.child_items[number]
    
    def last_child(self) -> 'TreeItem':
        
        return self.child_items[-1]

    def child_count(self) -> int:
        
        return len(self.child_items)

    def child_number(self) -> int:
        
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        
        return 0

    # used by treeview #

    def get_as_dict(self, only_selected:bool=False) -> dict: 

        return_dict = {}

        for child in self.child_items:

            child_key = child.item_data[0]
            child_values = child.item_data[1:]

            not_none_index_list = [e for e, value in enumerate(child_values) if value is not None]
            if not_none_index_list:
                child_values = child_values[:1+max(not_none_index_list)]
            else:
                child_values = [None]

            child_values = [ value if not isinstance(value, list) else value[0] for value in child_values ]

            if child.child_items:

                sub_child_dict = child.get_as_dict(only_selected=only_selected)

                if sub_child_dict:

                    if not_none_index_list:
                        return_dict.update( { child_key : (child_values, sub_child_dict) } )

                    else:
                        return_dict.update( { child_key : sub_child_dict } )
                
            else:

                if only_selected and not child.checked:
                    continue

                return_dict.update( { child_key : child_values } )

        return return_dict

    def get_item_data(self) -> list:

        return self.item_data.copy()

# ---------------------------- #
# --- Styled Item Delegate --- #
# ---------------------------- #

class generic_treeview_delegate(QStyledItemDelegate):

    def __init__(self, 
            money_format:bool= False,
            parent:DataDictTreeView= None,
            ):

        super().__init__(parent)

        self.money_format = money_format

    def initStyleOption(self, option:QStyleOptionViewItem, index:QModelIndex):

        super().initStyleOption(option, index)
        
        value = index.data()

        if isinstance(value, bool):
            option.displayAlignment = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter

        elif isinstance(value, (int, float, np.unsignedinteger, np.signedinteger, np.floating)):
            option.displayAlignment = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
    
    def createEditor(self, parent:QWidget, option:QStyleOptionViewItem, index:QModelIndex):

        value = index.data()
        model:TreeModel = index.model()
        column_name = model.headerData(index.column(), Qt.Orientation.Horizontal)
        item:TreeItem = model.get_item(index)

        if isinstance(value, bool):

            editor = QCheckBox(parent)
            editor.setAutoFillBackground(True)
            return editor

        elif isinstance(value, int):

            editor = QSpinBox(parent, alignment= Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if item.get_min_value(index.column()) is not None and item.get_max_value(index.column()):
                editor.setRange(item.get_min_value(index.column()), item.get_max_value(index.column()))
            else:
                editor.setRange(-2147483648, 2147483647)
            
            return editor

        elif isinstance(value, float):

            editor = QDoubleSpinBox(parent, alignment= Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            editor.setSingleStep(0.1)
            if item.get_min_value(index.column()) is not None and item.get_max_value(index.column()):
                editor.setRange(item.get_min_value(index.column()), item.get_max_value(index.column()))
            else:
                editor.setRange(sys.float_info.min, sys.float_info.max)
            return editor

        elif isinstance(value, np.unsignedinteger):

            editor = QNumpyUIntSpinBox(
                dtype=np.dtype(value), 
                parent=parent, 
                alignment= Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )

            if item.get_min_value(index.column()) is not None and item.get_max_value(index.column()):
                editor.setRange(item.get_min_value(index.column()), item.get_max_value(index.column()))
            
            return editor

        elif isinstance(value, np.signedinteger):

            editor = QNumpyInt64SpinBox(
                dtype=np.dtype(value), 
                parent=parent, 
                alignment= Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
            
            if item.get_min_value(index.column()) is not None and item.get_max_value(index.column()):
                editor.setRange(item.get_min_value(index.column()), item.get_max_value(index.column()))

            return editor
        
        elif isinstance(value, np.floating):

            editor = QDoubleSpinBox(parent, alignment= Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            if item.get_min_value(index.column()) is not None and item.get_max_value(index.column()):
                editor.setRange(item.get_min_value(index.column()), item.get_max_value(index.column()))
            else:
                min_value = np.finfo(np.dtype(value)).min
                max_value = np.finfo(np.dtype(value)).max
                editor.setRange(min_value, max_value)

            return editor
        
        elif isinstance(value, list):

            editor = QComboBox(parent)
            editor.addItems(value)
            QTimer.singleShot(0, editor.showPopup)

            return editor

        # Use default editor for other types
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor:QWidget, index:QModelIndex):

        value = index.data()

        if isinstance(value, bool):
            editor.setChecked(value)

        elif isinstance(value, (int, float, np.unsignedinteger, np.signedinteger, np.floating)):
            editor.setValue(value)

        elif isinstance(value, list):
            editor.setCurrentText(value[0])

        else:
            super().setEditorData(editor, index)

    def editorEvent(self, event:QEvent, model:QAbstractItemModel, option:QStyleOptionViewItem, index:QModelIndex):

        value = index.data(Qt.ItemDataRole.EditRole)
        model:TreeModel = index.model()
        item:TreeItem = model.get_item(index)
        is_editable = item.is_editable(index.column())

        if isinstance(value, bool):

            if is_editable:

                if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton: 
                    
                    new_value = not value
                    model.setData(index, new_value, Qt.ItemDataRole.EditRole)
                    return True 

        if isinstance(value, list):

            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.parent().edit(index)

                return True

        return super().editorEvent(event, model, option, index)

    def setModelData(self, editor:QWidget, model:QAbstractItemModel, index:QModelIndex):

        value = index.data()

        if isinstance(value, bool):
            model.setData(index, editor.isChecked(), Qt.ItemDataRole.EditRole)

        elif isinstance(value, (int, float, np.floating)):
            
            model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)

        elif isinstance(value, np.signedinteger):
            
            model.setData(index, editor.int_value(), Qt.ItemDataRole.EditRole)

        elif isinstance(value, np.unsignedinteger):

            model.setData(index, editor.uint_value(), Qt.ItemDataRole.EditRole)

        elif isinstance(value, list):

            selected_text = editor.currentText()
            selected_index = editor.currentIndex()

            value.pop(selected_index)
            value.insert(0, selected_text)

            model.setData(index, value, Qt.ItemDataRole.EditRole)

        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor:QWidget, option:QStyleOptionViewItem, index:QModelIndex):

        value = index.data(Qt.ItemDataRole.EditRole)

        if isinstance(value, bool):

            checkbox_size = 20  # Adjust the size of the checkbox as needed
            x = option.rect.x() + (option.rect.width() - checkbox_size) // 2
            y = option.rect.y() + (option.rect.height() - checkbox_size) // 2
            checkbox_rect = QRect(x, y, checkbox_size, checkbox_size)

            editor.setGeometry(checkbox_rect)

        elif isinstance(value, (int, float, np.unsignedinteger, np.signedinteger, np.floating)):

            editor.setGeometry(option.rect)

        else:

            editor.setGeometry(option.rect)

    def paint(self, painter:QPainter, option:QStyleOptionViewItem, index:QModelIndex):

        value = index.data()

        cell_is_editable = index.flags() & Qt.ItemFlag.ItemIsEditable

        if isinstance(value, bool):
            
            if cell_is_editable: 

                checkbox_style = QStyleOptionButton()
                checkbox_style.state |= QStyle.StateFlag.State_Enabled
                if value:
                    checkbox_style.state |= QStyle.StateFlag.State_On
                else:
                    checkbox_style.state |= QStyle.StateFlag.State_Off
                
                checkbox_size = 20
                x = option.rect.x() + (option.rect.width() - checkbox_size) // 2
                y = option.rect.y() + (option.rect.height() - checkbox_size) // 2
                checkbox_style.rect = QRect(x, y, checkbox_size, checkbox_size)
                
                QApplication.style().drawControl(QStyle.ControlElement.CE_CheckBox, checkbox_style, painter)

                self.set_background_colors(painter, option, option.rect, cell_is_editable)

            else:
                self.set_background_colors(painter, option, option.rect, cell_is_editable)
                painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, str(value).capitalize())

        elif isinstance(value, (int, float, np.unsignedinteger, np.signedinteger, np.floating)):

            if cell_is_editable:
            
                spinbox_style = QStyleOptionSpinBox()
                spinbox_style.state |= QStyle.StateFlag.State_Enabled
                spinbox_style.frame = False
                spinbox_style.rect = option.rect

                QApplication.style().drawComplexControl(QStyle.ComplexControl.CC_SpinBox, spinbox_style, painter)

                spinbox_style.rect.adjust(0, 0, -15, 0)
                self.set_background_colors(painter, option, spinbox_style.rect, cell_is_editable)

                string_of_num = f'{value}' if not self.money_format else f'{value:,.2f}'

                painter.drawText(spinbox_style.rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, string_of_num)
                
            else:

                option.rect.adjust(0, 0, -15, 0)
                self.set_background_colors(painter, option, option.rect, cell_is_editable)
                
                string_of_num = f'{value}' if not self.money_format else f'{value:,.2f}'
                
                painter.drawText(option.rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, string_of_num)

        elif isinstance(value, list):

            combobox_style = QStyleOptionComboBox()
            combobox_style.state = option.state
            combobox_style.rect = option.rect
            combobox_style.editable = False
            combobox_style.currentText = value[0]

            QApplication.style().drawComplexControl(QStyle.ComplexControl.CC_ComboBox, combobox_style, painter)
            QApplication.style().drawControl(QStyle.ControlElement.CE_ComboBoxLabel, combobox_style, painter)
            
            self.set_background_colors(painter, option, option.rect, cell_is_editable)

        else:

            self.set_background_colors(painter, option, option.rect, cell_is_editable)

            super().paint(painter, option, index)

    def set_background_colors(self, painter:QPainter, option:QStyleOptionViewItem, rect:QRect, cell_is_editable:bool):

        if option.state & QStyle.StateFlag.State_Selected:
            painter.save()
            painter.fillRect(rect, QColor(color_amber_70p['hex'].replace('#', '#CC')))
            painter.restore()
            return 
        
        if option.state & QStyle.StateFlag.State_MouseOver:
            painter.save()
            painter.fillRect(rect, QColor(color_amber_70p['hex'].replace('#', '#44')))
            painter.restore()
            return 
        
    def sizeHint(self, option:QStyleOptionViewItem, index:QModelIndex):

        size_hint = super().sizeHint(option, index)
        value = index.data()
    
        if isinstance(value, (int, float, np.unsignedinteger, np.signedinteger, np.floating)):

            font_metrics = option.fontMetrics
            content_width = font_metrics.boundingRect(str(value)).width() + 30
            content_height = font_metrics.boundingRect(str(value)).height()

            return QSize(content_width, content_height)

        else:
            return size_hint

# ------------ #
# --- Util --- #
# ------------ #

def print_data_dict(data_dict:dict, indent:str='', key_offset:int=0, with_type:bool=False):

    for key, value in data_dict.items():

        new_key_offset = len(f'{indent} {key}')
        if new_key_offset > key_offset:
            key_offset = new_key_offset + 8

        if isinstance(value, dict):

            print(f'{indent} {key}')
            print_data_dict(data_dict=value, indent=indent+'----', key_offset=key_offset, with_type=with_type)
            
        elif isinstance(value, list):

            print(f'{indent} {f"{key}":<{key_offset-len(indent)}} : {value}')

            if with_type:
                print(f'{indent} {f"":<{key_offset-len(indent)}} : {[type(element) for element in value]}')
                

        elif isinstance(value, tuple):

            print(f'{indent} {f"{key}":<{key_offset-len(indent)}} : {value[0]}')

            if with_type:
                print(f'{indent} {f"":<{key_offset-len(indent)}} : {[type(element) for element in value[1]]}')

            print_data_dict(data_dict=value[1], indent=indent+'----', key_offset=key_offset, with_type=with_type)

        else:
            
            raise ValueError(f' print_data_dict encountered unexpected value type: {str(type(value))}')
