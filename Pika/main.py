

import sys
import os
import subprocess
import re # Import regex module

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QTreeWidget, QTreeWidgetItem, QFileDialog, QLabel, QMessageBox, QStyle
)
from PySide6.QtCore import Qt, QProcess, QDateTime

class PikaBackupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pika Backup Browser")
        self.setGeometry(100, 100, 1000, 700)

        self.archive_path = "/media/herb/Linux_Drive_2/Pika Backups/backup-herb-Ubuntu-24.10-2TB-herb-2024-12-23"
        self.mounted_backup_path = None
        self.current_backup_id = None
        self.borg_passphrase = None # Store passphrase from .env

        self.load_passphrase_from_env() # Load passphrase at startup
        self.init_ui()

    def load_passphrase_from_env(self):
        env_file_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                for line in f:
                    match = re.match(r'passkey:\s*"([^"]+)"', line.strip())
                    if match:
                        self.borg_passphrase = match.group(1)
                        print(f"Passphrase loaded from .env: {self.borg_passphrase}")
                        break
            if not self.borg_passphrase:
                QMessageBox.warning(self, ".env Error", "Passkey not found in .env file or format is incorrect.")
        else:
            QMessageBox.warning(self, ".env Missing", "No .env file found. Please create one with 'passkey: "<your_passphrase>"'.")

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Archive Path Selection
        archive_layout = QHBoxLayout()
        self.archive_label = QLabel("Pika Archive Path:")
        archive_layout.addWidget(self.archive_label)
        self.archive_input = QLineEdit(self.archive_path)
        archive_layout.addWidget(self.archive_input)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_archive)
        archive_layout.addWidget(self.browse_button)
        self.load_archive_button = QPushButton("Load Archive")
        self.load_archive_button.clicked.connect(self.load_archive)
        archive_layout.addWidget(self.load_archive_button)
        main_layout.addLayout(archive_layout)

        # Backup List and File Viewer
        content_layout = QHBoxLayout()
        
        # Backup List
        backup_list_layout = QVBoxLayout()
        backup_list_label = QLabel("Available Backups:")
        backup_list_layout.addWidget(backup_list_label)
        self.backup_list_widget = QListWidget()
        self.backup_list_widget.itemClicked.connect(self.select_backup)
        backup_list_layout.addWidget(self.backup_list_widget)
        content_layout.addLayout(backup_list_layout, 1)

        # File Viewer
        file_viewer_layout = QVBoxLayout()
        file_viewer_label = QLabel("Backup Contents:")
        file_viewer_layout.addWidget(file_viewer_label)
        self.file_tree_widget = QTreeWidget()
        self.file_tree_widget.setHeaderLabels(["Name", "Size", "Permissions", "User", "Group", "Date Modified"])
        file_viewer_layout.addWidget(self.file_tree_widget)
        content_layout.addLayout(file_viewer_layout, 3)

        main_layout.addLayout(content_layout)

        # Restore Buttons
        restore_layout = QHBoxLayout()
        self.restore_original_button = QPushButton("Restore to Original Location")
        self.restore_original_button.clicked.connect(self.restore_to_original)
        self.restore_original_button.setEnabled(False)
        restore_layout.addWidget(self.restore_original_button)
        self.restore_to_button = QPushButton("Restore to...")
        self.restore_to_button.clicked.connect(self.restore_to_custom_location)
        self.restore_to_button.setEnabled(False)
        restore_layout.addWidget(self.restore_to_button)
        main_layout.addLayout(restore_layout)

        self.setLayout(main_layout)

    def browse_archive(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Pika Archive Directory")
        if dir_path:
            self.archive_input.setText(dir_path)
            self.archive_path = dir_path

    def load_archive(self):
        self.archive_path = self.archive_input.text()
        if not os.path.isdir(self.archive_path):
            QMessageBox.warning(self, "Invalid Path", "The specified archive path does not exist or is not a directory.")
            return
        
        if not self.borg_passphrase:
            QMessageBox.critical(self, "Passphrase Error", "Borg passphrase not loaded. Cannot mount archive.")
            return

        self.backup_list_widget.clear()
        self.file_tree_widget.clear()
        self.restore_original_button.setEnabled(False)
        self.restore_to_button.setEnabled(False)
        self.current_backup_id = None
        self.unmount_current_backup()

        self.run_borg_command(["list", "--json", self.archive_path], self.parse_backup_list, self.borg_passphrase)

    def parse_backup_list(self, stdout):
        try:
            import json
            data = json.loads(stdout)
            print(f"Parsed borg list JSON: {json.dumps(data, indent=2)}") # Debug print
            archives = data.get("archives", [])
            # Sort archives by timestamp in descending order (most recent first)
            archives.sort(key=lambda x: x.get("time", ""), reverse=True)
            for archive in archives:
                name = archive.get("name")
                id = archive.get("id")
                timestamp = archive.get("time")
                print(f"Adding backup to list: Name={name}, ID={id}, Timestamp={timestamp}") # Debug print
                self.backup_list_widget.addItem(f"{name} ({timestamp}) - ID: {id}")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Failed to parse borg list output. Is the repository valid and passphrase correct?")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def select_backup(self, item):
        self.unmount_current_backup()
        self.file_tree_widget.clear()
        self.restore_original_button.setEnabled(False)
        self.restore_to_button.setEnabled(False)

        text = item.text()
        # Extract ID from the item text
        try:
            self.current_backup_id = text.split("ID: ")[1]
            print(f"Selected backup ID for mounting: {self.current_backup_id}") # Debug print
        except IndexError:
            QMessageBox.warning(self, "Error", "Could not extract backup ID from selected item.")
            return

        if not self.borg_passphrase:
            QMessageBox.critical(self, "Passphrase Error", "Borg passphrase not loaded. Cannot mount archive.")
            return

        self.mounted_backup_path = os.path.join("/tmp", f"pika_mount_{os.getpid()}")
        os.makedirs(self.mounted_backup_path, exist_ok=True)

        self.run_borg_command(
            ["mount", f"{self.archive_path}::{self.current_backup_id}", self.mounted_backup_path],
            self.on_mount_complete, self.borg_passphrase
        )

    def on_mount_complete(self, stdout):
        if self.mounted_backup_path and os.path.ismount(self.mounted_backup_path):
            self.populate_file_tree(self.mounted_backup_path, self.file_tree_widget.invisibleRootItem())
            self.restore_original_button.setEnabled(True)
            self.restore_to_button.setEnabled(True)
        else:
            QMessageBox.critical(self, "Mount Error", 
                                 "Failed to mount the backup. This could be due to an incorrect passphrase, "
                                 "FUSE not working, or other issues. Please verify your passphrase and try again. "
                                 f"You can also try running the command manually in a terminal: "
                                 f"BORG_PASSPHRASE='{self.borg_passphrase}' borg mount {self.archive_path}::{self.current_backup_id} {self.mounted_backup_path}")
            self.unmount_current_backup()

    def populate_file_tree(self, path, parent_item):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            item = QTreeWidgetItem([entry])
            parent_item.addChild(item)
            
            if os.path.isdir(full_path):
                item.setIcon(0, QApplication.style().standardIcon(QStyle.SP_DirIcon))
                self.populate_file_tree(full_path, item)
            else:
                item.setIcon(0, QApplication.style().standardIcon(QStyle.SP_FileIcon))
                try:
                    stat_info = os.stat(full_path)
                    item.setText(1, str(stat_info.st_size))
                    item.setText(2, oct(stat_info.st_mode)[-4:])
                    import pwd, grp
                    item.setText(3, pwd.getpwuid(stat_info.st_uid).pw_name)
                    item.setText(4, grp.getgrgid(stat_info.st_gid).gr_name)
                    item.setText(5, QDateTime.fromSecsSinceEpoch(stat_info.st_mtime).toString(Qt.ISODate))
                except Exception as e:
                    print(f"Could not get file info for {full_path}: {e}")

    def restore_to_original(self):
        selected_items = self.file_tree_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select files or folders to restore.")
            return

        # Confirm with user
        reply = QMessageBox.question(self, "Confirm Restore", 
                                     "Are you sure you want to restore selected items to their original locations? This may overwrite existing files.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        for item in selected_items:
            # Reconstruct the original path from the mounted path
            relative_path = self.get_path_from_tree_item(item)
            if relative_path.startswith(self.mounted_backup_path):
                original_target_path = relative_path[len(self.mounted_backup_path):].lstrip(os.sep)
            else:
                original_target_path = relative_path # Should not happen if logic is correct

            # Borg extract command will handle the full path from the archive root
            # We need to extract to the root directory and borg will place it correctly
            # based on the path within the archive.
            # For simplicity, we'll extract to a temp dir and then move, or use borg's --extract-path
            # For now, let's just show the command.
            QMessageBox.information(self, "Restore Info", 
                                    f"Simulating restore of {relative_path} to original location. Actual command would be: borg extract {self.archive_path}::{self.current_backup_id} {relative_path}")

    def restore_to_custom_location(self):
        selected_items = self.file_tree_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select files or folders to restore.")
            return

        dest_dir = QFileDialog.getExistingDirectory(self, "Select Destination Directory for Restore")
        if not dest_dir:
            return

        for item in selected_items:
            relative_path = self.get_path_from_tree_item(item)
            QMessageBox.information(self, "Restore Info", 
                                    f"Simulating restore of {relative_path} to {dest_dir}. Actual command would be: borg extract {self.archive_path}::{self.current_backup_id} --paths {relative_path} {dest_dir}")

    def get_path_from_tree_item(self, item):
        path_parts = []
        current_item = item
        while current_item:
            path_parts.insert(0, current_item.text(0))
            current_item = current_item.parent()
        
        # The first part will be the mount point, which we need to remove for relative path within backup
        # Or, if we are populating from the mounted path, the first part is the mount point itself.
        # We need the path relative to the mounted_backup_path
        full_path_in_mount = os.path.join(self.mounted_backup_path, *path_parts[1:]) # Skip the root item which is the mount point
        return full_path_in_mount

    def run_borg_command(self, command_args, callback=None, passphrase=None):
        full_command = ["borg"] + command_args
        print(f"Running command: {' '.join(full_command)}")
        
        process = QProcess(self)
        process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process))
        process.readyReadStandardError.connect(lambda: self.handle_stderr(process))
        process.finished.connect(lambda: self.on_command_finished(process, callback))
        
        process.stdout_buffer = ""
        process.stderr_buffer = ""

        # Set environment variables for the process
        environment = process.processEnvironment()
        if passphrase:
            environment.insert("BORG_PASSPHRASE", passphrase)
        process.setProcessEnvironment(environment)
        
        process.start("borg", command_args)
        if not process.waitForStarted():
            QMessageBox.critical(self, "Process Error", f"Failed to start borg process: {process.errorString()}")

    def handle_stdout(self, process):
        process.stdout_buffer += process.readAllStandardOutput().data().decode()

    def handle_stderr(self, process):
        process.stderr_buffer += process.readAllStandardError().data().decode()

    def on_command_finished(self, process, callback):
        command_str = ' '.join(process.arguments()) # Get the command that was run
        print(f"Command finished: {command_str}")
        if process.exitCode() != 0:
            QMessageBox.critical(self, "Borg Command Error", f"Command '{command_str}' failed with exit code {process.exitCode()}:\n{process.stderr_buffer}")
        elif callback:
            callback(process.stdout_buffer)

        process.deleteLater()

    def unmount_current_backup(self):
        if self.mounted_backup_path and os.path.ismount(self.mounted_backup_path):
            print(f"Unmounting {self.mounted_backup_path}")
            try:
                # Passphrase might be needed for unmount if the mount command used it
                # Use the stored passphrase
                env = os.environ.copy()
                if self.borg_passphrase:
                    env["BORG_PASSPHRASE"] = self.borg_passphrase

                subprocess.run(["borg", "umount", self.mounted_backup_path], check=True, capture_output=True, env=env)
                print(f"Successfully unmounted {self.mounted_backup_path}")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Unmount Error", f"Failed to unmount {self.mounted_backup_path}:\n{e.stderr.decode()}")
            except Exception as e:
                QMessageBox.critical(self, "Unmount Error", f"An unexpected error occurred during unmount: {e}")
            finally:
                if os.path.exists(self.mounted_backup_path) and not os.listdir(self.mounted_backup_path):
                    os.rmdir(self.mounted_backup_path)
                self.mounted_backup_path = None

    def closeEvent(self, event):
        self.unmount_current_backup()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PikaBackupApp()
    window.show()
    sys.exit(app.exec())
