# -*- coding: utf-8 -*-

import sys, os, logging, time, typing, json

from PySide6.QtCore import Qt, Signal, Slot, QDir, QFile, QSaveFile, QAbstractTableModel
from PySide6.QtWidgets import QWidget, QPushButton, QStyle, QFileDialog, QTableView, QAbstractScrollArea, QApplication, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QHeaderView
from PySide6.QtGui import QIcon, QAction, QWheelEvent, QColor, QKeySequence, QShortcut

from ..buttons.buttons import QLoadFileButton, QSaveFileButton

import pandas as pd
import numpy as np

##################
### QTableView ###
##################

class QBasicTableView(QTableView):

    csv_loaded_from_file = Signal(str)

    dataframe_updated = Signal(pd.DataFrame)
    
    def __init__(self, 
                 editable_table:bool= False, 
                 transposed_display:bool= False, 
                 resize_columns:bool= True,
                 tight_on:bool= False,
                 scroll_bar_on:bool= True,
                 parent:QWidget=None
                 ):
        
        super(QBasicTableView, self).__init__(parent)
        
        self.editable_table = editable_table
        self.transposed_display = transposed_display
        self.resize_columns = resize_columns
        self.tight_on = tight_on
        self.scroll_bar_on = scroll_bar_on

        self.dataframe = pd.DataFrame()
        self.display_dataframe = pd.DataFrame()
        self.table_model = None

        if tight_on:
            self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            #self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            #self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        if not scroll_bar_on:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignRight)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        self.update_table(pd.DataFrame())



        # copy_action = QAction("CopyTable", self)
        # # copy_action.setShortcut("Ctrl+C")
        # copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        # copy_action.triggered.connect(self.copy_selected_cells)
        # self.addAction(copy_action)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.shortcut.activated.connect(self.copy_selected_cells)



    def clear_table(self):

        self.update_table(pd.DataFrame())
        
    def update_dataframe_from_ui(self):
        
        input_dataframe = self.table_model.get_dataframe()
        self.validate_dataframe(input_dataframe)

    def update_dataframe_from_input_dataframe(self, input_dataframe:pd.DataFrame, emit:bool=True):

        self.validate_dataframe(input_dataframe, emit=emit)

    def update_dataframe_from_dict(self, input_dict:dict):

        dataframe_from_dict = pd.DataFrame([input_dict]) #.from_dict(input_dict)
        self.validate_dataframe(dataframe_from_dict)

    def read_dataframe_from_csv(self, input_path, delimiter:str=','):

        input_dataframe = pd.read_csv(input_path, delimiter=delimiter)#on_bad_lines='warn')
        self.validate_dataframe(input_dataframe)
    
    def validate_dataframe(self, input_dataframe:pd.DataFrame, emit:bool=True):

        if input_dataframe.empty:
            self.clear_table()
        else:
            self.update_table(input_dataframe, emit=emit)

    def update_table(self, input_dataframe:pd.DataFrame, emit:bool=True):

        self.dataframe = input_dataframe
        
        if self.transposed_display:
            input_dataframe = input_dataframe.T
        else:
            pass

        self.display_dataframe = input_dataframe

        if self.editable_table:
            self.table_model = editable_table_model_dataframe(input_dataframe)
        else:
            self.table_model = display_table_model_dataframe(input_dataframe)

        self.setModel(self.table_model)

        if self.resize_columns:
            self.setVisible(False)
            self.resizeColumnsToContents()
            self.resizeRowsToContents()
            self.setVisible(True)
    
        if emit:
            self.dataframe_updated.emit(self.dataframe)

    ### events ###

    def wheelEvent(self, event: QWheelEvent):

        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            #self.horizontalScrollBar().wheelEvent(event)
            #self.horizontalScrollBar().setSingleStep(1)
            if event.angleDelta().y() > 0:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - 1)# row_height)
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + 1)# row_height)

            if self.horizontalScrollBar().isVisible():
                event.accept()

        else:
            #self.verticalScrollBar().wheelEvent(event)
            #self.verticalScrollBar().setSingleStep(1)
            if event.angleDelta().y() > 0:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 1)# row_height)
            else:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 1)# row_height)
            
            if self.verticalScrollBar().isVisible():
                event.accept()

    ### actions ### 

    def copy_selected_cells(self):

        selection_model = self.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if not selected_indexes:
            return

        # Sort indexes to ensure correct order for copying (row-major)
        selected_indexes.sort(key=lambda x: (x.row(), x.column()))

        copied_text = []
        current_row = -1
        row_data = []

        for index in selected_indexes:
            if index.row() != current_row:
                if row_data:
                    copied_text.append("\t".join(row_data))
                row_data = []
                current_row = index.row()
            
            data = self.model().data(index, Qt.ItemDataRole.DisplayRole)
            row_data.append(str(data))
        
        if row_data: # Add the last row's data
            copied_text.append("\t".join(row_data))

        clipboard_text = "\n".join(copied_text)
        
        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text)
        print("Copied to clipboard:\n", clipboard_text)

