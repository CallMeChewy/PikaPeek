# File: ConfigDialog.py
# Path: Gui/ConfigDialog.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-10
# Last Modified: 2025-07-10 09:30AM
"""
Description: A dialog for configuring PikaPeek settings.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.layout = QVBoxLayout(self)

        # Borg executable path
        self.layout.addWidget(QLabel("Borg Executable Path:"))
        self.borg_path_edit = QLineEdit()
        self.layout.addWidget(self.borg_path_edit)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_for_borg)
        self.layout.addWidget(self.browse_button)

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.layout.addWidget(self.save_button)

    def _browse_for_borg(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Borg Executable")
        if path:
            self.borg_path_edit.setText(path)

    def get_borg_path(self):
        return self.borg_path_edit.text()

    def set_borg_path(self, path):
        self.borg_path_edit.setText(path)
