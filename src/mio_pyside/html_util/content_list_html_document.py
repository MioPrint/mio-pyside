
import base64, imghdr

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWebEngineWidgets import QWebEngineView

import numpy as np
import pandas as pd

from .basic_html_document import BasicHtmlDocumentWidget

class ContentListHtmlDocumentWidget(BasicHtmlDocumentWidget):

    def __init__(self,
            parent:QWidget= None,
            *args, **kwargs
            ):

        super().__init__(
            parent= parent, 
            *args, **kwargs
            )

        self.html_content_list = []

    ### SETs ###

    @Slot(list)
    def set_html_content_list(self, html_content_list:list):

        self.html_content_list = html_content_list

        self.html_string = get_html_string_from_content_list(self.html_content_list)

        self.web_engine_view_widget.setHtml(self.html_string)

        self.html_updated.emit(self.html_string)

def get_html_string_from_content_list(content_list:list) -> str:

    head_string = get_html_head_string(indent= 1)
    body_string = get_html_body_string(content_list= content_list, indent= 1)    

    html_string = f"\n<!DOCTYPE html>\n<html lang=\"en\">\n{head_string}\n{body_string}\n</html>\n"

    return html_string

def get_html_head_string(indent:int=1):

    style_string = get_html_style_string(indent=indent+1)

    head_string = format_html_content('head', style_string, indent)
    return head_string

def get_html_style_string(indent:int=2):

    style_content = f"""
    p {{
        font-family: "Courier New", Courier, monospace;
        font-size: 16px;
    }}
    table {{
        border-collapse: collapse;
        width: auto;
    }}
    th, td {{
        border: 1px solid black;
        font-family: "Courier New", Courier, monospace;
        font-size: 16px;
        text-align: center;
        padding: 5px;
    }}
    img {{
        padding: 10px;
    }}
    .borderless_table {{
        border: none;
        border-collapse: collapse;
        width: auto;
    }}
    .borderless_table > tbody > tr > td {{
        border: none;
    }}
    """  
    
    line_list = []
    for line in style_content.split('\n'):
        line = f"\n{'\t'*(indent+1)}{line}"
        line_list.append(line)
    style_content = ''.join(line_list)

    style_string = format_html_content('style', style_content, indent)
    return style_string

def get_html_body_string(content_list:list, indent:int=1):

    body_content = process_content_list_vertically(content_list, indent=indent+1)
    body_string = format_html_content('body', body_content, indent)
    return body_string

### Section / Paragraph ###

def get_html_section_paragraph_from_str(input_str:str, indent:int=2):

    paragraph_indent = "\t"*(indent+1)
    paragraph_string = f"\n{paragraph_indent}<p>{input_str}</p>"

    section_string = format_html_content('section', paragraph_string, indent)
    return section_string

### Table ###

def get_html_table_string_from_df(input_df:pd.DataFrame, indent:int=2):

    table_name = input_df.attrs['table_name'] if 'table_name' in input_df.attrs.keys() else ''
    is_images_table = input_df.attrs['images_table'] if 'images_table' in input_df.attrs.keys() else False
    drop_index = input_df.attrs['drop_index'] if 'drop_index' in input_df.attrs.keys() else False
    drop_column_names = input_df.attrs['drop_column_names'] if 'drop_column_names' in input_df.attrs.keys() else False

    table_args = {}
    if 'borderless' in input_df.attrs.keys():
        table_args['class'] = 'borderless_table'

    row_strings_list = []

    if not drop_column_names:
        column_names_as_row_string = get_html_row_string_from_df_series(input_series=input_df.columns, row_label=table_name, indent=indent+1, parse_image=False)
        row_strings_list.append(column_names_as_row_string)

    for index, row in input_df.iterrows():
            
        if drop_index:
            row_as_string = get_html_row_string_from_df_series(input_series=row, indent=indent+1)
        else:
            row_as_string = get_html_row_string_from_df_series(input_series=row, row_label=index, indent=indent+1)

        row_strings_list.append(row_as_string)

    row_indent = "\t"*(indent+1)
    all_rows_string = f"{row_indent}{f'{row_indent}'.join(row_strings_list)}"

    table_string = format_html_content('table', all_rows_string, indent, table_args)
    return table_string