###############
### QWidget ###
###############

class sheet_display_widget(QWidget):

    csv_loaded_from_file = Signal(str)

    def __init__(self, 
            input_data:pd.DataFrame|np.ndarray= pd.DataFrame(),
            window_title:str= ' ',
            adjust_column_widths:bool= False,
            is_transposed:bool= False,
            enable_load_button:bool= False,
            parent:QWidget= None,
            ):
        
        super().__init__(parent= parent)

        if parent is None:
            self.setWindowTitle(window_title)
        #self.setMinimumSize(800, 600)
        
        self.df = pd.DataFrame()

        self.is_transposed = is_transposed

        ### WIDGETS ### 
        self.basic_table = QBasicTableView(resize_columns=False, tight_on=adjust_column_widths)


        if adjust_column_widths:
            self.basic_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            #self.basic_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        ### STARTUP ### 
        if isinstance(input_data, pd.DataFrame):
            self.startup_via_df(input_data)
        elif isinstance(input_data, np.ndarray):
            self.startup_via_np_masked_array(input_data)

        self.button_save_table_to_csv = QLoadFileButton(target_extension='.csv', button_text= ' Load to .csv ', parent= self)
        self.button_save_table_to_csv.file_abspath_selected.connect(self.on_button_save_table_to_csv_click)

        self.button_load_table_from_csv = QSaveFileButton(target_extension='.csv', button_text= ' Save to .csv ', parent= self)
        self.button_load_table_from_csv.setEnabled(enable_load_button)
        self.button_load_table_from_csv.file_abspath_selected.connect(self.on_button_load_table_from_csv_click)

        #self.button_save_table_to_csv = QPushButton(' Save to .csv ')
        #self.button_save_table_to_csv.setIcon(QIcon(qApp.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)))
        #self.button_save_table_to_csv.clicked.connect(self.on_button_save_table_to_csv_click)
        #self.button_load_table_from_csv = QPushButton(' Load from .csv ')
        #self.button_load_table_from_csv.setIcon(QIcon(qApp.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)))
        #self.button_load_table_from_csv.clicked.connect(self.on_button_load_table_from_csv_click)

        self.checkbox_transpose = QCheckBox('Transpose', parent=self)
        self.checkbox_transpose.setChecked(self.is_transposed)
        self.checkbox_transpose.clicked.connect(self.on_checkbox_transpose_clicked)

        ### LAYOUT ### 
        layout_footer = QHBoxLayout()
        layout_footer.addWidget(self.checkbox_transpose, alignment=Qt.AlignmentFlag.AlignRight)
        layout_footer.addWidget(self.button_load_table_from_csv, alignment=Qt.AlignmentFlag.AlignRight)
        layout_footer.addWidget(self.button_save_table_to_csv, alignment=Qt.AlignmentFlag.AlignRight)
        layout_footer.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout = QVBoxLayout()
        layout.addWidget(self.basic_table,1)
        layout.addLayout(layout_footer)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(layout)

    def startup_via_df(self, init_df:pd.DataFrame):

        self.df = init_df
        
        if self.is_transposed:
            self.df = self.df.T
            
        self.basic_table.update_dataframe_from_input_dataframe(self.df)

    def startup_via_np_masked_array(self, init_masked_array:np.ma.array):

        self.df = pd.DataFrame(init_masked_array)
        
        if self.is_transposed:
            self.df = self.df.T
            
        self.basic_table.update_dataframe_from_input_dataframe(self.df)

    @Slot(str)
    def on_button_save_table_to_csv_click(self, input_path:str):
        
        #save_name = 'table' + '.csv'
        #input_path = str(QFileDialog.getSaveFileName(self, 'Save Table to .csv File', os.path.join(src.path_src,'interface_maker\\csvs',save_name), '(*.csv)')[0])
        #input_path = str(QFileDialog.getSaveFileName(self, 'Save Table to .csv File', os.path.join(src.folder_path, save_name), '(*.csv)')[0])
        if input_path != '':
            self.df.to_csv(input_path, index=False)
            logging.info(f' table saved to {input_path}')
        else:
            logging.info(f' saving table cancelled')

    @Slot(str)
    def on_button_load_table_from_csv_click(self, input_path:str):

        #input_path = str(QFileDialog.getOpenFileName(self, 'Find Table .csv File', os.path.join(src.path_src,'interface_maker\\csvs'), '(*.csv)')[0])
        #input_path = str(QFileDialog.getOpenFileName(self, 'Find Table .csv File', os.path.join(src.folder_path), '(*.csv)')[0])
        if input_path != '':

            self.basic_table.read_dataframe_from_csv(input_path)
            
            logging.info(f' loading csv done from {input_path}')
            self.csv_loaded_from_file.emit(input_path)
        else: 
            logging.info(f' loading table cancelled')

    @Slot()
    def on_checkbox_transpose_clicked(self):

        if self.checkbox_transpose.isChecked() != self.is_transposed:

            self.is_transposed = self.checkbox_transpose.isChecked()

            self.df = self.df.T

            self.basic_table.update_dataframe_from_input_dataframe(self.df)

