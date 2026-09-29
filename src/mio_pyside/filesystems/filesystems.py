
from dataclasses import dataclass, field, fields, asdict

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from ..buttons.buttons import QLoadFolderButton
from ..config import GLOBAL_WORKING_DIR, WorkingDir
from ..utils.decorators import block_signals, wait_cursor
from ..utils.format import format_file_size

class QFileAndFolderSelection(QWidget):

    selectedFilesChanged = Signal(list)
    selectedDirChanged   = Signal(list)

    def __init__(self,
            local_working_dir   : WorkingDir= None,
            # --- Selection Settings --- #
            selectable_row          : bool= True, 
            single_selection        : bool= False,
            # --- Filter Settings --- #
            file_extensions             : list[str]= [],
            startswith_filter_strings   : str= "",
            endswith_filter_strings     : str= "",
            contains_filter_strings     : str= "",
            # --- Other --- #
            scrollbar_on_the_left   : bool= False,
            parent:QWidget= None
            ):

        super().__init__(
            parent= parent,
            )
        
        self.setMinimumSize(350, 200)

        global GLOBAL_WORKING_DIR
        self._local_working_dir = local_working_dir if local_working_dir is not None else GLOBAL_WORKING_DIR

        self._selectable_row        = selectable_row
        self._single_selection      = single_selection 
        self._file_extensions           = file_extensions
        self._startswith_filter_strings = startswith_filter_strings
        self._endswith_filter_strings   = endswith_filter_strings
        self._contains_filter_strings   = contains_filter_strings
        self._scrollbar_on_the_left     = scrollbar_on_the_left

        # --- Widgets --- #

        self.navigation_bar = QFileNavigationBar(
            local_working_dir= self._local_working_dir, 
            parent= self,
            )

        self.filter_bar = QFilterBar(
            file_extensions             = self._file_extensions,
            startswith_filter_strings   = self._startswith_filter_strings,
            endswith_filter_strings     = self._endswith_filter_strings,
            contains_filter_strings     = self._contains_filter_strings,
            parent= self,
            )

        self.file_tree_view = QFileTree(
            local_working_dir       = self._local_working_dir,
            selectable_row          = self._selectable_row,
            single_selection        = self._single_selection,
            file_extensions             = self._file_extensions,
            startswith_filter_strings   = self._startswith_filter_strings,
            endswith_filter_strings     = self._endswith_filter_strings,
            contains_filter_strings     = self._contains_filter_strings,
            scrollbar_on_the_left   = self._scrollbar_on_the_left,
            parent= self,
            )

        self.filter_bar.filterStringsUpdated.connect(self.file_tree_view.updateFilterStrings)

        self.file_tree_view.selectedFilesChanged.connect(self.selectedFilesChanged.emit)
        self.file_tree_view.selectedDirChanged.connect(self.selectedDirChanged.emit)

        # --- Layout --- #

        layout_main_v = QVBoxLayout()
        layout_main_v.addWidget(self.navigation_bar)
        layout_main_v.addWidget(self.filter_bar)
        layout_main_v.addWidget(self.file_tree_view)
        self.setLayout(layout_main_v)

# --- Navigation Bar --- #