def get_html_row_string_from_df_series(input_series:pd.Series, row_label:str='', indent:int=3, parse_image:bool=True):

    cell_values_list = [row_label] + list(input_series.values)
    row_tds = []
    for cell_value in cell_values_list:
        tds_content = parse_variable(cell_value, parse_image=parse_image, str_as_paragraph=False, indent=indent+1)
        tds_string = format_html_content('td', tds_content, indent+1)
        row_tds.append(tds_string)

    tr_indent = "\t"*(indent)
    tr_content = f"\n{tr_indent}{f'\n{tr_indent}'.join(row_tds)}"

    row_string = format_html_content('tr', tr_content, indent)
    return row_string

### Util ###

def format_html_content(content_type:str, content_value:str, indent:int, arguments:dict={}):

    argument_string = ' '+' '.join([f'{key}="{value}"' for key, value in arguments.items()]) if arguments else ''

    return f"\n{'\t'*indent}<{content_type}{argument_string}>{content_value}\n{'\t'*indent}</{content_type}>"

def process_content_list_vertically(content_list:list, indent:int=1, break_on:bool=True):

    ver_string_list = []
    for html_content in content_list:

        html_element_string = parse_variable(html_content, indent= indent)
        ver_string_list.append(html_element_string)
        
    break_string = f"\n{'\t'*(indent+1)}<br/>" if break_on else f"\n{'\t'*(indent+1)}"
    return_content = break_string.join(ver_string_list)

    return return_content

def parse_variable(input_variable, parse_image:bool=True, str_as_paragraph:bool=True, indent:int=1):

    #print(type(input_variable))

    if isinstance(input_variable, str):
        html_element_string = parse_string(input_variable, parse_image=parse_image, str_as_paragraph=str_as_paragraph, indent= indent)
        return html_element_string

    if isinstance(input_variable, bool):
        html_element_string = parse_string(input_variable, parse_image=parse_image, str_as_paragraph=str_as_paragraph, indent= indent)
        return html_element_string

    if isinstance(input_variable, int):
        html_element_string = parse_string(input_variable, parse_image=parse_image, str_as_paragraph=str_as_paragraph, indent= indent)
        return html_element_string
    
    if isinstance(input_variable, float):
        html_element_string = parse_string(input_variable, parse_image=parse_image, str_as_paragraph=str_as_paragraph, indent= indent)
        return html_element_string
    
    if isinstance(input_variable, np.integer):
        html_element_string = parse_string(input_variable, parse_image=parse_image, str_as_paragraph=str_as_paragraph, indent= indent)
        return html_element_string
    
    if isinstance(input_variable, np.floating):
        html_element_string = parse_string(input_variable, parse_image=parse_image, str_as_paragraph=str_as_paragraph, indent= indent)
        return html_element_string
    
    if isinstance(input_variable, pd.DataFrame):

        html_element_string = get_html_table_string_from_df(input_variable, indent= indent)
        return html_element_string

    return ''

def parse_string(input_variable, parse_image:bool=True, str_as_paragraph:bool=True, indent:int=0):

    input_str = str(input_variable)

    if input_str.endswith('.png') and parse_image:
        return f'<img src="{input_str}">'
    
    if input_str.endswith('.jpeg') and parse_image:
        return f'<img src="{input_str}">'
    
    if input_str.endswith('.gif') and parse_image:
        return f'<img src="{input_str}">'
    
    if is_base64_image(input_str) and parse_image:
        return f'<img src="{input_str}">'

    if str_as_paragraph:
        
        return get_html_section_paragraph_from_str(input_variable, indent= indent)

    return input_str

def is_base64_image(b64_string:str) -> bool:

    try:

        # Remove the data URL scheme (if present) and decode the Base64 string
        if b64_string.startswith('data:image'):
            b64_string = b64_string.split(",")[1]
        
        # Decode the Base64 string
        decoded_data = base64.b64decode(b64_string)
        
        # Check if the decoded data corresponds to an image
        image_format = imghdr.what(None, decoded_data)
        
        return image_format is not None  # Returns True if it's an image format
    
    except (base64.binascii.Error, ValueError):
        # Raised if decoding fails or data is not valid Base64
        return False