class QBasicTableWidget(QWidget):
    
    csv_loaded_from_file = Signal(str)

    default_file_name = ''

    dataframe = pd.DataFrame()

    dataframe_updated = Signal(pd.DataFrame)

    def __init__(self, 
                editable_table:bool= False, 
                transposed_display:bool= False, 
                resize_columns:bool= True,
                tight_on:bool= False,
                scroll_bar_on:bool= True,
                delimiter:str=',',
                parent:QWidget= None,
                ):
        
        super().__init__(parent)

        self.editable_table = editable_table
        self.transposed_display = transposed_display
        self.resize_columns = resize_columns
        self.tight_on = tight_on
        self.scroll_bar_on = scroll_bar_on
        self.delimiter = delimiter

        self.init_widgets()
        self.init_layout()
        
    def init_widgets(self):

        self.basic_table_view = QBasicTableView(
            editable_table=self.editable_table,
            transposed_display=self.transposed_display,
            resize_columns=self.resize_columns,
            tight_on=self.tight_on,
            scroll_bar_on=self.scroll_bar_on,
            parent=self
            )
        self.basic_table_view.dataframe_updated.connect(self.dataframe_updated_slot)

        self.button_load_table_from_csv = QLoadFileButton(
            target_extension='.csv',
            button_text=' Load from .csv ',
            parent=self
            )
        self.button_load_table_from_csv.file_abspath_selected.connect(self.on_load_table_from_csv)

        self.button_save_table_to_csv = QSaveFileButton(
            target_extension='.csv',
            button_text=' Save to .csv ',
            parent=self
            )
        self.button_save_table_to_csv.file_abspath_selected.connect(self.on_save_table_to_csv)

        self.csv_file_abspath = QLabel()

    def init_layout(self):

        layout_csv_buttons = QHBoxLayout()
        layout_csv_buttons.addWidget(self.button_save_table_to_csv)
        layout_csv_buttons.addWidget(self.button_load_table_from_csv)
        layout_csv_buttons.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout_table_footer = QHBoxLayout()
        layout_table_footer.addWidget(self.csv_file_abspath, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_table_footer.addLayout(layout_csv_buttons)
        
        layout_main_v = QVBoxLayout()
        layout_main_v.addWidget(self.basic_table_view, 1)
        layout_main_v.addLayout(layout_table_footer)
        #layout_main_v.setContentsMargins(0,0,0,0)

        self.setLayout(layout_main_v)

    @Slot(pd.DataFrame)
    def dataframe_updated_slot(self, dataframe:pd.DataFrame):

        self.dataframe = dataframe
        self.dataframe_updated.emit(self.dataframe)

    @Slot(str)
    def on_save_table_to_csv(self, csv_abspath:str):

        self.basic_table_view.dataframe.to_csv(csv_abspath, index=False)

        self.default_file_name = os.path.basename(csv_abspath)

        logging.info(f' table saved to {csv_abspath}')

    #@src.wait_cursor_on_call()
    @Slot(str)
    def on_load_table_from_csv(self, csv_abspath:str):

        self.basic_table_view.read_dataframe_from_csv(csv_abspath, delimiter= self.delimiter)

        self.default_file_name = os.path.basename(csv_abspath)

        self.csv_file_abspath.setText(csv_abspath)

        logging.info(f' loading csv done from {csv_abspath}')

        self.csv_loaded_from_file.emit(csv_abspath)

    def set_dataframe(self, dataframe:pd.DataFrame):

        self.basic_table_view.update_dataframe_from_input_dataframe(dataframe, emit=False)

        self.dataframe = dataframe

################
### NOT USED ###
################

class display_table_model_dataframe(QAbstractTableModel):

    def __init__(self, init_dataframe:pd.DataFrame):
        super(display_table_model_dataframe, self).__init__()
        
        self.df = init_dataframe

        self.background_colors_df = pd.DataFrame().reindex_like(self.df)
        self.foreground_colors_df = pd.DataFrame().reindex_like(self.df)

    def set_background_colors(self, input_background_colors_df:pd.DataFrame):
        self.background_colors_df = input_background_colors_df

    def set_foreground_colors(self, input_foreground_colors_df:pd.DataFrame):
        self.foreground_colors_df = input_foreground_colors_df

    def get_dataframe(self):
        return self.df
    
    #def dataChanged(self, index_1, index_2):
    #    pass

    def data(self, index, role):

        if index.isValid():
        
            value = self.df.iloc[index.row(), index.column()]
            column_name = self.df.columns[index.column()]

            if role == Qt.UserRole:
                # Qt.UserRole = 0x0100
                pass

            if role == Qt.DisplayRole:
                # Qt.DisplayRole = 0

                if isinstance(value, int):
                    return str(value)
                
                if isinstance(value, float):
                    return str(value)

                if isinstance(value, str):

                    if value=='':
                        return value
                    else:
                        return '"%s"' % value
                
                # last return
                return str(value)
            
            if role == Qt.DecorationRole: 
                # Qt.DecorationRole = 1
                pass
            
            '''
            if role == Qt.EditRole:
                # Qt.EditRole = 2
                return str(value)
            '''

            if role == Qt.ToolTipRole:
                # Qt.ToolTipRole = 3
                pass

            if role == Qt.StatusTipRole:
                # Qt.StatusTipRole = 4
                pass
            
            if role == Qt.WhatsThisRole:
                # Qt.WhatsThisRole = 5
                pass

            if role == Qt.FontRole:
                # Qt.FontRole = 6
                pass

            if role == Qt.TextAlignmentRole:
                # Qt.TextAlignmentRole = 7
                return Qt.AlignVCenter + Qt.AlignHCenter
            
            if role == Qt.BackgroundRole:
                # Qt.BackgroundRole = 8
                background_color = self.background_colors_df.iloc[index.row(), index.column()]
                if background_color is not None:
                    return background_color
                else:
                    return QColor('white')

            if role == Qt.ForegroundRole:
                # Qt.ForegroundRole = 9
                foreground_color = self.foreground_colors_df.iloc[index.row(), index.column()]
                if foreground_color is not None:
                    return foreground_color
                else:
                    return QColor('black')
            
            if role == Qt.CheckStateRole:
                # Qt.CheckStateRole = 10
                pass

            if role == Qt.AccessibleTextRole:
                # Qt.AccessibleTextRole = 11
                pass

            if role == Qt.AccessibleDescriptionRole:
                # Qt.AccessibleDescriptionRole = 12
                pass

            if role == Qt.SizeHintRole:
                # Qt.SizeHintRole = 13
                pass

        else:
            return False
                    
    def rowCount(self, index):
        return self.df.shape[0]

    def columnCount(self, index):
        return self.df.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and not self.df.empty:

            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])

            if orientation == Qt.Vertical:
                return str(self.df.index[section])

