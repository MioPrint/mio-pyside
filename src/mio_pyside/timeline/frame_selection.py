
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class FrameSelectionWidget(QWidget):

    index_updated = Signal(int)

    def __init__(self, 
            min_index:int= 0, 
            max_index:int= 100,
            parent:QWidget= None,
            ):

        super(FrameSelectionWidget, self).__init__(parent)

        ### FRAME SELECTION VARIABLES ###

        self.FRAME_SELECTION_TEMPLATE = "Frame Selection (index) ({idx_min},{idx_max})"
        self.min_index = min_index
        self.max_index = max_index
        self.current_index = self.min_index

        ### FRAME SELECTION WIDGETS ###

        selection_text = self.FRAME_SELECTION_TEMPLATE.format(
            idx_min=self.min_index,
            idx_max=self.max_index
        )
        self.label_frame_selection = QLabel(selection_text)
        
        self.button_frame_selection_first = QPushButton()
        self.button_frame_selection_first.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward)))
        self.button_frame_selection_first.clicked.connect(self.on_button_frame_selection_first_clicked)
        
        self.button_frame_selection_previous = QPushButton()
        self.button_frame_selection_previous.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward)))
        self.button_frame_selection_previous.clicked.connect(self.on_button_frame_selection_previous_clicked)
        
        self.lineedit_frame_selection = QLineEdit()
        self.lineedit_frame_selection.setText(str(0))
        self.lineedit_frame_selection.returnPressed.connect(self.on_lineedit_frame_selection_enter)
        self.lineedit_frame_selection.setFixedWidth(40)
        
        self.button_frame_selection_next = QPushButton()
        self.button_frame_selection_next.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward)))
        self.button_frame_selection_next.clicked.connect(self.on_button_frame_selection_next_clicked)
        
        self.button_frame_selection_last = QPushButton()
        self.button_frame_selection_last.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward)))
        self.button_frame_selection_last.clicked.connect(self.on_button_frame_selection_last_clicked)
        
        ##############
        ### LAYOUT ###
        ##############

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_frame_selection_first, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_buttons.addWidget(self.button_frame_selection_previous, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_buttons.addWidget(self.lineedit_frame_selection, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_buttons.addWidget(self.button_frame_selection_next, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_buttons.addWidget(self.button_frame_selection_last, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label_frame_selection, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(layout_buttons)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0,0,0,0)
        #print(layout.getContentsMargins())
        
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    ### FRAME SELECTION WIDGET SIGNALS ###

    def on_lineedit_frame_selection_enter(self):

        old_idx = self.current_index
        new_idx = self.lineedit_frame_selection.text()
        
        if self.is_valid_idx(new_idx):
            self.current_index = int(new_idx)
            self.update_frame_selection_options()
            self.index_updated.emit(self.current_index)

        else:
            self.current_index = old_idx
            self.lineedit_frame_selection.setText(str(old_idx))
            print(f' {new_idx} is NOT a valid index!')

    def is_valid_idx(self, new_idx:str):

        if isinstance(new_idx, str):
            if new_idx.isdigit():
                new_idx = int(new_idx)
                if new_idx >= self.min_index and new_idx <= self.max_index:
                    return True
                else:
                    return False
            else:
                return False
            
        elif isinstance(new_idx, int):
            if new_idx >= self.min_index and new_idx <= self.max_index:
                return True
            else:
                return False

    def on_button_frame_selection_first_clicked(self):
        self.current_index = self.min_index
        self.update_frame_selection_options()
        self.index_updated.emit(self.current_index)
        
    def on_button_frame_selection_previous_clicked(self):
        self.current_index = self.current_index - 1
        self.update_frame_selection_options()
        self.index_updated.emit(self.current_index)
        
    def on_button_frame_selection_next_clicked(self):
        self.current_index = self.current_index + 1
        self.update_frame_selection_options()
        self.index_updated.emit(self.current_index)
        
    def on_button_frame_selection_last_clicked(self):
        self.current_index = self.max_index
        self.update_frame_selection_options()
        self.index_updated.emit(self.current_index)
        
    ### FRAME SELECTION UPDATES ###

    def update_frame_selection_limits(self, min_index:int, max_index:int):
        self.min_index = min_index
        self.max_index = max_index
        self.current_index = self.min_index
        
        self.update_frame_selection_options()
        self.index_updated.emit(self.current_index)

    def update_frame_selection_options(self):
   
        selection_text = self.FRAME_SELECTION_TEMPLATE.format(
            idx_min=self.min_index,
            idx_max=self.max_index
        )
        self.label_frame_selection.setText(selection_text)
        self.lineedit_frame_selection.setText(str(self.current_index))
        self.lineedit_frame_selection.setEnabled(True)

        if self.current_index == self.min_index:
            self.button_frame_selection_first.setEnabled(False)
        else:
            self.button_frame_selection_first.setEnabled(True)

        if self.current_index == self.max_index:
            self.button_frame_selection_last.setEnabled(False)
        else:
            self.button_frame_selection_last.setEnabled(True)

        if self.current_index + 1 <= self.max_index:
            self.button_frame_selection_next.setEnabled(True)
        else:
            self.button_frame_selection_next.setEnabled(False)

        if self.current_index - 1 >= self.min_index:
            self.button_frame_selection_previous.setEnabled(True)
        else:
            self.button_frame_selection_previous.setEnabled(False)

    ### SETs ###

    def set_current_index(self, new_current_index:int):

        if self.is_valid_idx(new_current_index):
            self.current_index = new_current_index
            self.update_frame_selection_options()
            self.index_updated.emit(self.current_index)
        else:
            pass

    ### GETs ### 

    def get_current_index(self) -> int:

        return self.current_index