# File: SetupProject.py
# Path: ~/Desktop/PikaPeek/SetupProject.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-09
# Last Modified: 2025-07-09 05:11PM
"""
Description: Initializes the PikaPeek project folder with a PySide6-based GUI structure,
Himalaya-compliant headers, and all dependencies required to begin development of a 
Borg snapshot explorer and analyzer tool.

Run this script from the root of your new project directory.
"""

import os
import subprocess
from datetime import datetime

ProjectName = "PikaPeek"
ModuleList = ["Gui", "Core", "Assets", "Config", "Docs"]
RequirementsList = ["PySide6"]  # borgbackup removed; install via apt

MainHeader = f"""# File: Main.py
# Path: ~/Desktop/{ProjectName}/Main.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-09
# Last Modified: {datetime.now().strftime('%Y-%m-%d %I:%M%p')}
"""

MainDocstring = '''"""
Description: Launches the PikaPeek PySide6 GUI application.
This is the entry point for exploring, mounting, and analyzing Borg backup snapshots.
"""'''

MainContent = f"""{MainHeader}{MainDocstring}

import sys
from PySide6.QtWidgets import QApplication
from Gui.GuiMain import GuiMain

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Window = GuiMain()
    Window.show()
    sys.exit(App.exec())
"""

GuiMainContent = f"""# File: GuiMain.py
# Path: ~/Desktop/{ProjectName}/Gui/GuiMain.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-09
# Last Modified: {datetime.now().strftime('%Y-%m-%d %I:%M%p')}
"""
GuiMainDocstring = '''"""
Description: Primary window for the PikaPeek application.
Includes interface for listing, mounting, and inspecting Borg backups.
"""'''

GuiMainBody = """
from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtCore import Qt

class GuiMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PikaPeek 🐭🔍")
        self.setMinimumSize(800, 600)
        self.InitUI()

    def InitUI(self):
        Label = QLabel("Welcome to PikaPeek!\nUse the menu to load and explore Borg backups.", self)
        Label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(Label)
"""

GuiMainContent += GuiMainDocstring + GuiMainBody

def CreateStructure():
    print(f"🛠️ Creating project structure for {ProjectName}...")
    for ModuleName in ModuleList:
        os.makedirs(ModuleName, exist_ok=True)
    open("Main.py", "w").write(MainContent)
    os.makedirs("Gui", exist_ok=True)
    open("Gui/GuiMain.py", "w").write(GuiMainContent)
    open("Requirements.txt", "w").write("\n".join(RequirementsList))
    print("✅ Structure created.")

def CreateVenv():
    print("🐍 Creating virtual environment...")
    subprocess.run(["python3", "-m", "venv", ".venv"])
    print("✅ .venv created.")

def InstallDependencies():
    print("📦 Installing dependencies...")
    subprocess.run([".venv/bin/pip", "install", "--upgrade", "pip"])
    subprocess.run([".venv/bin/pip", "install", "-r", "Requirements.txt"])
    print("✅ Dependencies installed.")
    print("⚠️  NOTE: 'borgbackup' must be installed via apt (sudo apt install borgbackup)")

if __name__ == "__main__":
    CreateStructure()
    CreateVenv()
    InstallDependencies()
    print("🎉 PikaPeek project initialized successfully.")
