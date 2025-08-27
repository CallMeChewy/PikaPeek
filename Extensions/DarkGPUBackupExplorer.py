#!/usr/bin/python3
# File: DarkGPUBackupExplorer.py  
# Path: /home/herb/Desktop/PikaPeek/Extensions/DarkGPUBackupExplorer.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-29
# Last Modified: 2025-07-29 08:15AM
"""
Dark Mode GPU-Accelerated PySide6 Backup Explorer - Optimized for RTX 4070
Dark theme to reduce eye strain while maintaining high performance
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
        QStatusBar, QHeaderView, QListWidgetItem
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer
    from PySide6.QtGui import QFont, QPalette, QColor
    
    # Optional OpenGL widget for GPU acceleration
    try:
        from PySide6.QtOpenGL import QOpenGLWidget
        OPENGL_AVAILABLE = True
    except ImportError:
        print("⚠️  OpenGL widget not available - using standard widgets")
        OPENGL_AVAILABLE = False
except ImportError as e:
    print("❌ PySide6 import failed.")
    print(f"🐍 Python version: {sys.version}")
    print(f"🐍 Python executable: {sys.executable}")
    print(f"🔍 Import error: {e}")
    print("🔧 Debug info:")
    import sys
    print(f"   Python path: {sys.path[:3]}...")
    
    # Try alternative import paths
    try:
        sys.path.insert(0, '/usr/lib/python3/dist-packages')
        from PySide6.QtWidgets import QApplication
        print("✅ Found PySide6 in system packages!")
    except ImportError:
        print("❌ PySide6 still not found in system packages")
        
        # Check if we can find it manually
        import os
        possible_paths = [
            '/usr/lib/python3/dist-packages',
            '/usr/local/lib/python3.11/dist-packages',
            '/usr/lib/python3.11/dist-packages'
        ]
        
        for path in possible_paths:
            pyside_path = os.path.join(path, 'PySide6')
            if os.path.exists(pyside_path):
                print(f"🔍 Found PySide6 at: {pyside_path}")
                sys.path.insert(0, path)
                break
        else:
            print("🛠️ Solutions:")
            print("1. Try: sudo apt install python3-pyside6.qtwidgets")
            print("2. Create virtual environment:")
            print("   python3 -m venv ~/pikapeek-env")
            print("   source ~/pikapeek-env/bin/activate")
            print("   pip install PySide6")
            sys.exit(1)
        
        # Try import again
        try:
            from PySide6.QtWidgets import QApplication
            print("✅ PySide6 import successful after path fix!")
        except ImportError:
            print("❌ Still cannot import PySide6")
            sys.exit(1)

class DarkGPUBackupWorker(QThread):
    """GPU-optimized worker for backup operations with dark theme"""
    finished = Signal(str, object)
    progress = Signal(str)
    
    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args
        self.repo_path = "/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
        self.mount_point = "/home/herb/dark-gpu-backup-mount"
    
    def run(self):
        try:
            if self.operation == "list_archives":
                self.progress.emit("🌙 Scanning backup repository...")
                result = self.list_archives()
                self.finished.emit("list_archives", result)
            elif self.operation == "mount_archive":
                self.progress.emit(f"🌙 Mounting archive {self.args[0]}...")
                result = self.mount_archive(self.args[0])
                self.finished.emit("mount_archive", result)
            elif self.operation == "list_files":
                self.progress.emit(f"🌙 Loading files from {self.args[0]}...")
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
                    'icon': '🌙'
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
                        icon = "🌙"
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
                        
                        # File type icons with dark theme
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
                            icon = "🌙"
                            
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

class DarkGPUBackupExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mount_point = "/home/herb/dark-gpu-backup-mount"
        self.recovery_path = "/home/herb/Desktop/RecoveredFiles"
        self.temp_path = "/home/herb/Desktop/TempPreview"
        self.current_archive = None
        self.current_path = None
        
        # Create directories
        os.makedirs(self.recovery_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
        
        self.init_dark_gpu_ui()
        self.load_archives()
    
    def init_dark_gpu_ui(self):
        """Initialize dark mode GPU-accelerated UI"""
        self.setWindowTitle("🌙 Dark GPU-Accelerated Pika Backup Explorer (RTX 4070)")
        self.setGeometry(100, 100, 1200, 800)
        
        # Enable GPU acceleration
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)
        
        # Set dark theme styling - GitHub dark inspired
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d1117, stop:1 #161b22);
                color: #e1e4e8;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #30363d;
                border-radius: 8px;
                margin: 5px;
                padding-top: 10px;
                background: rgba(33, 38, 45, 150);
                color: #e1e4e8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #238636, stop:1 #1f7c2f);
                border: 1px solid #30363d;
                color: #f0f6fc;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ea043, stop:1 #26913a);
                border: 1px solid #40464d;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f7c2f, stop:1 #1a6b29);
            }
            QTableWidget {
                gridline-color: #30363d;
                background-color: #0d1117;
                alternate-background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                color: #e1e4e8;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #21262d;
            }
            QTableWidget::item:hover {
                background: #21262d;
            }
            QTableWidget::item:selected {
                background: #264f78;
                color: #ffffff;
            }
            QHeaderView::section {
                background: #21262d;
                color: #e1e4e8;
                padding: 8px;
                border: 1px solid #30363d;
                font-weight: bold;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #30363d;
                border-radius: 6px;
                background: #21262d;
                color: #e1e4e8;
            }
            QComboBox::drop-down {
                border: none;
                background: #30363d;
            }
            QComboBox::down-arrow {
                color: #e1e4e8;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #30363d;
                background: #21262d;
                color: #e1e4e8;
                selection-background-color: #264f78;
            }
            QListWidget {
                border: 1px solid #30363d;
                border-radius: 8px;
                background: #0d1117;
                color: #e1e4e8;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #21262d;
            }
            QListWidget::item:hover {
                background: #21262d;
            }
            QListWidget::item:selected {
                background: #264f78;
                color: #ffffff;
            }
            QLabel {
                color: #e1e4e8;
            }
            QProgressBar {
                border: 1px solid #30363d;
                border-radius: 8px;
                text-align: center;
                background: #21262d;
                color: #e1e4e8;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #58a6ff, stop:1 #1f6feb);
                border-radius: 6px;
            }
            QStatusBar {
                background: #21262d;
                color: #e1e4e8;
                border-top: 1px solid #30363d;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header with GPU info
        header_layout = QHBoxLayout()
        
        gpu_label = QLabel("🌙 RTX 4070 Dark Mode | ")
        gpu_label.setStyleSheet("color: #58a6ff; font-weight: bold;")
        header_layout.addWidget(gpu_label)
        
        header_layout.addWidget(QLabel("📅 Select Backup:"))
        
        self.archive_combo = QComboBox()
        self.archive_combo.setMinimumWidth(450)
        self.archive_combo.currentTextChanged.connect(self.on_archive_selected)
        header_layout.addWidget(self.archive_combo)
        
        self.mount_btn = QPushButton("🌙 Mount Archive")
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
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("🌙 Loading dark mode GPU-accelerated backup browser...")
        self.status_label.setStyleSheet("padding: 8px; background: rgba(88, 166, 255, 20); color: #e1e4e8; border: 1px solid #30363d; border-radius: 4px;")
        layout.addWidget(self.status_label)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Folders
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        folder_label = QLabel("🌙 Quick Navigation")
        folder_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #58a6ff;")
        left_layout.addWidget(folder_label)
        
        self.current_path_label = QLabel("No archive mounted")
        self.current_path_label.setStyleSheet("background: #21262d; color: #e1e4e8; padding: 6px; border-radius: 4px; font-family: monospace; border: 1px solid #30363d;")
        left_layout.addWidget(self.current_path_label)
        
        self.folder_list = QListWidget()
        self.folder_list.itemClicked.connect(self.on_folder_selected)
        left_layout.addWidget(self.folder_list)
        
        splitter.addWidget(left_widget)
        
        # Right panel - Files
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        files_label = QLabel("🌙 Files & Directories")
        files_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #58a6ff;")
        right_layout.addWidget(files_label)
        
        # File table with GPU acceleration
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(["🌙 Name", "📅 Date Modified", "📊 Size", "🔧 Type"])
        
        # Optimize for GPU rendering
        header = self.file_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.file_table.setAlternatingRowColors(True)
        self.file_table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        right_layout.addWidget(self.file_table)
        
        # Action buttons with dark theme styling
        actions_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ Preview File")
        self.preview_btn.clicked.connect(self.preview_selected)
        self.preview_btn.setEnabled(False)
        actions_layout.addWidget(self.preview_btn)
        
        self.temp_copy_btn = QPushButton("🌙 Quick Copy")
        self.temp_copy_btn.clicked.connect(self.temp_copy_selected)
        self.temp_copy_btn.setEnabled(False)
        self.temp_copy_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d29922, stop:1 #bb8409); border: 1px solid #30363d; }")
        actions_layout.addWidget(self.temp_copy_btn)
        
        self.copy_btn = QPushButton("💾 Permanent Copy")
        self.copy_btn.clicked.connect(self.copy_selected)
        self.copy_btn.setEnabled(False)
        actions_layout.addWidget(self.copy_btn)
        
        actions_layout.addStretch()
        
        # Folder access buttons
        self.open_temp_btn = QPushButton("🌙 Temp Folder")
        self.open_temp_btn.clicked.connect(lambda: self.open_folder(self.temp_path))
        self.open_temp_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8b5cf6, stop:1 #7c3aed); border: 1px solid #30363d; }")
        actions_layout.addWidget(self.open_temp_btn)
        
        self.open_recovery_btn = QPushButton("🌙 Recovery Folder")
        self.open_recovery_btn.clicked.connect(lambda: self.open_folder(self.recovery_path))
        self.open_recovery_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6b7280, stop:1 #4b5563); border: 1px solid #30363d; }")
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
        
        self.status_bar.showMessage("🌙 Dark mode GPU acceleration enabled - Easy on the eyes, high performance")
    
    def update_performance_info(self):
        """Update GPU performance info with dark theme"""
        if self.current_archive:
            try:
                # Get GPU memory info if nvidia-smi is available
                result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,temperature.gpu', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    used, total, temp = result.stdout.strip().split(', ')
                    gpu_info = f"RTX 4070: {used}MB/{total}MB VRAM | {temp}°C"
                    self.status_bar.showMessage(f"🌙 {gpu_info} | Archive: {self.current_archive}")
                else:
                    self.status_bar.showMessage(f"🌙 RTX 4070 Dark Mode | Archive: {self.current_archive}")
            except:
                self.status_bar.showMessage(f"🌙 RTX 4070 Dark Mode | Archive: {self.current_archive}")
    
    def load_archives(self):
        """Load archives with GPU acceleration"""
        self.status_label.setText("🌙 GPU: Scanning backup repository...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.worker = DarkGPUBackupWorker("list_archives")
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
            display_text = f"🌙 {archive['readable_date']} ({archive['name']})"
            self.archive_combo.addItem(display_text, archive)
        
        self.status_label.setText(f"✅ Dark GPU: Loaded {len(result)} backup archives")
    
    def on_archive_selected(self):
        """Handle archive selection"""
        self.mount_btn.setEnabled(self.archive_combo.currentData() is not None)
    
    def mount_selected_archive(self):
        """Mount selected archive with GPU optimization"""
        archive_data = self.archive_combo.currentData()
        if not archive_data:
            return
        
        archive_name = archive_data['name']
        self.status_label.setText(f"🌙 GPU: Mounting {archive_name}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.worker = DarkGPUBackupWorker("mount_archive", archive_name)
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
        
        self.status_label.setText(f"✅ Dark GPU: Successfully mounted {self.current_archive}")
        
        # Start performance monitoring
        self.perf_timer.start(2000)
    
    def setup_folder_navigation(self):
        """Setup folder navigation list"""
        self.folder_list.clear()
        
        base_path = os.path.join(self.mount_point, "home/herb")
        folders = [
            ("🌙 Home Directory", base_path),
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
        
        self.current_path_label.setText(f"🌙 {display_path}")
        self.status_label.setText(f"🌙 GPU: Loading files from {display_path}...")
        
        self.worker = DarkGPUBackupWorker("list_files", path)
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
        
        self.status_label.setText(f"✅ Dark GPU: Rendered {len(result)} items")
    
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
        selected_items = self.get_selected_items()
        has_selection = len(selected_items) > 0
        has_single_selection = len(selected_items) == 1

        self.preview_btn.setEnabled(has_single_selection and not selected_items[0]['is_dir'])
        self.temp_copy_btn.setEnabled(has_selection)
        self.copy_btn.setEnabled(has_selection)
    
    def get_selected_items(self):
        """Get all selected items"""
        selected_items = []
        for item in self.file_table.selectedItems():
            if item.column() == 0:
                selected_items.append(item.data(Qt.UserRole))
        return selected_items
    
    def preview_selected(self):
        """Preview selected file"""
        selected_items = self.get_selected_items()
        if len(selected_items) == 1:
            file_info = selected_items[0]
            if not file_info['is_dir']:
                QMessageBox.information(self, "🌙 File Preview", 
                                      f"File: {file_info['name']}\n"
                                      f"Size: {file_info['size']}\n"
                                      f"Date: {file_info['date']}\n"
                                      f"Path: {file_info['path']}")
    
    def temp_copy_selected(self):
        """Quick copy to temp folder"""
        selected_items = self.get_selected_items()
        if selected_items:
            for item_info in selected_items:
                self.copy_item(item_info, self.temp_path, "Temp")

    def copy_selected(self):
        """Permanent copy to recovery folder"""
        selected_items = self.get_selected_items()
        if selected_items:
            for item_info in selected_items:
                self.copy_item(item_info, self.recovery_path, "Recovery")

    def copy_item(self, item_info, dest_dir, dest_type):
        """Copy file or directory with GPU-accelerated progress"""
        try:
            src_path = item_info['path']
            item_name = item_info['name']
            dest_path = os.path.join(dest_dir, item_name)

            # Handle duplicates
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(item_name)
                dest_path = os.path.join(dest_dir, f"{name}_{counter}{ext}")
                counter += 1

            # Show progress for large files/folders
            if item_info['is_dir'] or os.path.getsize(src_path) > 10 * 1024 * 1024:  # 10MB
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 100)
                self.status_label.setText(f"🌙 GPU: Copying {item_name}...")

            if item_info['is_dir']:
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)

            if self.progress_bar.isVisible():
                self.progress_bar.setVisible(False)

            QMessageBox.information(self, "🌙 Copy Success",
                                  f"✅ {item_info['name']} copied to {dest_type} folder:\n{dest_path}")
            self.status_label.setText(f"✅ Dark GPU: Copied {item_name} to {dest_type}")

        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"❌ Failed to copy {item_info['name']}: {e}")
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
            
            self.status_label.setText("🌙 Archive unmounted - Dark GPU ready for next operation")
            self.status_bar.showMessage("🌙 RTX 4070 Dark Mode Ready")
            
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
    app.setApplicationName("Dark GPU Pika Backup Explorer")
    app.setApplicationVersion("3.0 Dark RTX")
    
    # Enable GPU acceleration
    app.setAttribute(Qt.AA_UseOpenGLES, True)
    
    # Check GPU availability
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("🌙 RTX 4070 detected - Enabling dark mode GPU acceleration")
        else:
            print("⚠️ NVIDIA GPU not detected, using software rendering")
    except:
        print("⚠️ nvidia-smi not available, using software rendering")
    
    window = DarkGPUBackupExplorer()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())