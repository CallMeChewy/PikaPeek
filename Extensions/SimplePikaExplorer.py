#!/usr/bin/env python3
# File: SimplePikaExplorer.py
# Path: /home/herb/SimplePikaExplorer.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-29
# Last Modified: 2025-07-29 06:05AM
"""
Simple PySide6 Backup Explorer - Basic version that should work reliably
"""

import sys
import os
import subprocess
import shutil
from datetime import datetime

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QListWidget, QTableWidget, QTableWidgetItem, QLabel, QPushButton,
        QComboBox, QMessageBox, QTextEdit, QSplitter, QAbstractItemView
    )
    from PySide6.QtCore import Qt, QThread, Signal
except ImportError:
    print("PySide6 not available. Please install with: pip install PySide6")
    sys.exit(1)

class SimpleBackupWorker(QThread):
    """Simple worker for basic operations"""
    finished = Signal(str, object)  # operation, result
    
    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args
        self.repo_path = "/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
    
    def run(self):
        try:
            if self.operation == "list_archives":
                result = self.list_archives()
                self.finished.emit("list_archives", result)
            elif self.operation == "list_files":
                result = self.list_files(self.args[0])
                self.finished.emit("list_files", result)
        except Exception as e:
            self.finished.emit(self.operation, f"Error: {e}")
    
    def list_archives(self):
        """Get backup archives"""
        try:
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg list "{self.repo_path}"'],
                capture_output=True, text=True, check=False, timeout=30
            )
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            archives = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        archives.append({
                            'name': parts[0],
                            'date': f"{parts[2]} {parts[3]}"
                        })
            
            return list(reversed(archives))  # Most recent first
            
        except Exception as e:
            return f"Error: {e}"
    
    def list_files(self, path):
        """List files in mounted directory"""
        try:
            if not os.path.exists(path):
                return f"Path not found: {path}"
            
            files = []
            for item in sorted(os.listdir(path)):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                
                try:
                    stat = os.stat(item_path)
                    date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    
                    if is_dir:
                        size = "Folder"
                    else:
                        size_bytes = stat.st_size
                        if size_bytes < 1024:
                            size = f"{size_bytes} B"
                        elif size_bytes < 1024*1024:
                            size = f"{size_bytes/1024:.1f} KB"
                        else:
                            size = f"{size_bytes/(1024*1024):.1f} MB"
                except:
                    date = "Unknown"
                    size = "Unknown"
                
                files.append({
                    'name': item,
                    'is_dir': is_dir,
                    'size': size,
                    'date': date,
                    'path': item_path
                })
            
            return files
            
        except Exception as e:
            return f"Error: {e}"

class SimplePikaExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mount_point = "/home/herb/simple-pika-mount"
        self.recovery_path = "/home/herb/Desktop/RecoveredFiles"
        self.temp_path = "/home/herb/Desktop/TempPreview"
        self.current_archive = None
        self.current_path = None
        
        # Create directories
        os.makedirs(self.recovery_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
        
        self.init_ui()
        self.load_archives()
    
    def init_ui(self):
        """Initialize simple UI"""
        self.setWindowTitle("🐭 Simple Pika Backup Explorer")
        self.setGeometry(100, 100, 1000, 700)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #B0E0E6, stop: 1 #87CEEB);
            }
            * {
                color: black;
            }
        """)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("📅 Select Backup:"))
        
        self.archive_combo = QComboBox()
        self.archive_combo.setMinimumWidth(400)
        self.archive_combo.currentTextChanged.connect(self.on_archive_selected)
        controls_layout.addWidget(self.archive_combo)
        
        self.mount_btn = QPushButton("🔗 Mount")
        self.mount_btn.clicked.connect(self.mount_selected_archive)
        self.mount_btn.setEnabled(False)
        controls_layout.addWidget(self.mount_btn)
        
        self.unmount_btn = QPushButton("🔒 Unmount")
        self.unmount_btn.clicked.connect(self.unmount_archive)
        self.unmount_btn.setEnabled(False)
        controls_layout.addWidget(self.unmount_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Status
        self.status_label = QLabel("Loading backup archives...")
        layout.addWidget(self.status_label)
        
        # Main content - splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left - Simple folder list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("📁 Quick Access:"))
        
        self.folder_list = QListWidget()
        self.folder_list.itemClicked.connect(self.on_folder_selected)
        left_layout.addWidget(self.folder_list)
        
        splitter.addWidget(left_widget)
        
        # Right - File table
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.path_label = QLabel("No archive mounted")
        right_layout.addWidget(self.path_label)
        
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["Name", "Date", "Size"])
        self.file_table.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        right_layout.addWidget(self.file_table)
        
        # File actions
        actions_layout = QHBoxLayout()
        
        self.temp_copy_btn = QPushButton("📋 Copy to Temp")
        self.temp_copy_btn.clicked.connect(self.temp_copy_selected)
        self.temp_copy_btn.setEnabled(False)
        actions_layout.addWidget(self.temp_copy_btn)
        
        self.copy_btn = QPushButton("💾 Copy Permanent")
        self.copy_btn.clicked.connect(self.copy_selected)
        self.copy_btn.setEnabled(False)
        actions_layout.addWidget(self.copy_btn)
        
        self.open_temp_btn = QPushButton("📂 Open Temp Folder")
        self.open_temp_btn.clicked.connect(lambda: subprocess.run(['nautilus', self.temp_path], check=False))
        actions_layout.addWidget(self.open_temp_btn)
        
        self.open_recovery_btn = QPushButton("📂 Open Recovery Folder")
        self.open_recovery_btn.clicked.connect(lambda: subprocess.run(['nautilus', self.recovery_path], check=False))
        actions_layout.addWidget(self.open_recovery_btn)
        
        right_layout.addLayout(actions_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([250, 750])
        
        layout.addWidget(splitter)
        
        # Selection handler
        self.file_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_archives(self):
        """Load backup archives"""
        self.status_label.setText("Loading backup archives...")
        
        self.worker = SimpleBackupWorker("list_archives")
        self.worker.finished.connect(self.on_archives_loaded)
        self.worker.start()
    
    def on_archives_loaded(self, operation, result):
        """Handle loaded archives"""
        if isinstance(result, str) and result.startswith("Error"):
            QMessageBox.critical(self, "Error", result)
            self.status_label.setText("Failed to load archives")
            return
        
        self.archive_combo.clear()
        self.archive_combo.addItem("Select backup date...", None)
        
        for archive in result:
            display_text = f"{archive['date']} - {archive['name']}"
            self.archive_combo.addItem(display_text, archive)
        
        self.status_label.setText(f"Loaded {len(result)} backup archives")
    
    def on_archive_selected(self):
        """Handle archive selection"""
        self.mount_btn.setEnabled(self.archive_combo.currentData() is not None)
    
    def mount_selected_archive(self):
        """Mount the selected archive"""
        archive_data = self.archive_combo.currentData()
        if not archive_data:
            return
        
        archive_name = archive_data['name']
        self.status_label.setText(f"Mounting {archive_name}...")
        
        try:
            # Unmount existing
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], check=False)
            
            os.makedirs(self.mount_point, exist_ok=True)
            
            # Mount archive
            full_archive = f"/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11::{archive_name}"
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg mount "{full_archive}" "{self.mount_point}"'],
                capture_output=True, text=True, check=False, timeout=60
            )
            
            if result.returncode == 0:
                self.current_archive = archive_name
                self.current_path = os.path.join(self.mount_point, "home/herb")
                self.unmount_btn.setEnabled(True)
                self.mount_btn.setEnabled(False)
                
                # Setup folder list
                self.setup_folder_list()
                
                # Load initial files
                self.load_files(self.current_path)
                
                self.status_label.setText(f"Mounted: {archive_name}")
            else:
                QMessageBox.critical(self, "Error", f"Mount failed: {result.stderr}")
                self.status_label.setText("Mount failed")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Mount error: {e}")
            self.status_label.setText("Mount failed")
    
    def setup_folder_list(self):
        """Setup quick access folder list"""
        self.folder_list.clear()
        
        base_path = os.path.join(self.mount_point, "home/herb")
        folders = [".", "Desktop", "Documents", "Projects", "Downloads", "Pictures", "Scripts"]
        
        for folder in folders:
            if folder == ".":
                folder_path = base_path
                display_name = "🏠 Home"
            else:
                folder_path = os.path.join(base_path, folder)
                display_name = f"📁 {folder}"
                
                if not os.path.exists(folder_path):
                    continue
            
            item = self.folder_list.addItem(display_name)
            item = self.folder_list.item(self.folder_list.count() - 1)
            item.setData(Qt.UserRole, folder_path)
    
    def on_folder_selected(self, item):
        """Handle folder selection"""
        folder_path = item.data(Qt.UserRole)
        if folder_path:
            self.current_path = folder_path
            self.load_files(folder_path)
    
    def load_files(self, path):
        """Load files from path"""
        relative_path = path.replace(os.path.join(self.mount_point, "home/herb"), "")
        if not relative_path:
            relative_path = "/home/herb"
        else:
            relative_path = f"/home/herb{relative_path}"
        
        self.path_label.setText(f"📁 {relative_path}")
        self.status_label.setText(f"Loading files from {relative_path}...")
        
        self.worker = SimpleBackupWorker("list_files", path)
        self.worker.finished.connect(self.on_files_loaded)
        self.worker.start()
    
    def on_files_loaded(self, operation, result):
        """Handle loaded files"""
        if isinstance(result, str):
            QMessageBox.warning(self, "Warning", result)
            return
        
        # Clear and populate table
        self.file_table.setRowCount(0)
        
        for file_info in result:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            
            # Name with icon
            icon = "📁" if file_info['is_dir'] else "📄"
            name_item = QTableWidgetItem(f"{icon} {file_info['name']}")
            name_item.setData(Qt.UserRole, file_info)
            self.file_table.setItem(row, 0, name_item)
            
            # Date
            self.file_table.setItem(row, 1, QTableWidgetItem(file_info['date']))
            
            # Size
            self.file_table.setItem(row, 2, QTableWidgetItem(file_info['size']))
        
        self.file_table.resizeColumnsToContents()
        self.status_label.setText(f"Loaded {len(result)} items")
    
    def on_file_double_clicked(self, item):
        """Handle file double-click"""
        if item.column() != 0:
            return
        
        file_info = item.data(Qt.UserRole)
        if file_info['is_dir']:
            # Navigate to directory
            self.current_path = file_info['path']
            self.load_files(file_info['path'])
    
    def on_selection_changed(self):
        """Handle selection change"""
        selected = self.file_table.selectedItems()
        has_selection = len(selected) > 0
        
        self.temp_copy_btn.setEnabled(has_selection)
        self.copy_btn.setEnabled(has_selection)

    def get_selected_items(self):
        """Get selected file info"""
        selected_items = []
        selected_rows = set()
        for item in self.file_table.selectedItems():
            selected_rows.add(item.row())

        for row in sorted(list(selected_rows)):
            item = self.file_table.item(row, 0)
            if item:
                selected_items.append(item.data(Qt.UserRole))
        return selected_items

    def temp_copy_selected(self):
        """Copy selected items to temp"""
        items = self.get_selected_items()
        if items:
            for item in items:
                self.copy_item(item, self.temp_path, "Temp")
            QMessageBox.information(self, "Success", f"Copied {len(items)} items to Temp folder.")

    def copy_selected(self):
        """Copy selected items permanently"""
        items = self.get_selected_items()
        if items:
            for item in items:
                self.copy_item(item, self.recovery_path, "Recovery")
            QMessageBox.information(self, "Success", f"Copied {len(items)} items to Recovery folder.")

    def copy_item(self, item_info, dest_dir, dest_type):
        """Copy file or directory to destination"""
        try:
            src_path = item_info['path']
            item_name = item_info['name']
            dest_path = os.path.join(dest_dir, item_name)
            
            # Handle duplicates
            counter = 1
            base_name, ext = os.path.splitext(item_name)
            while os.path.exists(dest_path):
                dest_path = os.path.join(dest_dir, f"{base_name}_{counter}{ext}")
                counter += 1
            
            if item_info['is_dir']:
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)

            self.status_label.setText(f"Copied {item_name} to {dest_type}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Copy failed for {item_name}: {e}")
    
    def unmount_archive(self):
        """Unmount current archive"""
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], check=False)
            
            self.current_archive = None
            self.current_path = None
            self.unmount_btn.setEnabled(False)
            self.mount_btn.setEnabled(True)
            
            # Clear interface
            self.folder_list.clear()
            self.file_table.setRowCount(0)
            self.path_label.setText("No archive mounted")
            
            self.status_label.setText("Archive unmounted")
        
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Unmount error: {e}")
    
    def closeEvent(self, event):
        """Handle close event"""
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], check=False)
        except:
            pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Check if display is available
    if not app.primaryScreen():
        print("No display available. Make sure you're running in a graphical environment.")
        return 1
    
    window = SimplePikaExplorer()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())