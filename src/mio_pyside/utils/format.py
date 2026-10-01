
def format_file_size(file_size) -> str:

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if file_size < 1024:
            return f"{file_size:.1f} {unit}"
        file_size /= 1024
    return f"{file_size:.1f} PB"

def sanitize_xml_text_value(text_value):

    if text_value == 'N/A' or text_value == '' or text_value == None:
        text_value = None

    else:
        if '.' in text_value:
            try: text_value = float(text_value)
            except ValueError: pass
        else:
            try: text_value = int(text_value)
            except ValueError: pass

    return text_value