class QFileNavigationBar(QWidget):

    def __init__(self,
            local_working_dir : WorkingDir= None,
            parent:QWidget= None
            ):

        super().__init__(
            parent= parent,
            )
        
        global GLOBAL_WORKING_DIR
        self._local_working_dir = local_working_dir if local_working_dir is not None else GLOBAL_WORKING_DIR
        self._local_working_dir.changed.connect(self.localPathUpdated)

        self._history       : list = [self._local_working_dir.abspath()]
        self._history_index : int  = 1

        # --- Widgets --- #

        self.button_folder_dialog = QLoadFolderButton(local_working_dir= self._local_working_dir, parent= self)

        self.button_refresh = QPushButton(parent= self)
        self.button_refresh.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)))
        #self.button_refresh.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.button_refresh.clicked.connect(self.on_refresh)

        self.button_undo = QPushButton(parent= self)
        self.button_undo.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowLeft)))
        #self.button_undo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.button_undo.setEnabled(False)
        self.button_undo.clicked.connect(self.on_undo)

        self.button_redo = QPushButton(parent= self)
        self.button_redo.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight)))
        #self.button_redo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.button_redo.setEnabled(False)
        self.button_redo.clicked.connect(self.on_redo)

        self.button_up = QPushButton(parent= self)
        self.button_up.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)))
        #self.button_up.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.button_up.setEnabled( not self._local_working_dir.dir().isRoot() )
        self.button_up.clicked.connect(self.on_up)

        self.combobox_lineedit_path = QFolderPathCombobox(local_working_dir= self._local_working_dir, parent= self)
        
        # --- Layout --- #

        layout_main_h = QHBoxLayout()
        layout_main_h.addWidget(self.button_folder_dialog)
        layout_main_h.addWidget(self.combobox_lineedit_path)
        layout_main_h.addWidget(self.button_refresh)
        layout_main_h.addWidget(self.button_undo)
        layout_main_h.addWidget(self.button_redo)
        layout_main_h.addWidget(self.button_up)
        #layout_main_h.addStretch(0)
        layout_main_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_main_h.setSpacing(2)
        layout_main_h.setContentsMargins(0,0,0,0)
        
        self.setLayout(layout_main_h)

    @Slot()
    def on_refresh(self):

        self._history       : list = [self._local_working_dir.abspath()]
        self._history_index : int  = 1
        self._local_working_dir.refresh()

    @Slot()
    def on_undo(self):

        self._history_index -= 1
        self._local_working_dir.setPath(self._history[self._history_index])
    
    @Slot()
    def on_redo(self):

        self._history_index += 1
        self._local_working_dir.setPath(self._history[self._history_index])
    
    @Slot()
    def on_up(self):

        parent_path = self._local_working_dir.parentDir()

        if parent_path in self._history:

            self._history.pop(self._history.index(parent_path))
            self._history.append(parent_path)
            self._history_index = len(self._history)-1

        self._local_working_dir.setPath(parent_path)

    @Slot(str)
    def localPathUpdated(self, abspath:str):

        if not abspath in self._history:
            self._history.append(abspath)
            self._history_index = len(self._history)-1
        else:
            self._history_index = self._history.index(abspath)

        self.button_undo.setEnabled( len(self._history) > 1 and self._history_index != 0 )
        self.button_redo.setEnabled( len(self._history) > 1 and self._history_index != len(self._history)-1 )
        self.button_up.setEnabled( not self._local_working_dir.dir().isRoot() )

