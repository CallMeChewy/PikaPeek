# File: test_borg_manager.py
# Path: tests/test_borg_manager.py

import unittest
import sys
import os

# Add the project root to the Python path to allow for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock
from Core.BorgManager import BorgManager

class TestBorgManager(unittest.TestCase):

    def setUp(self):
        """Set up a BorgManager instance for each test."""
        self.manager = BorgManager()

    @patch('subprocess.run')
    def test_list_archives_success(self, mock_subprocess_run):
        """Test that list_archives correctly parses successful borg JSON output and filters by size."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = '''
{
    "archives": [
        {"name": "archive1", "size": 1024},
        {"name": "archive2", "size": 0},
        {"name": "archive3", "size": 2048}
    ]
}
'''
        mock_process.stderr = ''
        mock_subprocess_run.return_value = mock_process

        success, archives, error = self.manager.list_archives('/fake/repo')

        self.assertTrue(success)
        self.assertEqual(len(archives), 2)
        self.assertIn('archive1', archives)
        self.assertIn('archive3', archives)
        self.assertNotIn('archive2', archives)
        self.assertEqual(error, '')
        mock_subprocess_run.assert_called_once_with(
            ['borg', 'list', '--json', '/fake/repo'],
            capture_output=True, text=True, check=False
        )

    @patch('subprocess.run')
    def test_list_archives_failure(self, mock_subprocess_run):
        """Test that list_archives handles a failed borg command."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = ''
        mock_process.stderr = 'Repository not found'
        mock_subprocess_run.return_value = mock_process

        success, archives, error = self.manager.list_archives('/fake/repo')

        self.assertFalse(success)
        self.assertEqual(len(archives), 0)
        self.assertEqual(error, 'Repository not found')

    @patch('subprocess.run')
    def test_list_archive_contents_success(self, mock_subprocess_run):
        """Test listing contents of an archive successfully with JSON output."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = '''
{
    "files": [
        {"path": "path/to/file1.txt", "type": "f", "size": 100},
        {"path": "path/to/dir", "type": "d"}
    ]
}
'''
        mock_process.stderr = ''
        mock_subprocess_run.return_value = mock_process

        success, contents, error = self.manager.list_archive_contents('/fake/repo::archive1')

        self.assertTrue(success)
        self.assertEqual(len(contents), 2)
        self.assertIn('path/to/file1.txt', contents)
        self.assertIn('path/to/dir', contents)
        self.assertEqual(error, '')
        mock_subprocess_run.assert_called_once_with(
            ['borg', 'list', '--json', '/fake/repo::archive1'],
            capture_output=True, text=True, check=False
        )

    @patch('os.makedirs')
    @patch('subprocess.run')
    def test_mount_success(self, mock_subprocess_run, mock_makedirs):
        """Test mounting an archive successfully."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = ''
        mock_process.stderr = ''
        mock_subprocess_run.return_value = mock_process

        success, error = self.manager.mount('/fake/repo::archive1', '/tmp/mountpoint')

        self.assertTrue(success)
        self.assertEqual(error, '')
        mock_makedirs.assert_called_once_with('/tmp/mountpoint', exist_ok=True)
        mock_subprocess_run.assert_called_once_with(
            ['borg', 'mount', '/fake/repo::archive1', '/tmp/mountpoint'],
            capture_output=True, text=True, check=False
        )

    @patch('subprocess.run')
    def test_unmount_success(self, mock_subprocess_run):
        """Test unmounting an archive successfully."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = ''
        mock_process.stderr = ''
        mock_subprocess_run.return_value = mock_process

        success, error = self.manager.unmount('/tmp/mountpoint')

        self.assertTrue(success)
        self.assertEqual(error, '')
        mock_subprocess_run.assert_called_once_with(
            ['borg', 'umount', '/tmp/mountpoint'],
            capture_output=True, text=True, check=False
        )

    @patch('os.chdir')
    @patch('os.getcwd')
    @patch('subprocess.run')
    def test_extract_success(self, mock_subprocess_run, mock_getcwd, mock_chdir):
        """Test extracting an entire archive successfully."""
        mock_getcwd.return_value = '/original/dir'
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = ''
        mock_process.stderr = ''
        mock_subprocess_run.return_value = mock_process

        success, error = self.manager.extract('/fake/repo::archive1', '/tmp/destination')

        self.assertTrue(success)
        self.assertEqual(error, '')
        # Check that we changed to the destination directory
        mock_chdir.assert_any_call('/tmp/destination')
        # Check that we changed back to the original directory
        mock_chdir.assert_any_call('/original/dir')
        mock_subprocess_run.assert_called_once_with(
            ['borg', 'extract', '/fake/repo::archive1'],
            capture_output=True, text=True, check=False
        )

    @patch('os.chdir')
    @patch('os.getcwd')
    @patch('subprocess.run')
    def test_extract_with_files_success(self, mock_subprocess_run, mock_getcwd, mock_chdir):
        """Test extracting specific files from an archive successfully."""
        mock_getcwd.return_value = '/original/dir'
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = ''
        mock_process.stderr = ''
        mock_subprocess_run.return_value = mock_process

        files_to_extract = ['path/to/file1.txt', 'path/to/dir']
        success, error = self.manager.extract('/fake/repo::archive1', '/tmp/destination', files=files_to_extract)

        self.assertTrue(success)
        self.assertEqual(error, '')
        mock_subprocess_run.assert_called_once_with(
            ['borg', 'extract', '/fake/repo::archive1', 'path/to/file1.txt', 'path/to/dir'],
            capture_output=True, text=True, check=False
        )

if __name__ == '__main__':
    unittest.main()
