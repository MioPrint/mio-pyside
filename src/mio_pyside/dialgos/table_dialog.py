import json
from typing import List, Dict, Any

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPlainTextEdit,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt


# =========================================================
# 1) JSON TEXT VIEWER DIALOG
# =========================================================

class JsonViewerDialog(QDialog):
    """
    Dialog that displays a JSON-serializable dict
    inside an editor-style text field.
    """

    def __init__(self, data: Dict[str, Any], parent=None):
        super().__init__(parent)

        self.setWindowTitle("JSON Viewer")
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        self.editor = QPlainTextEdit(self)
        self.editor.setReadOnly(True)
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        # monospaced font improves readability
        font = self.editor.font()
        font.setFamily("Consolas")
        font.setStyleHint(font.Monospace)
        self.editor.setFont(font)

        layout.addWidget(self.editor)

        # pretty-print JSON
        try:
            text = json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            text = f"Invalid JSON data:\n{e}"

        self.editor.setPlainText(text)


# =========================================================
# 2) DATAFRAME TABS DIALOG
# =========================================================

class DataFrameTabsDialog(QDialog):
    """
    Accepts list[list[dict]].

    Each outer element = one tab.
    Inner list = rows.
    Dict keys = columns.
    """

    def __init__(self, frames: List[List[Dict[str, Any]]], parent=None):
        super().__init__(parent)

        self.setWindowTitle("DataFrames Viewer")
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        self._build_tabs(frames)

    # -------------------------

    def _build_tabs(self, frames: List[List[Dict[str, Any]]]):
        for idx, frame in enumerate(frames):
            table = self._create_table(frame)
            self.tabs.addTab(table, f"Table {idx}")

    # -------------------------

    def _create_table(self, data: List[Dict[str, Any]]) -> QTableWidget:
        table = QTableWidget()

        if not data:
            table.setRowCount(0)
            table.setColumnCount(0)
            return table

        # Collect columns (union of all keys)
        columns = sorted({k for row in data for k in row.keys()})

        table.setColumnCount(len(columns))
        table.setRowCount(len(data))
        table.setHorizontalHeaderLabels(columns)

        # Fill cells
        for row_idx, row in enumerate(data):
            for col_idx, key in enumerate(columns):
                value = row.get(key, "")
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                table.setItem(row_idx, col_idx, item)

        # nicer resizing
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        table.verticalHeader().setVisible(False)

        return table


# =========================================================
# Example usage (optional test)
# =========================================================

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # ---- JSON dialog example ----
    json_data = {"name": "Alice", "age": 30, "items": [1, 2, 3]}
    dlg1 = JsonViewerDialog(json_data)
    dlg1.show()

    # ---- DataFrame tabs example ----
    frames = [
        [
            {"a": 1, "b": 2},
            {"a": 3, "b": 4},
        ],
        [
            {"x": "hello", "y": 9.5},
            {"x": "world", "y": 2.1},
        ],
    ]

    dlg2 = DataFrameTabsDialog(frames)
    dlg2.show()

    sys.exit(app.exec())