class QFolderPathCombobox(QComboBox):

    def __init__(self,
            local_working_dir : WorkingDir= None,
            parent:QWidget= None
            ):

        super().__init__(
            parent= parent,
            )

        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        #self.setMaximumWidth(500)
        self.setMaxVisibleItems(20)
        
        global GLOBAL_WORKING_DIR
        self._local_working_dir = local_working_dir if local_working_dir is not None else GLOBAL_WORKING_DIR
        self._local_working_dir.changed.connect(self.localPathUpdated)

        self.activated.connect(self.on_item_activated)
        self.lineEdit().editingFinished.connect(self.on_lineedit_editing_finished)

        self.localPathUpdated(self._local_working_dir.abspath())

    @Slot()
    def on_lineedit_editing_finished(self):

        new_text = self.lineEdit().text()

        if not QDir(new_text).exists():
            self.lineEdit().setText(self._local_working_dir.abspath())
            return

        self._local_working_dir.setPath(new_text)

    @Slot(int)
    def on_item_activated(self, item_index:int):

        self._local_working_dir.setPath(self.itemText(item_index))

    @Slot(str)
    @block_signals
    def localPathUpdated(self, abspath:str):

        self.clear()

        _subfolder_paths = self._local_working_dir.dir().entryInfoList(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        _subfolder_paths = [ fileInfo.absoluteFilePath() for fileInfo in _subfolder_paths ]

        _all_dirs = [abspath] + _subfolder_paths

        for e, path in enumerate(_all_dirs):
            self.addItem(path)
            icon = QFileIconProvider().icon(QFileInfo(path))
            self.setItemIcon(e, icon)

        self.setCurrentIndex(0)

# --- Filter Bar --- #

class QFilterBar(QWidget):

    filterStringsUpdated = Signal(str,str,str)
    startswithUpdated = Signal(str)
    containsUpdated   = Signal(str)
    endswithUpdated   = Signal(str)

    def __init__(self,
            file_extensions             : list[str]= [],
            startswith_filter_strings   : str= "",
            contains_filter_strings     : str= "",
            endswith_filter_strings     : str= "",
            parent:QWidget= None,
            ):

        super().__init__(
            parent= parent,
            )

        self._file_extensions = file_extensions

        # --- Widgets --- #

        self.lineedit_startswith = QLineEdit(text= startswith_filter_strings, parent= self)
        self.lineedit_startswith.setPlaceholderText("Starts with ...")
        self.lineedit_startswith.editingFinished.connect(self.on_filter_strings_updated)
        self.lineedit_startswith.editingFinished.connect(self.on_startswith_update)
        
        self.lineedit_contains = QLineEdit(text= contains_filter_strings, parent= self)
        self.lineedit_contains.setPlaceholderText("Contains ...")
        self.lineedit_contains.editingFinished.connect(self.on_filter_strings_updated)
        self.lineedit_contains.editingFinished.connect(self.on_contains_update)

        self.lineedit_endswith = QLineEdit(text= endswith_filter_strings, parent= self)
        self.lineedit_endswith.setPlaceholderText("Ends with ...")
        self.lineedit_endswith.editingFinished.connect(self.on_filter_strings_updated)
        self.lineedit_endswith.editingFinished.connect(self.on_endswith_update)

        # --- Layout --- #

        layout_main_h = QHBoxLayout()
        layout_main_h.addWidget(self.lineedit_startswith)
        layout_main_h.addWidget(self.lineedit_contains)
        layout_main_h.addWidget(self.lineedit_endswith)
        #layout_main_h.addStretch(0)
        layout_main_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_main_h.setSpacing(2)
        layout_main_h.setContentsMargins(0,0,0,0)
        
        self.setLayout(layout_main_h)

    @Slot()
    def on_filter_strings_updated(self):

        self.filterStringsUpdated.emit( self.lineedit_startswith.text(), self.lineedit_contains.text(), self.lineedit_endswith.text() )

    @Slot()
    def on_startswith_update(self): # text:str):

        self.startswithUpdated.emit( self.lineedit_startswith.text() )

    @Slot()
    def on_contains_update(self): #, text:str):
        
        self.containsUpdated.emit( self.lineedit_contains.text() )

    @Slot()
    def on_endswith_update(self): #, text:str):
        
        self.endswithUpdated.emit( self.lineedit_endswith.text() )

# --- File Tree --- #

files_through_filter = []

class QFileTree(QWidget):

    selectedFilesChanged = Signal(list)
    selectedDirChanged   = Signal(list)

    def __init__(self,
            local_working_dir : WorkingDir       = None,
            # --- Selection Settings --- #
            selectable_row          : bool= True, 
            single_selection        : bool= False,
            # --- Filter Settings --- #
            file_extensions             : list[str]= [],
            startswith_filter_strings   : str= "",
            contains_filter_strings     : str= "",
            endswith_filter_strings     : str= "",
            # --- Other --- #
            scrollbar_on_the_left   : bool= False,
            parent:QWidget= None
            ):

        super().__init__(
            parent= parent,
            )
        
        global GLOBAL_WORKING_DIR
        self._local_working_dir = local_working_dir if local_working_dir is not None else GLOBAL_WORKING_DIR
        self._local_working_dir.changed.connect(self.localPathUpdated)

        self._selectable_row        = selectable_row
        self._single_selection      = single_selection
        self._scrollbar_on_the_left = scrollbar_on_the_left

        # --- Model --- #

        self.model = QSelectableFileSystemModel(
            selectable_row   = self._selectable_row,
            single_selection = self._single_selection,
            parent= self
            )
        
        self.model.selectedFilesChanged.connect(self.selectedFilesChanged.emit)
        self.model.selectedDirChanged.connect(self.selectedDirChanged.emit)

        # --- Proxy --- #

        self.proxy = QFileFilterProxy(
            file_extensions           = file_extensions,
            startswith_filter_strings = startswith_filter_strings,
            contains_filter_strings   = contains_filter_strings,
            endswith_filter_strings   = endswith_filter_strings,
            parent= self
            )
        self.proxy.setSourceModel(self.model)
        self.model.proxy = self.proxy

        # --- View --- #

        self.tree = QFileSystemTreeView(parent= self)
        self.tree.setModel(self.proxy)
        self.tree.header().sectionClicked.connect(self.onHeaderClicked)

        # --- #

        root_path = self._local_working_dir.abspath()

        root_index = self.model.setRootPath(root_path)

        self.tree.setRootIndex(root_index)

        self.proxy._block = False

        # --- Layout --- #

        if self._scrollbar_on_the_left:

            verticalScrollBar = self.tree.verticalScrollBar()
            self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            layout = QHBoxLayout()
            layout.addWidget(verticalScrollBar)
            layout.addWidget(self.tree)
            layout.setSpacing(0)
            layout.setContentsMargins(1,1,1,1)    

        else:
            
            layout = QVBoxLayout()
            layout.addWidget(self.tree)
            layout.setContentsMargins(1,1,1,1)            

        self.setLayout(layout)

    @Slot(str)
    def localPathUpdated(self, root_path:str):

        root_index = self.model.setRootPath(root_path)

        #self.proxy.setSourceModel(self.model)        
        #self.tree.setModel(self.proxy)
        
        self.tree.setRootIndex(root_index)

        self.selectedFilesChanged.emit([])
        self.selectedDirChanged.emit([])

    @Slot(str,str,str)
    def updateFilterStrings(self, startswith:str, contains:str, endswith:str):

        self.proxy.setFilterStrings(startswith, contains, endswith)

        self.proxy.beginFilterChange()
        self.proxy.endFilterChange()
        
        self.tree.setRootIndex(self.model.index(self.model.rootPath())) 

        self.selectedFilesChanged.emit( self.model.getSelectedFiles() )
        self.selectedDirChanged.emit( self.model.getSelectedFiles() )

    @Slot(int)
    def onHeaderClicked(self, selected_column: int):
        
        current_column = self.tree.header().sortIndicatorSection()
        current_order  = self.tree.header().sortIndicatorOrder()

        if selected_column == current_column: 
            new_order = Qt.SortOrder.DescendingOrder if current_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder

        else:
            new_order = Qt.SortOrder.AscendingOrder

        new_mode = QFileFilterProxy.column_to_sort_mode.get(selected_column, "name")

        self.proxy.setSortSettings(new_mode, new_order)

@dataclass
class FileAndDirInfo:

    abspath     : str
    parentDir   : str = field(default="")
    size        : int = field(default=0)
    displaySize : str = field(default="")
    checkState  : Qt.CheckState = field(default=Qt.CheckState.Unchecked)
    isDir       : bool = field(default=False)
    directDirCount  : int = field(default=-1)
    directFileCount : int = field(default=-1)
    fullDirCount    : int = field(default=-1)
    fullFileCount   : int = field(default=-1)

    def __post_init__(self):

        self.displaySize = format_file_size(self.size)

class QSelectableFileSystemModel(QFileSystemModel):

    selectedFilesChanged = Signal(list)
    selectedDirChanged   = Signal(list)

    def __init__(self, 
            selectable_row          : bool= True, 
            single_selection        : bool= False,
            parent= None
            ):
    
        super().__init__(
            parent= parent,
            )

        self._selectable_row        = selectable_row
        self._single_selection      = single_selection

        self._data : dict[str, FileAndDirInfo] = {}
        self._last_index: QModelIndex | None = None

        self.setIconProvider(QFileIconProvider())

        self.setFilter( QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.Hidden)
    
    @wait_cursor
    def setRootPath(self, path:str):

        root_index = super().setRootPath(path)

        self._data = {}
        self.populateData(root_index)

        return root_index

    def populateData(self, index: QModelIndex) -> tuple[int,int,int]:

        dirInfo   = self.fileInfo(index)
        abspath   = dirInfo.absoluteFilePath()
        dirObject = QDir(abspath)

        directDirs  = dirObject.entryInfoList(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        directFiles = dirObject.entryInfoList(QDir.Filter.Files)

        directDirCount  = len( directDirs )
        directFileCount = len( directFiles )

        totalFileSize = 0

        for file_info in directFiles:

            totalFileSize += file_info.size()
            
            self._data[file_info.absoluteFilePath()] = FileAndDirInfo(
                abspath    = file_info.absoluteFilePath(),
                parentDir  = dirInfo.absoluteDir().path(),
                size       = file_info.size(),
                checkState = Qt.CheckState.Unchecked,
                isDir      = False,
                directDirCount  = -1,
                directFileCount = -1,
                fullDirCount    = -1,
                fullFileCount   = -1,
            )

        #totalFileSize = sum([ file_info.size() for file_info in directFiles ])

        if directDirCount == 0:
            self._data[abspath] = FileAndDirInfo(
                abspath    = abspath,
                parentDir  = dirInfo.absoluteDir().path(),
                size       = totalFileSize,
                checkState = Qt.CheckState.Unchecked,
                isDir      = True,
                directDirCount  = directDirCount,
                directFileCount = directFileCount,
                fullDirCount    = directDirCount,
                fullFileCount   = directFileCount,
            )
            return directDirCount, directFileCount, totalFileSize
        
        totalSubDirCount = 0
        totalSubFileCount = 0
        totalSubDirSize = 0

        for subDirInfo in directDirs:

            sub_dir_index = self.index(subDirInfo.absoluteFilePath())
            subDirCount, subFileCount, subDirSize = self.populateData(sub_dir_index)

            totalSubDirCount += subDirCount
            totalSubFileCount += subFileCount
            totalSubDirSize += subDirSize

        self._data[abspath] = FileAndDirInfo(
            abspath   = abspath,
            parentDir = dirInfo.absoluteDir().path(),
            size      = totalFileSize + totalSubDirSize,
            checkState = Qt.CheckState.Unchecked,
            isDir      = True,
            directDirCount  = directDirCount,
            directFileCount = directFileCount,
            fullDirCount    = directDirCount + totalSubDirCount,
            fullFileCount   = directFileCount + totalSubFileCount,
        )

        return directDirCount, directFileCount, totalFileSize

    def flags(self, index: QModelIndex):

        if self._selectable_row and index.column() == 0:

            return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable

        return super().flags(index)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole): # = Qt.ItemDataRole.DisplayRole):

        if self._selectable_row and index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole and self.filePath(index) in self._data:

            if self._single_selection: 
                if not self.fileInfo(index).isDir():
                    return self._data[self.filePath(index)].checkState
            else:
                return self._data[self.filePath(index)].checkState

        if index.column() == 1 and role == Qt.ItemDataRole.DisplayRole and self.filePath(index) in self._data:
            return self._data[self.filePath(index)].displaySize

        return super().data(index, role)

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole):
        
        if index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:

            if self._single_selection:

                if self._last_index is not None:
                    
                    self._data[self.filePath(self._last_index)].checkState = Qt.CheckState.Unchecked
                    self.dataChanged.emit(self._last_index, self._last_index, [Qt.ItemDataRole.DisplayRole])

                    self._last_index = None if self._last_index == index else index

                else:
                    self._last_index = index

            self._data[self.filePath(index)].checkState = value

            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            
            if self.isDir(index) and self.hasChildren(index):
                self.setChildrenData(index, value)

            self.selectedFilesChanged.emit( self.getSelectedFiles() )
            self.selectedDirChanged.emit( self.getSelectedDirs() )

            return True
        
        return super().setData(index, value, role)

    @wait_cursor
    def setChildrenData(self, parent_index: QModelIndex, value:Qt.CheckState):

        if not parent_index.isValid():
            return

        dir_iterator = QDirIterator(self.filePath(parent_index), self.filter() ) #  | QDir.Filter.NoDotAndDotDot

        while dir_iterator.hasNext():

            child_path = dir_iterator.next()
            child_index = self.index(child_path)

            self._data[child_path].checkState = value

            self.dataChanged.emit(child_index, child_index, [Qt.ItemDataRole.CheckStateRole])

            if self.isDir(child_index) and self.hasChildren(child_index):
                self.setChildrenData(child_index, value)

    def getSelectedFiles(self) -> list[str]:
        
        return [ path for path, file_and_dir_info in self._data.items() if file_and_dir_info.checkState == 2 and not file_and_dir_info.isDir ]

    def getSelectedDirs(self) -> list[str]:
        
        return [ path for path, file_and_dir_info in self._data.items() if file_and_dir_info.checkState == 2 and file_and_dir_info.isDir ]
    
