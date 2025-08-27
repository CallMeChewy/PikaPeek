# File: GuiMain.py
# Path: ~/Desktop/PikaPeek/Gui/GuiMain.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-09
# Last Modified: 2025-07-31 07:34PM
"""
Description: Primary window for the PikaPeek application.
Includes interface for listing, mounting, and inspecting Borg backups.
"""
from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtCore import Qt

class GuiMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PikaPeek 🐭🔍")
        self.setMinimumSize(800, 600)
        self.InitUI()

    def InitUI(self):
        Label = QLabel("Welcome to PikaPeek!
Use the menu to load and explore Borg backups.", self)
        Label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(Label)
