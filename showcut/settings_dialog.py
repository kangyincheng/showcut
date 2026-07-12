"""
Custom keyboard shortcuts settings dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QLabel, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence, QFont


DEFAULT_SHORTCUTS = {
    "start_capture": "Ctrl+Shift+A",
    "rect_tool": "R",
    "ellipse_tool": "E",
    "line_tool": "L",
    "arrow_tool": "A",
    "polygon_tool": "P",
    "text_tool": "T",
    "undo": "Ctrl+Z",
    "redo": "Ctrl+Shift+Z",
    "save": "Ctrl+S",
    "copy": "Ctrl+C",
    "toggle_ortho": "Shift",
}


class ShortcutEdit(QLineEdit):
    shortcutChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Press key...")
        self._current_key = ""

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clear()
            self.shortcutChanged.emit("")
            return
        if event.key() == Qt.Key_Backspace:
            self.clear()
            self.shortcutChanged.emit("")
            return
        key = event.key()
        modifiers = event.modifiers()
        key_sequence = QKeySequence(modifiers | key)
        key_str = key_sequence.toString(QKeySequence.PortableText)
        if key_str:
            self.setText(key_str)
            self.shortcutChanged.emit(key_str)

    def set_shortcut(self, shortcut):
        self.setText(shortcut)


class SettingsDialog(QDialog):
    def __init__(self, shortcuts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Shortcut Settings")
        self.setMinimumSize(500, 500)
        self._shortcuts = dict(shortcuts)
        self._defaults = dict(DEFAULT_SHORTCUTS)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Custom Shortcuts")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        self.table = QTableWidget(len(self._shortcuts), 2, self)
        self.table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        action_names = {
            "start_capture": "Start Capture",
            "rect_tool": "Rectangle Tool",
            "ellipse_tool": "Ellipse Tool",
            "line_tool": "Line Tool",
            "arrow_tool": "Arrow Tool",
            "polygon_tool": "Polygon Tool",
            "text_tool": "Text Tool",
            "undo": "Undo",
            "redo": "Redo",
            "save": "Save",
            "copy": "Copy to Clipboard",
            "toggle_ortho": "Toggle Orthogonal Mode",
        }

        self._shortcut_edits = {}
        row = 0
        for key, shortcut in self._shortcuts.items():
            name = action_names.get(key, key)
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item)
            edit = ShortcutEdit()
            edit.set_shortcut(shortcut)
            edit.shortcutChanged.connect(lambda s, k=key: self._on_shortcut_changed(k, s))
            self.table.setCellWidget(row, 1, edit)
            self._shortcut_edits[key] = edit
            row += 1

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.reset_btn = QPushButton("Reset Defaults")
        self.reset_btn.clicked.connect(self._reset_defaults)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _on_shortcut_changed(self, key, shortcut):
        if not shortcut:
            self._shortcuts[key] = ""
            return
        for k, v in self._shortcuts.items():
            if k != key and v == shortcut:
                QMessageBox.warning(self, "Shortcut Conflict",
                    f"Shortcut \"{shortcut}\" is already in use.")
                self._shortcut_edits[key].set_shortcut(self._shortcuts[key])
                return
        self._shortcuts[key] = shortcut

    def _reset_defaults(self):
        reply = QMessageBox.question(self, "Reset Defaults",
            "Reset all shortcuts to defaults?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._shortcuts = dict(self._defaults)
            for key, edit in self._shortcut_edits.items():
                edit.set_shortcut(self._defaults.get(key, ""))

    def get_shortcuts(self):
        return dict(self._shortcuts)


def load_shortcuts(settings):
    shortcuts = dict(DEFAULT_SHORTCUTS)
    for key in DEFAULT_SHORTCUTS:
        val = settings.value(f"shortcuts/{key}", "")
        if val:
            shortcuts[key] = val
    return shortcuts


def save_shortcuts(settings, shortcuts):
    for key, value in shortcuts.items():
        settings.setValue(f"shortcuts/{key}", value)