class QFileFilterProxy(QSortFilterProxyModel):

    filterUpdated = Signal()
    sortUpdated = Signal()

    column_to_sort_mode = {
        0: "name",
        1: "size",
        2: "type",
        3: "date"
    }

    def __init__(self, 
            file_extensions             : list[str]= [],
            startswith_filter_strings   : str= "",
            contains_filter_strings     : str= "",
            endswith_filter_strings     : str= "",
            parent:QObject= None,
            ):

        super().__init__(
            parent= parent,
            )
        
        self.setRecursiveFilteringEnabled(True)
        self.setDynamicSortFilter(True)
        
        self._file_extensions = [ext.strip(".") for ext in file_extensions]
        self._startswith      = startswith_filter_strings
        self._contains        = contains_filter_strings
        self._endswith        = endswith_filter_strings

        self._sort_mode = "name" # 'name', 'size', 'type', 'date'
        self._sort_order = Qt.SortOrder.AscendingOrder

        self._block = True

    def setSourceModel(self, sourceModel:QSelectableFileSystemModel):

        #super().setSourceModel(None)

        return super().setSourceModel(sourceModel)

        #QTimer.singleShot(0, lambda: super().setSourceModel(sourceModel))

        self.invalidate()

        #self._startswith = ""
        #self._contains = ""
        #self._endswith = ""

        #self._sort_mode = "name" # 'name', 'size', 'type', 'date'
        #self._sort_order = Qt.SortOrder.AscendingOrder

    # --- Filtering --- #

    def setFilterStrings(self, startswith:str, contains:str, endswith:str):

        self._startswith = startswith
        self._contains = contains
        self._endswith = endswith

    def filterAcceptsRow(self, source_row:int, source_parent:QModelIndex):

        if self._block:
            return True

        model:QSelectableFileSystemModel = self.sourceModel()
        model_root_path = model.rootDirectory().absolutePath()
        index = model.index(source_row, 0, source_parent)

        if not index.isValid():
            return False

        parent_info = model.fileInfo(source_parent)
        file_info = model.fileInfo(index)

        #parent_path = parent_info.absoluteFilePath()

        name = file_info.fileName()
        ext = file_info.suffix()
        path = file_info.absoluteFilePath()

        # print(ext, self._file_extensions, ext == "", bool(self._file_extensions), ext in self._file_extensions)

        # print(parent_path in model_root_path, file_info.isRoot() and model_root_path != "",  model_root_path, parent_path, path, )

        if path in model_root_path:
            if path in model._data:
                model._data[path].checkState = Qt.CheckState.Unchecked
            return False
        
        if file_info.isRoot() and model_root_path != "":
            if path in model._data:
                model._data[path].checkState = Qt.CheckState.Unchecked
            return False

        if self._file_extensions and ext != "" and ext not in self._file_extensions:
            return False
        
        if not (self._startswith or self._contains or self._endswith):
            return True

        if self._startswith and name.startswith(self._startswith):
            return True
        
        if self._contains and self._contains in name:
            return True
        
        if self._endswith and name.endswith(self._endswith):
            return True

        if path in model._data:
            model._data[path].checkState = Qt.CheckState.Unchecked
        return False

    # --- Sorting --- #

    def setSortSettings(self, mode:str, order:Qt.SortOrder):

        self._sort_mode = mode 
        self._sort_order = order
        self.invalidate()

    def lessThan(self, left: QModelIndex, right: QModelIndex):

        model: QFileSystemModel = self.sourceModel()

        left_info  = model.fileInfo(left)
        right_info = model.fileInfo(right)

        if left_info.isDir() and not right_info.isDir():
            return True
        
        if not left_info.isDir() and right_info.isDir():
            return False
        
        if self._sort_mode == 'name':
            if self._sort_order == Qt.SortOrder.AscendingOrder:
                return left_info.fileName().lower() < right_info.fileName().lower()
            elif self._sort_order == Qt.SortOrder.DescendingOrder:
                return left_info.fileName().lower() > right_info.fileName().lower()

        if self._sort_mode == 'size':

            if self._sort_order == Qt.SortOrder.AscendingOrder:
                return left_info.size() < right_info.size()
            elif self._sort_order == Qt.SortOrder.DescendingOrder:
                return left_info.size() > right_info.size()

        if self._sort_mode == 'type':

            if self._sort_order == Qt.SortOrder.AscendingOrder:
                return left_info.suffix().lower() < right_info.suffix().lower()
            elif self._sort_order == Qt.SortOrder.DescendingOrder:
                return left_info.suffix().lower() > right_info.suffix().lower()
        
        if self._sort_mode == 'date':

            if self._sort_order == Qt.SortOrder.AscendingOrder:
                return left_info.lastModified() < right_info.lastModified()
            elif self._sort_order == Qt.SortOrder.DescendingOrder:
                return left_info.lastModified() > right_info.lastModified()
        
        raise

class QFileSystemTreeView(QTreeView):

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

        self.setSortingEnabled(True)

        self.header().setSectionsClickable(True)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    def setModel(self, model: QSelectableFileSystemModel | QFileFilterProxy):

        super().setModel(model)

        self.setColumnWidth(0, 250)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    def setRootIndex(self, index:QModelIndex):

        model = self.model()

        if isinstance(model, QFileFilterProxy):
            
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













