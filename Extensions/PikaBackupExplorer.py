# File: PikaBackupExplorer.py
# Path: /home/herb/PikaBackupExplorer.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-29
# Last Modified: 2025-07-29 05:58AM
"""
PySide6 Desktop Backup Explorer for Pika Backups
Full-featured GUI application for browsing and recovering backup files
"""

import sys
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QProgressBar,
    QMessageBox, QFileDialog, QGroupBox, QStatusBar, QMenuBar, QMenu,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QIcon, QFont, QAction

class BorgWorker(QThread):
    """Background worker for Borg operations"""
    finished = Signal(str, object, str)  # operation, result, error
    progress = Signal(str)  # status message
    
    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args
        self.repo_path = "/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
        self.mount_point = "/home/herb/desktop-backup-mount"
    
    def run(self):
        try:
            if self.operation == "list_archives":
                self.list_archives()
            elif self.operation == "mount_archive":
                self.mount_archive(self.args[0])
            elif self.operation == "unmount":
                self.unmount_archive()
            elif self.operation == "list_files":
                self.list_files(self.args[0])
        except Exception as e:
            self.finished.emit(self.operation, None, str(e))
    
    def list_archives(self):
        """Get list of all backup archives"""
        self.progress.emit("Loading backup archives...")
        
        try:
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg list "{self.repo_path}"'],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode != 0:
                self.finished.emit("list_archives", None, result.stderr)
                return
            
            archives = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        archive_name = parts[0]
                        date_str = f"{parts[2]} {parts[3]}"
                        archives.append({
                            'name': archive_name,
                            'date': date_str,
                            'readable_date': self.format_date(date_str)
                        })
            
            # Most recent first
            archives.reverse()
            self.finished.emit("list_archives", archives, "")
            
        except Exception as e:
            self.finished.emit("list_archives", None, str(e))
    
    def mount_archive(self, archive_name):
        """Mount a specific archive"""
        self.progress.emit(f"Mounting archive {archive_name}...")
        
        try:
            # Unmount any existing archive
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], check=False)
            
            # Create mount point
            os.makedirs(self.mount_point, exist_ok=True)
            
            # Mount archive
            full_archive = f"{self.repo_path}::{archive_name}"
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg mount "{full_archive}" "{self.mount_point}"'],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode == 0:
                self.finished.emit("mount_archive", archive_name, "")
            else:
                self.finished.emit("mount_archive", None, result.stderr)
                
        except Exception as e:
            self.finished.emit("mount_archive", None, str(e))
    
    def unmount_archive(self):
        """Unmount current archive"""
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], check=False)
            self.finished.emit("unmount", True, "")
        except Exception as e:
            self.finished.emit("unmount", None, str(e))
    
    def list_files(self, path):
        """List files in a directory"""
        self.progress.emit(f"Loading files from {path}...")
        
        try:
            if not os.path.exists(path):
                self.finished.emit("list_files", [], "Path not found")
                return
            
            items = []
            
            # Add parent directory if not at root
            if path != os.path.join(self.mount_point, "home/herb"):
                items.append({
                    'name': '..',
                    'is_dir': True,
                    'size': '',
                    'date': '',
                    'path': os.path.dirname(path)
                })
            
            # List directory contents
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
                        elif size_bytes < 1024*1024*1024:
                            size = f"{size_bytes/(1024*1024):.1f} MB"
                        else:
                            size = f"{size_bytes/(1024*1024*1024):.1f} GB"
                except:
                    date = "Unknown"
                    size = "Unknown"
                
                items.append({
                    'name': item,
                    'is_dir': is_dir,
                    'size': size,
                    'date': date,
                    'path': item_path
                })
            
            self.finished.emit("list_files", items, "")
            
        except Exception as e:
            self.finished.emit("list_files", None, str(e))
    
    def format_date(self, date_str):
        """Format date string for display"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return date_str

class PikaBackupExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_archive = None
        self.current_path = None
        self.mount_point = "/home/herb/desktop-backup-mount"
        self.recovery_path = str(Path.home() / "Desktop" / "RecoveredFiles")
        self.temp_path = str(Path.home() / "Desktop" / "TempPreview")
        
        # Create recovery directories
        os.makedirs(self.recovery_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
        
        self.init_ui()
        self.load_archives()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🐭 Pika Backup Explorer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Top controls
        controls_group = QGroupBox("Backup Selection")
        controls_layout = QHBoxLayout(controls_group)
        
        # Archive selector
        controls_layout.addWidget(QLabel("📅 Select Backup:"))
        self.archive_combo = QComboBox()
        self.archive_combo.setMinimumWidth(400)
        self.archive_combo.currentTextChanged.connect(self.on_archive_selected)
        controls_layout.addWidget(self.archive_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_archives)
        controls_layout.addWidget(self.refresh_btn)
        
        # Unmount button
        self.unmount_btn = QPushButton("🔒 Unmount")
        self.unmount_btn.clicked.connect(self.unmount_archive)
        self.unmount_btn.setEnabled(False)
        controls_layout.addWidget(self.unmount_btn)
        
        controls_layout.addStretch()
        main_layout.addWidget(controls_group)
        
        # Splitter for navigation and files
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Directory tree
        nav_group = QGroupBox("📁 Navigation")
        nav_layout = QVBoxLayout(nav_group)
        
        # Current path display
        self.path_label = QLabel("No archive mounted")
        self.path_label.setStyleSheet("background: #f0f0f0; padding: 5px; border-radius: 3px;")
        nav_layout.addWidget(self.path_label)
        
        # Directory tree
        self.dir_tree = QTreeWidget()
        self.dir_tree.setHeaderLabels(["📂 Folders"])
        self.dir_tree.itemClicked.connect(self.on_folder_clicked)
        nav_layout.addWidget(self.dir_tree)
        
        splitter.addWidget(nav_group)
        
        # Right panel - File list
        files_group = QGroupBox("📄 Files")
        files_layout = QVBoxLayout(files_group)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter files...")
        self.search_edit.textChanged.connect(self.filter_files)
        search_layout.addWidget(self.search_edit)
        files_layout.addLayout(search_layout)
        
        # File table
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(["Name", "Date Modified", "Size", "Actions"])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setAlternatingRowColors(True)
        self.file_table.itemDoubleClicked.connect(self.on_file_double_clicked)
        files_layout.addWidget(self.file_table)
        
        # File actions
        actions_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ Preview")
        self.preview_btn.clicked.connect(self.preview_selected_file)
        self.preview_btn.setEnabled(False)
        actions_layout.addWidget(self.preview_btn)
        
        self.temp_copy_btn = QPushButton("📋 Temp Copy")
        self.temp_copy_btn.clicked.connect(self.temp_copy_selected_file)
        self.temp_copy_btn.setEnabled(False)
        actions_layout.addWidget(self.temp_copy_btn)
        
        self.copy_btn = QPushButton("💾 Copy")
        self.copy_btn.clicked.connect(self.copy_selected_file)
        self.copy_btn.setEnabled(False)
        actions_layout.addWidget(self.copy_btn)
        
        actions_layout.addStretch()
        
        # Recovery folders buttons
        self.open_temp_btn = QPushButton("📂 Open Temp Folder")
        self.open_temp_btn.clicked.connect(self.open_temp_folder)
        actions_layout.addWidget(self.open_temp_btn)
        
        self.open_recovery_btn = QPushButton("📂 Open Recovery Folder")
        self.open_recovery_btn.clicked.connect(self.open_recovery_folder)
        actions_layout.addWidget(self.open_recovery_btn)
        
        files_layout.addLayout(actions_layout)
        
        splitter.addWidget(files_group)
        
        # Set splitter sizes
        splitter.setSizes([300, 900])
        main_layout.addWidget(splitter)
        
        # Bottom panel - Preview/Log
        bottom_splitter = QSplitter(Qt.Vertical)
        
        # File preview
        preview_group = QGroupBox("📖 File Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(200)
        self.preview_text.setPlaceholderText("File preview will appear here...")
        preview_layout.addWidget(self.preview_text)
        
        bottom_splitter.addWidget(preview_group)
        main_layout.addWidget(bottom_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Enable table selection
        self.file_table.itemSelectionChanged.connect(self.on_file_selection_changed)
    
    def load_archives(self):
        """Load list of backup archives"""
        self.status_bar.showMessage("Loading backup archives...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.worker = BorgWorker("list_archives")
        self.worker.finished.connect(self.on_archives_loaded)
        self.worker.progress.connect(self.status_bar.showMessage)
        self.worker.start()
    
    def on_archives_loaded(self, operation, archives, error):
        """Handle archives loading completion"""
        self.progress_bar.setVisible(False)
        
        if error:
            QMessageBox.critical(self, "Error", f"Failed to load archives: {error}")
            self.status_bar.showMessage("Failed to load archives")
            return
        
        # Populate combo box
        self.archive_combo.clear()
        self.archive_combo.addItem("Select a backup date...", None)
        
        for archive in archives:
            display_text = f"{archive['readable_date']} - {archive['name']}"
            self.archive_combo.addItem(display_text, archive)
        
        self.status_bar.showMessage(f"Loaded {len(archives)} backup archives")
    
    def on_archive_selected(self):
        """Handle archive selection"""
        current_data = self.archive_combo.currentData()
        if current_data is None:
            return
        
        archive_name = current_data['name']
        self.status_bar.showMessage(f"Mounting archive {archive_name}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.worker = BorgWorker("mount_archive", archive_name)
        self.worker.finished.connect(self.on_archive_mounted)
        self.worker.progress.connect(self.status_bar.showMessage)
        self.worker.start()
    
    def on_archive_mounted(self, operation, result, error):
        """Handle archive mounting completion"""
        self.progress_bar.setVisible(False)
        
        if error:
            QMessageBox.critical(self, "Error", f"Failed to mount archive: {error}")
            self.status_bar.showMessage("Failed to mount archive")
            return
        
        self.current_archive = result
        self.current_path = os.path.join(self.mount_point, "home/herb")
        self.unmount_btn.setEnabled(True)
        
        # Build directory tree
        self.build_directory_tree()
        
        # Load initial files
        self.load_files(self.current_path)
        
        self.path_label.setText(f"📁 /home/herb")
        self.status_bar.showMessage(f"Archive {result} mounted successfully")
    
    def build_directory_tree(self):
        """Build directory tree structure"""
        self.dir_tree.clear()
        
        if not self.current_archive:
            return
        
        # Create root item
        root_path = os.path.join(self.mount_point, "home/herb")
        root_item = QTreeWidgetItem(self.dir_tree, ["home/herb"])
        root_item.setData(0, Qt.UserRole, root_path)
        
        # Add common directories
        common_dirs = ["Desktop", "Documents", "Projects", "Downloads", "Pictures", "Videos", "Scripts"]
        
        for dir_name in common_dirs:
            dir_path = os.path.join(root_path, dir_name)
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                dir_item = QTreeWidgetItem(root_item, [dir_name])
                dir_item.setData(0, Qt.UserRole, dir_path)
                
                # Check if directory has subdirectories
                try:
                    for sub_item in os.listdir(dir_path):
                        sub_path = os.path.join(dir_path, sub_item)
                        if os.path.isdir(sub_path) and not sub_item.startswith('.'):
                            sub_dir_item = QTreeWidgetItem(dir_item, [sub_item])
                            sub_dir_item.setData(0, Qt.UserRole, sub_path)
                except:
                    pass
        
        self.dir_tree.expandItem(root_item)
    
    def on_folder_clicked(self, item, column):
        """Handle folder click in tree"""
        folder_path = item.data(0, Qt.UserRole)
        if folder_path:
            self.current_path = folder_path
            
            # Update path label
            relative_path = folder_path.replace(os.path.join(self.mount_point, "home/herb"), "")
            if not relative_path:
                relative_path = "/home/herb"
            else:
                relative_path = f"/home/herb{relative_path}"
            
            self.path_label.setText(f"📁 {relative_path}")
            
            # Load files
            self.load_files(folder_path)
    
    def load_files(self, path):
        """Load files from specified path"""
        self.status_bar.showMessage(f"Loading files from {path}...")
        
        self.worker = BorgWorker("list_files", path)
        self.worker.finished.connect(self.on_files_loaded)
        self.worker.progress.connect(self.status_bar.showMessage)
        self.worker.start()
    
    def on_files_loaded(self, operation, files, error):
        """Handle files loading completion"""
        if error:
            QMessageBox.warning(self, "Warning", f"Error loading files: {error}")
            return
        
        # Clear and populate table
        self.file_table.setRowCount(0)
        
        for file_info in files:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(f"{'📁' if file_info['is_dir'] else '📄'} {file_info['name']}")
            name_item.setData(Qt.UserRole, file_info)
            self.file_table.setItem(row, 0, name_item)
            
            # Date
            self.file_table.setItem(row, 1, QTableWidgetItem(file_info['date']))
            
            # Size
            self.file_table.setItem(row, 2, QTableWidgetItem(file_info['size']))
            
            # Actions (will be handled by buttons)
            actions_text = "Navigate" if file_info['is_dir'] else "Copy/Preview"
            self.file_table.setItem(row, 3, QTableWidgetItem(actions_text))
        
        # Resize columns
        self.file_table.resizeColumnsToContents()
        
        self.status_bar.showMessage(f"Loaded {len(files)} items")
    
    def on_file_double_clicked(self, item):
        """Handle file double-click"""
        if item.column() != 0:
            return
        
        file_info = item.data(Qt.UserRole)
        if file_info['is_dir']:
            # Navigate to directory
            if file_info['name'] == '..':
                # Go to parent directory
                self.current_path = file_info['path']
            else:
                # Go to subdirectory
                self.current_path = file_info['path']
            
            # Update path display
            relative_path = self.current_path.replace(os.path.join(self.mount_point, "home/herb"), "")
            if not relative_path:
                relative_path = "/home/herb"
            else:
                relative_path = f"/home/herb{relative_path}"
            
            self.path_label.setText(f"📁 {relative_path}")
            
            # Load files from new path
            self.load_files(self.current_path)
        else:
            # Preview file
            self.preview_file(file_info)
    
    def on_file_selection_changed(self):
        """Handle file selection change"""
        selected_items = self.file_table.selectedItems()
        has_selection = len(selected_items) > 0
        
        if has_selection:
            # Get selected file info
            row = selected_items[0].row()
            file_info = self.file_table.item(row, 0).data(Qt.UserRole)
            is_file = not file_info['is_dir'] and file_info['name'] != '..'
            
            self.preview_btn.setEnabled(is_file and self.can_preview_file(file_info['name']))
            self.temp_copy_btn.setEnabled(is_file)
            self.copy_btn.setEnabled(is_file)
        else:
            self.preview_btn.setEnabled(False)
            self.temp_copy_btn.setEnabled(False)
            self.copy_btn.setEnabled(False)
    
    def can_preview_file(self, filename):
        """Check if file can be previewed"""
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', 
                          '.yaml', '.yml', '.sh', '.bat', '.ps1', '.ini', '.cfg', '.conf', 
                          '.log', '.sql', '.csv'}
        _, ext = os.path.splitext(filename.lower())
        return ext in text_extensions
    
    def get_selected_file_info(self):
        """Get currently selected file info"""
        selected_items = self.file_table.selectedItems()
        if not selected_items:
            return None
        
        row = selected_items[0].row()
        return self.file_table.item(row, 0).data(Qt.UserRole)
    
    def preview_selected_file(self):
        """Preview the selected file"""
        file_info = self.get_selected_file_info()
        if file_info:
            self.preview_file(file_info)
    
    def preview_file(self, file_info):
        """Preview a file in the preview pane"""
        try:
            file_path = file_info['path']
            file_size = os.path.getsize(file_path)
            
            if file_size > 1024 * 1024:  # 1MB limit
                content = f"File too large to preview ({file_size/1024/1024:.1f} MB)"
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)  # First 5000 characters
                    if len(content) == 5000:
                        content += "\n\n... (showing first 5,000 characters)"
            
            self.preview_text.setText(content)
            self.status_bar.showMessage(f"Previewing: {file_info['name']}")
            
        except Exception as e:
            self.preview_text.setText(f"Error previewing file: {e}")
    
    def temp_copy_selected_file(self):
        """Copy selected file to temp folder"""
        file_info = self.get_selected_file_info()
        if file_info:
            self.copy_file(file_info, self.temp_path, "Temp")
    
    def copy_selected_file(self):
        """Copy selected file to recovery folder"""
        file_info = self.get_selected_file_info()
        if file_info:
            self.copy_file(file_info, self.recovery_path, "Recovery")
    
    def copy_file(self, file_info, dest_folder, folder_type):
        """Copy file to specified folder"""
        try:
            src_path = file_info['path']
            filename = file_info['name']
            dest_path = os.path.join(dest_folder, filename)
            
            # Handle duplicate names
            counter = 1
            original_dest = dest_path
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(dest_folder, f"{name}_{counter}{ext}")
                counter += 1
            
            shutil.copy2(src_path, dest_path)
            
            QMessageBox.information(self, "Success", 
                                  f"File copied to {folder_type} folder:\n{dest_path}")
            self.status_bar.showMessage(f"Copied {filename} to {folder_type} folder")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy file: {e}")
    
    def open_temp_folder(self):
        """Open temp folder in file manager"""
        subprocess.run(['nautilus', self.temp_path], check=False)
    
    def open_recovery_folder(self):
        """Open recovery folder in file manager"""
        subprocess.run(['nautilus', self.recovery_path], check=False)
    
    def filter_files(self):
        """Filter files based on search text"""
        search_text = self.search_edit.text().lower()
        
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, 0)
            if item:
                filename = item.text().lower()
                self.file_table.setRowHidden(row, search_text not in filename)
    
    def unmount_archive(self):
        """Unmount current archive"""
        if not self.current_archive:
            return
        
        self.status_bar.showMessage("Unmounting archive...")
        
        self.worker = BorgWorker("unmount")
        self.worker.finished.connect(self.on_archive_unmounted)
        self.worker.start()
    
    def on_archive_unmounted(self, operation, result, error):
        """Handle archive unmounting"""
        self.current_archive = None
        self.current_path = None
        self.unmount_btn.setEnabled(False)
        
        # Clear interface
        self.dir_tree.clear()
        self.file_table.setRowCount(0)
        self.preview_text.clear()
        self.path_label.setText("No archive mounted")
        self.archive_combo.setCurrentIndex(0)
        
        self.status_bar.showMessage("Archive unmounted")
    
    def closeEvent(self, event):
        """Handle application close"""
        # Unmount any mounted archive
        if self.current_archive:
            try:
                if os.path.ismount(self.mount_point):
                    subprocess.run(['borg', 'umount', self.mount_point], check=False)
            except:
                pass
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Pika Backup Explorer")
    app.setApplicationVersion("1.0")
    
    # Set application icon (if available)
    try:
        app.setWindowIcon(QIcon(":/icons/backup.png"))
    except:
        pass
    
    window = PikaBackupExplorer()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()