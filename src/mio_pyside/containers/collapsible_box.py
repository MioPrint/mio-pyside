
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from .scrollarea_for_collapsible_box import ScrollAreaForCollapsibleBoxes

class CollapsibleBox(QWidget):

    box_has_collapsed = Signal()
    box_has_expanded = Signal()
    box_has_changed = Signal()

    def __init__(self, 
            title= '', 
            init_collapsed= True, 
            direction= 'vertical', 
            animate:bool= False,
            minimum_width:int= None,
            parent:QWidget= None,
            ):

        super(CollapsibleBox, self).__init__(parent)

        if isinstance(parent, ScrollAreaForCollapsibleBoxes):
            self.box_has_changed.connect(parent.adjust_scroll_area_width)

        self.title = title
        self.box_collapsed = init_collapsed
        
        if direction in ['vertical','horizontal']:
            self.direction = direction  
        else:
            raise ValueError(' collapsible_box initialized with invalid direction')
        
        self.animate = animate

        self.minimum_width = minimum_width

        ### Toggle Button ###
        self.toggle_button = QToolButton(text=self.title)
        self.toggle_button.setStyleSheet('QToolButton { border: none; }')
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow if self.box_collapsed else Qt.ArrowType.DownArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        ### Content Area ###
        self.content_area = QScrollArea(minimumHeight=0, maximumHeight=0, minimumWidth=0, maximumWidth=0)
        
        ### Toggle Animation ###
        self.animation_property_box_min_height = QPropertyAnimation(self, b'minimumHeight')
        self.animation_property_box_max_height = QPropertyAnimation(self, b'maximumHeight')
        self.animation_property_box_min_width = QPropertyAnimation(self, b'minimumWidth')
        self.animation_property_box_max_width = QPropertyAnimation(self, b'maximumWidth')
        self.animation_property_content_area_max_height = QPropertyAnimation(self.content_area, b'maximumHeight')
        self.animation_property_content_area_max_width = QPropertyAnimation(self.content_area, b'maximumWidth')

        animation_duration = 100
        self.animation_property_box_min_height.setDuration(animation_duration)
        self.animation_property_box_max_height.setDuration(animation_duration)
        self.animation_property_box_min_width.setDuration(animation_duration)
        self.animation_property_box_max_width.setDuration(animation_duration)
        self.animation_property_content_area_max_height.setDuration(animation_duration)
        self.animation_property_content_area_max_width.setDuration(animation_duration)

        self.toggle_animation = QParallelAnimationGroup(self)
        self.toggle_animation.addAnimation(self.animation_property_box_min_height)
        self.toggle_animation.addAnimation(self.animation_property_box_max_height)
        self.toggle_animation.addAnimation(self.animation_property_box_min_width)
        self.toggle_animation.addAnimation(self.animation_property_box_max_width)
        self.toggle_animation.addAnimation(self.animation_property_content_area_max_height)
        self.toggle_animation.addAnimation(self.animation_property_content_area_max_width)

        ### Layout ###
        if self.direction == 'vertical':
            layout_toggle_button = QVBoxLayout()
        elif self.direction == 'horizontal':
            layout_toggle_button = QHBoxLayout()

        layout_toggle_button.setSpacing(0)
        layout_toggle_button.setContentsMargins(0,0,0,0)
        layout_toggle_button.addWidget(self.toggle_button)
        layout_toggle_button.addWidget(self.content_area)

        self.setLayout(layout_toggle_button)

    def on_pressed(self):

        self.box_collapsed = not self.box_collapsed
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow if self.box_collapsed else Qt.ArrowType.DownArrow)

        if self.animate:
            self.toggle_animation.setDirection(QAbstractAnimation.Direction.Backward if self.box_collapsed else QAbstractAnimation.Direction.Forward)
            self.toggle_animation.start()
        else:
            self.set_widths_and_heights()

        self.box_has_changed.emit()
        self.box_has_collapsed.emit() if self.box_collapsed else self.box_has_expanded.emit()

    def set_contents_layout(self, layout:QBoxLayout):
        
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        self.update_contents_layout()
        
    def update_contents_layout(self):
        
        toggle_button_height = self.toggle_button.sizeHint().height()
        toggle_button_width = self.toggle_button.sizeHint().width() 
        
        self.content_area_height = self.content_area.layout().sizeHint().height()
        self.content_area_width = self.content_area.layout().sizeHint().width() if self.minimum_width is None else max(self.minimum_width, self.content_area.layout().sizeHint().width())
        
        self.box_collapsed_height = toggle_button_height
        self.box_collapsed_width = toggle_button_width
        
        if self.direction == 'vertical':
            self.box_expanded_height = toggle_button_height + self.content_area_height
            self.box_expanded_width = max(toggle_button_width, self.content_area_width)
            
        elif self.direction == 'horizontal':
            self.box_expanded_height = max(toggle_button_height, self.content_area_height)
            self.box_expanded_width = toggle_button_width + self.content_area_width

        if False:
            print()
            print(self.title)
            heights = ['height', toggle_button_height, content_area_height, box_expanded_height]
            widths = ['width', toggle_button_width, content_area_width, box_expanded_width]
            columns = ['type','toggle_button','content_area','box_expanded']
            import pandas as pd
            df = pd.DataFrame([heights,widths], columns=columns)
            print(df)
            print()

        self.animation_property_box_min_height.setStartValue(self.box_collapsed_height)
        self.animation_property_box_max_height.setStartValue(self.box_collapsed_height)
        self.animation_property_box_min_width.setStartValue(self.box_collapsed_width)
        self.animation_property_box_max_width.setStartValue(self.box_collapsed_width)
        self.animation_property_content_area_max_height.setStartValue(0)
        self.animation_property_content_area_max_width.setStartValue(0)
        
        self.animation_property_box_min_height.setEndValue(self.box_expanded_height)
        self.animation_property_box_max_height.setEndValue(self.box_expanded_height)
        self.animation_property_box_min_width.setEndValue(self.box_expanded_width)
        self.animation_property_box_max_width.setEndValue(self.box_expanded_width)
        self.animation_property_content_area_max_height.setEndValue(self.content_area_height)
        self.animation_property_content_area_max_width.setEndValue(self.content_area_width)

        self.set_widths_and_heights()
        self.box_has_changed.emit()

    def set_collapsed(self):

        self.box_collapsed = True
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.update_contents_layout()

    def set_expanded(self):

        self.box_collapsed = False
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        self.update_contents_layout()

    def is_collapsed(self):
        return self.box_collapsed
    
    def is_expanded(self):
        return not self.box_collapsed
    
    def set_widths_and_heights(self):

        if self.box_collapsed:
            self.setMinimumHeight(self.box_collapsed_height)
            self.setMaximumHeight(self.box_collapsed_height)
            self.setMinimumWidth(self.box_collapsed_width)
            self.setMaximumWidth(self.box_collapsed_width)
            self.content_area.setMaximumHeight(0)
            self.content_area.setMaximumWidth(0)

        else:
            self.setMinimumHeight(self.box_expanded_height)
            self.setMaximumHeight(self.box_expanded_height)
            self.setMinimumWidth(self.box_expanded_width)# if self.minimum_width is None else max(self.minimum_width, self.box_expanded_width))
            self.setMaximumWidth(self.box_expanded_width)# if self.minimum_width is None else max(self.minimum_width, self.box_expanded_width))
            self.content_area.setMaximumHeight(self.content_area_height)
            self.content_area.setMaximumWidth(self.content_area_width)

class CollapsibleBox_template(CollapsibleBox):

    def __init__(self,
            parent:QWidget= None,
            ):

        super(CollapsibleBox_template, self).__init__(
            title= 'CollapsibleBox_template', 
            init_collapsed= True, 
            direction= 'vertical', 
            parent= parent,
            )

        #self.content_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.init_widgets()
        self.init_layout()

    def init_widgets(self):

        pass

    def init_layout(self):

        layout_collapsible_box_template = QGridLayout()

        self.set_contents_layout(layout_collapsible_box_template)

    ### CONFIGURE WIDGETS ###
    
    ### WIDGET SIGNALS ###
    
    ### UPDATEs ###

    ### SETs ###

    ### GETs ###
