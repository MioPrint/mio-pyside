
def format_file_size(file_size) -> str:

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if file_size < 1024:
            return f"{file_size:.1f} {unit}"
        file_size /= 1024
    return f"{file_size:.1f} PB"










