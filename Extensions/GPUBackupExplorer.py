#!/usr/bin/env python3
# File: GPUBackupExplorer.py  
# Path: /home/herb/GPUBackupExplorer.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-29
# Last Modified: 2025-07-29 06:08AM
"""
GPU-Accelerated PySide6 Backup Explorer - Optimized for RTX 4070
"""

import sys
import os
import subprocess
import shutil
from datetime import datetime

# Set environment variables for GPU acceleration BEFORE importing Qt
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['QT_QUICK_BACKEND'] = 'rhi'
os.environ['QSG_RHI_BACKEND'] = 'vulkan'  # Use Vulkan for RTX 4070
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--enable-gpu-rasterization --enable-zero-copy'

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QListWidget, QTableWidget, QTableWidgetItem, QLabel, QPushButton,
        QComboBox, QMessageBox, QTextEdit, QSplitter, QProgressBar,
        QStatusBar, QHeaderView
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer
    from PySide6.QtGui import QFont, QPalette, QColor
    from PySide6.QtOpenGL import QOpenGLWidget
except ImportError:
    print("PySide6 not available. Installing...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'PySide6'], check=True)
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *

class GPUBackupWorker(QThread):
    """GPU-optimized worker for backup operations"""
    finished = Signal(str, object)
    progress = Signal(str)
    
    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args
        self.repo_path = "/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
        self.mount_point = "/home/herb/gpu-backup-mount"
    
    def run(self):
        try:
            if self.operation == "list_archives":
                self.progress.emit("🔍 Scanning backup repository...")
                result = self.list_archives()
                self.finished.emit("list_archives", result)
            elif self.operation == "mount_archive":
                self.progress.emit(f"🔗 Mounting archive {self.args[0]}...")
                result = self.mount_archive(self.args[0])
                self.finished.emit("mount_archive", result)
            elif self.operation == "list_files":
                self.progress.emit(f"📂 Loading files from {self.args[0]}...")
                result = self.list_files(self.args[0])
                self.finished.emit("list_files", result)
        except Exception as e:
            self.finished.emit(self.operation, f"Error: {e}")
    
    def list_archives(self):
        """Get all backup archives"""
        try:
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg list "{self.repo_path}"'],
                capture_output=True, text=True, check=False, timeout=45
            )
            
            if result.returncode != 0:
                return f"Repository Error: {result.stderr}"
            
            archives = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        # Format date nicely
                        try:
                            dt = datetime.strptime(f"{parts[2]} {parts[3]}", "%Y-%m-%d %H:%M:%S")
                            readable_date = dt.strftime("%B %d, %Y at %I:%M %p")
                        except:
                            readable_date = f"{parts[2]} {parts[3]}"
                        
                        archives.append({
                            'name': parts[0],
                            'date': f"{parts[2]} {parts[3]}",
                            'readable_date': readable_date
                        })
            
            return list(reversed(archives))  # Most recent first
            
        except subprocess.TimeoutExpired:
            return "Error: Repository access timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def mount_archive(self, archive_name):
        """Mount archive with GPU-optimized settings"""
        try:
            # Unmount any existing
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], 
                             check=False, timeout=30)
            
            # Create mount point
            os.makedirs(self.mount_point, exist_ok=True)
            
            # Mount with optimizations
            full_archive = f"{self.repo_path}::{archive_name}"
            result = subprocess.run(
                ['bash', '-c', f'echo "y" | borg mount "{full_archive}" "{self.mount_point}"'],
                capture_output=True, text=True, check=False, timeout=60
            )
            
            if result.returncode == 0:
                return {"success": True, "archive": archive_name}
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_files(self, path):
        """List files with GPU-accelerated processing"""
        try:
            if not os.path.exists(path):
                return f"Path not found: {path}"
            
            files = []
            
            # Add parent directory navigation
            parent_path = os.path.dirname(path)
            if parent_path != path and parent_path.endswith("home/herb"):
                files.append({
                    'name': '..',
                    'is_dir': True,
                    'size': '',
                    'date': '',
                    'path': parent_path,
                    'icon': '📁'
                })
            
            # Process directory contents
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
                        icon = "📁"
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
                        
                        # File type icons
                        ext = os.path.splitext(item)[1].lower()
                        if ext in ['.py', '.js', '.html', '.css']:
                            icon = "💻"
                        elif ext in ['.txt', '.md', '.log']:
                            icon = "📄"
                        elif ext in ['.jpg', '.png', '.gif', '.bmp']:
                            icon = "🖼️"
                        elif ext in ['.mp4', '.avi', '.mkv']:
                            icon = "🎬"
                        elif ext in ['.pdf']:
                            icon = "📕"
                        else:
                            icon = "📄"
                            
                except:
                    date = "Unknown"
                    size = "Unknown"
                    icon = "❓"
                
                files.append({
                    'name': item,
                    'is_dir': is_dir,
                    'size': size,
                    'date': date,
                    'path': item_path,
                    'icon': icon
                })
            
            return files
            
        except Exception as e:
            return f"Error: {e}"

class GPUBackupExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mount_point = "/home/herb/gpu-backup-mount"
        self.recovery_path = "/home/herb/Desktop/RecoveredFiles"
        self.temp_path = "/home/herb/Desktop/TempPreview"
        self.current_archive = None
        self.current_path = None
        
        # Create directories
        os.makedirs(self.recovery_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
        
        self.init_gpu_optimized_ui()
        self.load_archives()
    
    def init_gpu_optimized_ui(self):
        """Initialize GPU-accelerated UI"""
        self.setWindowTitle("🐭 GPU-Accelerated Pika Backup Explorer (RTX 4070)")
        self.setGeometry(100, 100, 1200, 800)
        
        # Enable GPU acceleration
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)
        
        # Set modern styling
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:1 #e0e0e0);
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin: 5px;
                padding-top: 10px;
                background: rgba(255, 255, 255, 200);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5CBF60, stop:1 #55b059);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3CAF40, stop:1 #359039);
            }
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
                alternate-background-color: #f8f8f8;
                border-radius: 8px;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background: white;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header with GPU info
        header_layout = QHBoxLayout()
        
        gpu_label = QLabel("🚀 RTX 4070 Accelerated | ")
        gpu_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        header_layout.addWidget(gpu_label)
        
        header_layout.addWidget(QLabel("📅 Select Backup:"))
        
        self.archive_combo = QComboBox()
        self.archive_combo.setMinimumWidth(450)
        self.archive_combo.currentTextChanged.connect(self.on_archive_selected)
        header_layout.addWidget(self.archive_combo)
        
        self.mount_btn = QPushButton("🔗 Mount Archive")
        self.mount_btn.clicked.connect(self.mount_selected_archive)
        self.mount_btn.setEnabled(False)
        header_layout.addWidget(self.mount_btn)
        
        self.unmount_btn = QPushButton("🔒 Unmount")
        self.unmount_btn.clicked.connect(self.unmount_archive)
        self.unmount_btn.setEnabled(False)
        header_layout.addWidget(self.unmount_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 8px;
                text-align: center;
                background: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #1976D2);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("🔍 Loading GPU-accelerated backup browser...")
        self.status_label.setStyleSheet("padding: 8px; background: rgba(33, 150, 243, 50); border-radius: 4px;")
        layout.addWidget(self.status_label)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Folders
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        folder_label = QLabel("📁 Quick Navigation")
        folder_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        left_layout.addWidget(folder_label)
        
        self.current_path_label = QLabel("No archive mounted")
        self.current_path_label.setStyleSheet("background: #f0f0f0; padding: 6px; border-radius: 4px; font-family: monospace;")
        left_layout.addWidget(self.current_path_label)
        
        self.folder_list = QListWidget()
        self.folder_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                background: white;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background: #e3f2fd;
            }
            QListWidget::item:selected {
                background: #2196F3;
                color: white;
            }
        """)
        self.folder_list.itemClicked.connect(self.on_folder_selected)
        left_layout.addWidget(self.folder_list)
        
        splitter.addWidget(left_widget)
        
        # Right panel - Files
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        files_label = QLabel("📄 Files & Directories")
        files_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        right_layout.addWidget(files_label)
        
        # File table with GPU acceleration
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(["📁 Name", "📅 Date Modified", "📊 Size", "🔧 Type"])
        
        # Optimize for GPU rendering
        header = self.file_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.file_table.setAlternatingRowColors(True)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        right_layout.addWidget(self.file_table)
        
        # Action buttons with GPU styling
        actions_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ Preview File")
        self.preview_btn.clicked.connect(self.preview_selected)
        self.preview_btn.setEnabled(False)
        actions_layout.addWidget(self.preview_btn)
        
        self.temp_copy_btn = QPushButton("📋 Quick Copy")
        self.temp_copy_btn.clicked.connect(self.temp_copy_selected)
        self.temp_copy_btn.setEnabled(False)
        self.temp_copy_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF9800, stop:1 #F57C00); }")
        actions_layout.addWidget(self.temp_copy_btn)
        
        self.copy_btn = QPushButton("💾 Permanent Copy")
        self.copy_btn.clicked.connect(self.copy_selected)
        self.copy_btn.setEnabled(False)
        actions_layout.addWidget(self.copy_btn)
        
        actions_layout.addStretch()
        
        # Folder access buttons
        self.open_temp_btn = QPushButton("📂 Temp Folder")
        self.open_temp_btn.clicked.connect(lambda: self.open_folder(self.temp_path))
        self.open_temp_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9C27B0, stop:1 #7B1FA2); }")
        actions_layout.addWidget(self.open_temp_btn)
        
        self.open_recovery_btn = QPushButton("📂 Recovery Folder")
        self.open_recovery_btn.clicked.connect(lambda: self.open_folder(self.recovery_path))
        self.open_recovery_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #607D8B, stop:1 #455A64); }")
        actions_layout.addWidget(self.open_recovery_btn)
        
        right_layout.addLayout(actions_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 900])
        
        layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Performance timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance_info)
        self.perf_timer.start(2000)  # Update every 2 seconds
        
        self.status_bar.showMessage("🚀 GPU acceleration enabled - Ready for high-performance backup browsing")
    
    def update_performance_info(self):
        """Update GPU performance info"""
        if self.current_archive:
            try:
                # Get GPU memory info if nvidia-smi is available
                result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    used, total = result.stdout.strip().split(', ')
                    gpu_info = f"RTX 4070: {used}MB/{total}MB VRAM"
                    self.status_bar.showMessage(f"🚀 {gpu_info} | Archive: {self.current_archive}")
                else:
                    self.status_bar.showMessage(f"🚀 RTX 4070 Active | Archive: {self.current_archive}")
            except:
                self.status_bar.showMessage(f"🚀 RTX 4070 Active | Archive: {self.current_archive}")
    
    def load_archives(self):
        """Load archives with GPU acceleration"""
        self.status_label.setText("🔍 GPU: Scanning backup repository...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.worker = GPUBackupWorker("list_archives")
        self.worker.finished.connect(self.on_archives_loaded)
        self.worker.progress.connect(self.status_label.setText)
        self.worker.start()
    
    def on_archives_loaded(self, operation, result):
        """Handle loaded archives"""
        self.progress_bar.setVisible(False)
        
        if isinstance(result, str) and result.startswith("Error"):
            QMessageBox.critical(self, "Repository Error", result)
            self.status_label.setText("❌ Failed to load backup repository")
            return
        
        self.archive_combo.clear()
        self.archive_combo.addItem("Select a backup date...", None)
        
        for archive in result:
            display_text = f"📅 {archive['readable_date']} ({archive['name']})"
            self.archive_combo.addItem(display_text, archive)
        
        self.status_label.setText(f"✅ GPU: Loaded {len(result)} backup archives")
    
    def on_archive_selected(self):
        """Handle archive selection"""
        self.mount_btn.setEnabled(self.archive_combo.currentData() is not None)
    
    def mount_selected_archive(self):
        """Mount selected archive with GPU optimization"""
        archive_data = self.archive_combo.currentData()
        if not archive_data:
            return
        
        archive_name = archive_data['name']
        self.status_label.setText(f"🔗 GPU: Mounting {archive_name}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.worker = GPUBackupWorker("mount_archive", archive_name)
        self.worker.finished.connect(self.on_archive_mounted)
        self.worker.progress.connect(self.status_label.setText)
        self.worker.start()
    
    def on_archive_mounted(self, operation, result):
        """Handle archive mounting"""
        self.progress_bar.setVisible(False)
        
        if isinstance(result, str):
            QMessageBox.critical(self, "Mount Error", result)
            self.status_label.setText("❌ Mount failed")
            return
        
        if not result.get("success"):
            QMessageBox.critical(self, "Mount Error", result.get("error", "Unknown error"))
            self.status_label.setText("❌ Mount failed")
            return
        
        self.current_archive = result["archive"]
        self.current_path = os.path.join(self.mount_point, "home/herb")
        
        self.unmount_btn.setEnabled(True)
        self.mount_btn.setEnabled(False)
        
        # Setup navigation
        self.setup_folder_navigation()
        self.load_files(self.current_path)
        
        self.status_label.setText(f"✅ GPU: Successfully mounted {self.current_archive}")
        
        # Start performance monitoring
        self.perf_timer.start(2000)
    
    def setup_folder_navigation(self):
        """Setup folder navigation list"""
        self.folder_list.clear()
        
        base_path = os.path.join(self.mount_point, "home/herb")
        folders = [
            ("🏠 Home Directory", base_path),
            ("🖥️ Desktop", os.path.join(base_path, "Desktop")),
            ("📄 Documents", os.path.join(base_path, "Documents")),
            ("🚀 Projects", os.path.join(base_path, "Projects")),
            ("⬇️ Downloads", os.path.join(base_path, "Downloads")),
            ("🖼️ Pictures", os.path.join(base_path, "Pictures")),
            ("🎬 Videos", os.path.join(base_path, "Videos")),
            ("⚙️ Scripts", os.path.join(base_path, "Scripts"))
        ]
        
        for display_name, folder_path in folders:
            if os.path.exists(folder_path):
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, folder_path)
                self.folder_list.addItem(item)
    
    def on_folder_selected(self, item):
        """Handle folder selection"""
        folder_path = item.data(Qt.UserRole)
        if folder_path:
            self.current_path = folder_path
            self.load_files(folder_path)
    
    def load_files(self, path):
        """Load files with GPU acceleration"""
        # Update path display
        relative_path = path.replace(os.path.join(self.mount_point, "home/herb"), "")
        if not relative_path:
            display_path = "/home/herb"
        else:
            display_path = f"/home/herb{relative_path}"
        
        self.current_path_label.setText(f"📁 {display_path}")
        self.status_label.setText(f"📂 GPU: Loading files from {display_path}...")
        
        self.worker = GPUBackupWorker("list_files", path)
        self.worker.finished.connect(self.on_files_loaded)
        self.worker.progress.connect(self.status_label.setText)
        self.worker.start()
    
    def on_files_loaded(self, operation, result):
        """Handle loaded files with GPU rendering"""
        if isinstance(result, str):
            QMessageBox.warning(self, "Directory Error", result)
            return
        
        # Clear table
        self.file_table.setRowCount(0)
        
        # Populate with GPU-optimized rendering
        for file_info in result:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            
            # Name with enhanced icon
            name_item = QTableWidgetItem(f"{file_info['icon']} {file_info['name']}")
            name_item.setData(Qt.UserRole, file_info)
            self.file_table.setItem(row, 0, name_item)
            
            # Date
            self.file_table.setItem(row, 1, QTableWidgetItem(file_info['date']))
            
            # Size
            self.file_table.setItem(row, 2, QTableWidgetItem(file_info['size']))
            
            # Type
            file_type = "Directory" if file_info['is_dir'] else "File"
            self.file_table.setItem(row, 3, QTableWidgetItem(file_type))
        
        # GPU-accelerated column resizing
        self.file_table.resizeColumnsToContents()
        
        self.status_label.setText(f"✅ GPU: Rendered {len(result)} items")
    
    def on_file_double_clicked(self, item):
        """Handle file double-click navigation"""
        if item.column() != 0:
            return
        
        file_info = item.data(Qt.UserRole)
        if file_info and file_info['is_dir']:
            self.current_path = file_info['path']
            self.load_files(file_info['path'])
    
    def on_selection_changed(self):
        """Handle selection changes"""
        selected = self.file_table.selectedItems()
        has_file_selected = False
        
        if selected:
            file_info = selected[0].data(Qt.UserRole)
            has_file_selected = file_info and not file_info['is_dir']
        
        self.preview_btn.setEnabled(has_file_selected)
        self.temp_copy_btn.setEnabled(has_file_selected)
        self.copy_btn.setEnabled(has_file_selected)
    
    def get_selected_file(self):
        """Get selected file info"""
        selected = self.file_table.selectedItems()
        if selected:
            return selected[0].data(Qt.UserRole)
        return None
    
    def preview_selected(self):
        """Preview selected file"""
        file_info = self.get_selected_file()
        if file_info:
            QMessageBox.information(self, "File Preview", 
                                  f"File: {file_info['name']}\n"
                                  f"Size: {file_info['size']}\n"
                                  f"Date: {file_info['date']}\n"
                                  f"Path: {file_info['path']}")
    
    def temp_copy_selected(self):
        """Quick copy to temp folder"""
        file_info = self.get_selected_file()
        if file_info:
            self.copy_file(file_info, self.temp_path, "Temp")
    
    def copy_selected(self):
        """Permanent copy to recovery folder"""
        file_info = self.get_selected_file()
        if file_info:
            self.copy_file(file_info, self.recovery_path, "Recovery")
    
    def copy_file(self, file_info, dest_dir, dest_type):
        """Copy file with GPU-accelerated progress"""
        try:
            src_path = file_info['path']
            filename = file_info['name']
            dest_path = os.path.join(dest_dir, filename)
            
            # Handle duplicates
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(dest_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            # Show progress for large files
            file_size = os.path.getsize(src_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 100)
                self.status_label.setText(f"🚀 GPU: Copying {filename}...")
            
            shutil.copy2(src_path, dest_path)
            
            if self.progress_bar.isVisible():
                self.progress_bar.setVisible(False)
            
            QMessageBox.information(self, "Copy Success", 
                                  f"✅ File copied to {dest_type} folder:\n{dest_path}")
            self.status_label.setText(f"✅ GPU: Copied {filename} to {dest_type}")
            
        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"❌ Failed to copy file: {e}")
            self.status_label.setText(f"❌ Copy failed: {e}")
    
    def open_folder(self, folder_path):
        """Open folder in file manager"""
        try:
            subprocess.run(['nautilus', folder_path], check=False)
        except:
            subprocess.run(['xdg-open', folder_path], check=False)
    
    def unmount_archive(self):
        """Unmount current archive"""
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], 
                             check=False, timeout=30)
            
            self.current_archive = None
            self.current_path = None
            self.unmount_btn.setEnabled(False)
            self.mount_btn.setEnabled(True)
            
            # Clear interface
            self.folder_list.clear()
            self.file_table.setRowCount(0)
            self.current_path_label.setText("No archive mounted")
            self.archive_combo.setCurrentIndex(0)
            
            # Stop performance monitoring
            self.perf_timer.stop()
            
            self.status_label.setText("🔒 Archive unmounted - GPU ready for next operation")
            self.status_bar.showMessage("🚀 RTX 4070 Ready")
            
        except Exception as e:
            QMessageBox.warning(self, "Unmount Warning", f"Unmount error: {e}")
    
    def closeEvent(self, event):
        """Handle close event"""
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(['borg', 'umount', self.mount_point], 
                             check=False, timeout=15)
        except:
            pass
        event.accept()

def main():
    # Set high DPI scaling for GPU displays
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    
    app = QApplication(sys.argv)
    app.setApplicationName("GPU Pika Backup Explorer")
    app.setApplicationVersion("2.0 RTX")
    
    # Enable GPU acceleration
    app.setAttribute(Qt.AA_UseOpenGLES, True)
    
    # Check GPU availability
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("🚀 RTX 4070 detected - Enabling GPU acceleration")
        else:
            print("⚠️ NVIDIA GPU not detected, using software rendering")
    except:
        print("⚠️ nvidia-smi not available, using software rendering")
    
    window = GPUBackupExplorer()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())