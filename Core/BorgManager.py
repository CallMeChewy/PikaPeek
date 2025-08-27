# File: BorgManager.py
# Path: Core/BorgManager.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-10
# Last Modified: 2025-07-10 09:00AM
"""
Description: Handles all interactions with the BorgBackup command-line tool.
This module provides a Python interface for listing, mounting, unmounting, and extracting
data from Borg repositories and archives.
"""

import subprocess
import os
import json
from typing import List, Tuple, Optional

class BorgManager:
    """A class to manage Borg a"""

    def __init__(self, borg_executable="borg"):
        """
        Initializes the BorgManager.
        Args:
            borg_executable (str): The path to the borg executable.
        """
        self.borg_executable = borg_executable

    def _execute_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """
        Executes a given borg command using subprocess.
        Args:
            command (List[str]): The command to execute as a list of strings.
        Returns:
            Tuple[bool, str, str]: A tuple containing success (bool), stdout (str), and stderr (str).
        """
        try:
            process = subprocess.run(
                [self.borg_executable] + command,
                capture_output=True,
                text=True,
                check=False  # Do not raise exception on non-zero exit codes
            )
            success = process.returncode == 0
            return success, process.stdout, process.stderr
        except FileNotFoundError:
            return False, "", f"Error: The borg executable '{self.borg_executable}' was not found."
        except Exception as e:
            return False, "", f"An unexpected error occurred: {e}"

    def list_archives(self, repository_path: str) -> Tuple[bool, List[str], str]:
        """
        Lists all archives in a given Borg repository, filtering for active, non-zero size backups.
        Args:
            repository_path (str): The path to the Borg repository.
        Returns:
            Tuple[bool, List[str], str]: A tuple containing success (bool), a list of filtered archive names, and an error message (str).
        """
        command = ["list", "--json", repository_path]
        success, stdout, stderr = self._execute_command(command)
        if success:
            try:
                data = json.loads(stdout)
                archives = []
                for archive_info in data.get("archives", []):
                    # Assuming "size" is the key for archive size and it's in bytes
                    # and "name" is the key for archive name.
                    # Adjust keys if Borg's JSON output uses different names.
                    if archive_info.get("size", 0) > 0:
                        archives.append(archive_info.get("name"))
                return True, archives, ""
            except json.JSONDecodeError:
                return False, [], "Failed to parse Borg JSON output."
        else:
            return False, [], stderr

    def list_archive_contents(self, archive_path: str) -> Tuple[bool, List[str], str]:
        """
        Lists the contents of a specific archive.
        Args:
            archive_path (str): The full path to the archive (e.g., /path/to/repo::archive-name).
        Returns:
            Tuple[bool, List[str], str]: A tuple containing success (bool), a list of file paths, and an error message (str).
        """
        command = ["list", "--json", archive_path]
        success, stdout, stderr = self._execute_command(command)
        if success:
            try:
                data = json.loads(stdout)
                # Assuming Borg's JSON output for archive contents has a 'files' key
                # and each file entry has a 'path' key.
                # Adjust keys if Borg's JSON output uses different names.
                contents = [file_info.get("path") for file_info in data.get("files", []) if file_info.get("path")]
                return True, contents, ""
            except json.JSONDecodeError:
                return False, [], "Failed to parse Borg JSON output for archive contents."
        else:
            return False, [], stderr

    def mount(self, archive_path: str, mount_point: str) -> Tuple[bool, str]:
        """
        Mounts a Borg archive to a specified mount point.
        Args:
            archive_path (str): The full path to the archive to mount.
            mount_point (str): The directory where the archive will be mounted.
        Returns:
            Tuple[bool, str]: A tuple containing success (bool) and an error message (str).
        """
        if not os.path.isdir(mount_point):
            try:
                os.makedirs(mount_point, exist_ok=True)
            except OSError as e:
                return False, f"Failed to create mount point directory: {e}"

        command = ["mount", archive_path, mount_point]
        success, _, stderr = self._execute_command(command)
        return success, stderr

    def unmount(self, mount_point: str) -> Tuple[bool, str]:
        """
        Unmounts a Borg archive from a mount point.
        Args:
            mount_point (str): The directory where the archive is mounted.
        Returns:
            Tuple[bool, str]: A tuple containing success (bool) and an error message (str).
        """
        command = ["umount", mount_point]
        success, _, stderr = self._execute_command(command)
        return success, stderr

    def extract(self, archive_path: str, destination: str, files: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Extracts files or the entire archive to a destination.
        Args:
            archive_path (str): The archive to extract from.
            destination (str): The directory to extract files to.
            files (Optional[List[str]]): A list of specific files/directories to extract. Extracts all if None.
        Returns:
            Tuple[bool, str]: A tuple containing success (bool) and an error message (str).
        """
        command = ["extract", archive_path]
        if files:
            command.extend(files)
        
        # Borg extracts to the current working directory by default.
        # We need to run the command from the destination directory.
        try:
            original_cwd = os.getcwd()
            os.chdir(destination)
            success, _, stderr = self._execute_command(command)
            os.chdir(original_cwd)
            return success, stderr
        except Exception as e:
            return False, f"An error occurred during extraction: {e}"
