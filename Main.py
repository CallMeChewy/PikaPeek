# File: Main.py
# Path: ~/Desktop/PikaPeek/Main.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-09
# Last Modified: 2025-07-31 07:34PM
"""
Description: Launches the PikaPeek PySide6 GUI application.
This is the entry point for exploring, mounting, and analyzing Borg backup snapshots.
"""

import sys
from PySide6.QtWidgets import QApplication
from Gui.GuiMain import GuiMain

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Window = GuiMain()
    Window.show()
    sys.exit(App.exec())