class editable_table_model_dataframe(QAbstractTableModel):

    def __init__(self, init_dataframe:pd.DataFrame):
        super(editable_table_model_dataframe, self).__init__()
        
        self.df = init_dataframe

        self.background_colors_df = pd.DataFrame().reindex_like(self.df)
        self.foreground_colors_df = pd.DataFrame().reindex_like(self.df)

    def set_background_colors(self, input_background_colors_df:pd.DataFrame):
        self.background_colors_df = input_background_colors_df

    def set_foreground_colors(self, input_foreground_colors_df:pd.DataFrame):
        self.foreground_colors_df = input_foreground_colors_df

    def get_dataframe(self):
        return self.df
    
    #def dataChanged(self, index_1, index_2):
    #    pass

    def data(self, index, role):

        if index.isValid():

            value = self.df.iloc[index.row(), index.column()]
            column_name = self.df.columns[index.column()]

            if role == Qt.UserRole:
                # Qt.UserRole = 0x0100
                pass

            if role == Qt.DisplayRole:
                # Qt.DisplayRole = 0

                if isinstance(value, int):
                    return str(value)
                
                if isinstance(value, float):
                    return str(value)

                if isinstance(value, str):

                    if value=='':
                        return value
                    else:
                        return '"%s"' % value
                
                # last return
                return str(value)
            
            if role == Qt.DecorationRole: 
                # Qt.DecorationRole = 1
                pass

            if role == Qt.EditRole:
                # Qt.EditRole = 2
                return str(value)
            
            if role == Qt.ToolTipRole:
                # Qt.ToolTipRole = 3
                pass

            if role == Qt.StatusTipRole:
                # Qt.StatusTipRole = 4
                pass
            
            if role == Qt.WhatsThisRole:
                # Qt.WhatsThisRole = 5
                pass

            if role == Qt.FontRole:
                # Qt.FontRole = 6
                pass

            if role == Qt.TextAlignmentRole:
                # Qt.TextAlignmentRole = 7
                return Qt.AlignVCenter + Qt.AlignHCenter
            
            if role == Qt.BackgroundRole:
                # Qt.BackgroundRole = 8
                background_color = self.background_colors_df.iloc[index.row(), index.column()]
                if background_color is not None:
                    return background_color
                else:
                    return QColor('white')

            if role == Qt.ForegroundRole:
                # Qt.ForegroundRole = 9
                foreground_color = self.foreground_colors_df.iloc[index.row(), index.column()]
                if foreground_color is not None:
                    return foreground_color
                else:
                    return QColor('black')
            
            if role == Qt.CheckStateRole:
                # Qt.CheckStateRole = 10
                pass

            if role == Qt.AccessibleTextRole:
                # Qt.AccessibleTextRole = 11
                pass

            if role == Qt.AccessibleDescriptionRole:
                # Qt.AccessibleDescriptionRole = 12
                pass

            if role == Qt.SizeHintRole:
                # Qt.SizeHintRole = 13
                pass

        else:
            return False
                    
    def rowCount(self, index):
        return self.df.shape[0]

    def columnCount(self, index):
        return self.df.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and not self.df.empty:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])

            if orientation == Qt.Vertical:
                return str(self.df.index[section])
            
    def setData(self, index, value, role):
        if index.isValid():
            if role == Qt.EditRole:
                self.df.iloc[index.row(), index.column()] = value
                self.dataChanged.emit(index, index, [Qt.UserRole, Qt.DisplayRole])
                self.background_colors_df = pd.DataFrame().reindex_like(self.df)
                self.foreground_colors_df = pd.DataFrame().reindex_like(self.df)
                return True
            else:
                return False
        else:
            return False

    def flags(self, index):
        flags = super(self.__class__,self).flags(index)
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled
        return flags

