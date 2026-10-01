
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class TabsWithOrderMemory(QTabWidget):

    def __init__(self, 
            memory_dict:dict,
            memory_key:str,
            parent:QWidget=None,
            *args, **kwargs
            ):
        
        super().__init__(parent=parent, *args, **kwargs)

        self.memory_dict = memory_dict
        self.memory_key = memory_key

        self.init_tab = memory_dict.get(memory_key+'_init_tab', '')
        self.tab_order_list = memory_dict.get(memory_key+'_tab_order', [])

        self.tabBar().tabMoved.connect(self.on_tab_moved)
        self.tabBar().tabBarClicked.connect(self.on_tab_clicked)
        
        self.setMovable(True)

    @Slot(int)
    def on_tab_clicked(self, idx:int):
        
        self.init_tab = self.widget(idx).__class__.__name__
        self.memory_dict[self.memory_key+'_init_tab'] = self.init_tab
        
    @Slot(int, int)
    def on_tab_moved(self, from_idx:int, to_idx:int):

        self.tab_order_list = self.get_tab_order()
        self.memory_dict[self.memory_key+'_tab_order'] = self.tab_order_list
    
    def init_complete(self):

        self.set_tab_order()
        self.set_init_tab()

    def set_tab_order(self):
    
        if not self.tab_order_list:
            
            self.tab_order_list = self.get_tab_order()
            self.memory_dict[self.memory_key+'_tab_order'] = self.tab_order_list
            return 

        for to_idx, module_name in enumerate(self.tab_order_list):

            from_idx = self.get_tab_order().index(module_name)
            self.tabBar().moveTab(from_idx, to_idx)

    def set_init_tab(self):

        if not self.init_tab:
            self.init_tab = self.widget(0).__class__.__name__
            self.memory_dict[self.memory_key+'_init_tab'] = self.init_tab
            return
        
        self.setCurrentIndex(self.get_tab_order().index(self.init_tab))

    def get_tab_order(self) -> list:

        return [ str(self.widget(tab_idx).__class__.__name__) for tab_idx in range(self.count()) ]
