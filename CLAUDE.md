# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PikaPeek is a Python GUI application for exploring, mounting, and analyzing Borg backup repositories. It provides a two-pane interface where users can browse repositories/archives on the left and view mounted archive contents on the right.

## Development Commands

### Running the Application
```bash
# Main application entry point
python Main.py

# Alternative entry point via Pika subdirectory
cd Pika && python main.py

# Launch Dark Mode GPU Explorer (Recommended for RTX 4070)
./Scripts/Launchers/launch-dark-gpu-explorer.sh

# Launch GPU-Accelerated Explorer
./Scripts/Launchers/launch-gpu-explorer.sh

# Launch Simple Backup Explorer
./Scripts/Launchers/run-backup-explorer.sh
```

### Testing
```bash
# Run unit tests for BorgManager
python -m unittest tests/test_borg_manager.py

# Run from project root
python -m pytest tests/
```

### Dependencies
```bash
# Install main dependency
pip install PySide6

# Or use specific version from Pika directory
pip install -r Pika/requirements.txt
```

## Architecture Overview

### Core Components

**Main Application Flow:**
- `Main.py` → Entry point that launches PySide6 GUI
- `Gui/GuiMain.py` → Main window with two-pane layout (QSplitter)
- `Core/BorgManager.py` → Backend wrapper for borg command-line operations
- `Core/BorgWorker.py` → QThread wrapper for asynchronous borg operations

**Key Architectural Patterns:**
- **MVC-like separation:** GUI components in `Gui/`, business logic in `Core/`
- **Asynchronous operations:** All borg commands run in separate QThread workers
- **Configuration management:** Settings stored in `Config/config.ini` with dialog-based editing

### Core Module Responsibilities

**`Core/BorgManager.py`:**
- Executes borg commands via subprocess
- Parses JSON output from borg operations
- Handles repository listing, archive mounting/unmounting, file extraction
- Filters out zero-size archives automatically

**`Core/BorgWorker.py`:**
- QThread subclass for non-blocking borg operations
- Emits `finished(bool, object, str)` signal with success/result/error
- Supports operations: list_archives, list_archive_contents, mount, unmount, extract

**`Gui/GuiMain.py`:**
- Two-pane interface: QTreeWidget (left) + QTreeView with QFileSystemModel (right)
- Auto-loads default repository from config on startup
- Auto-mounts first archive when loading default repository
- Menu/toolbar actions for all borg operations

### Data Flow

1. **Repository Loading:** User selects repository → BorgWorker lists archives → Populates left pane tree
2. **Archive Mounting:** User clicks archive → BorgWorker mounts to `/tmp/pika-peek-mount-*` → Right pane shows mounted filesystem
3. **File Operations:** Extract operations run in background threads with status updates

### Configuration System

- **Config file:** `Config/config.ini`
- **Settings:** `default_repository`, `borg_executable_path`
- **Dialog:** `Gui/ConfigDialog.py` provides GUI for editing settings

### Testing Strategy

- Unit tests focus on `Core/BorgManager.py` with mocked subprocess calls
- Tests verify JSON parsing, error handling, and command construction
- Located in `tests/test_borg_manager.py`

## Important Implementation Details

### Threading Model
All borg operations MUST run in `BorgWorker` threads to prevent GUI freezing. Connect to the `finished` signal for results.

### Mount Point Management
- Temporary mount points use pattern: `/tmp/pika-peek-mount-{random_hex}`
- Mount points are created with `os.makedirs(exist_ok=True)`
- Cleanup happens automatically on unmount

### Archive Filtering
The application automatically filters out zero-size archives in `BorgManager.list_archives()` to show only meaningful backups.

### Auto-loading Behavior
On startup, if a `default_repository` is configured and exists, the application will:
1. Auto-load the repository
2. Auto-mount the first available archive
3. Display the mounted content immediately

## File Structure Notes

### Core Project Structure
- `Core/` - Business logic and Borg backup management
- `Gui/` - PySide6 GUI components and main window
- `Config/` - Configuration management and settings
- `tests/` - Unit tests for core functionality

### Extensions and Scripts
- `Extensions/` - Extended backup explorer applications:
  - `DarkGPUBackupExplorer.py` - Dark theme GPU-accelerated explorer (RTX 4070 optimized)
  - `GPUBackupExplorer.py` - Light theme GPU-accelerated explorer  
  - `PikaBackupExplorer.py` - Full-featured backup explorer
  - `SimplePikaExplorer.py` - Simplified backup browser
- `Scripts/` - Supporting scripts and utilities:
  - `Launchers/` - Shell scripts for launching applications
  - `BackupBrowsers/` - Web-based and alternative browser implementations
- `Utils/` - Development and maintenance utilities

### Build and Distribution
- `build/` and `dist/` - PyInstaller packaging directories
- `Pika/` - Alternative entry point or development environment
- Design standards documentation in `Docs/Standards/` follows AIDEV-PascalCase-2.1 convention

### Extensions Features
The Extensions directory contains GPU-accelerated backup explorers with:
- Vulkan backend rendering for high performance
- Real-time GPU monitoring (VRAM usage, temperature)
- Dark/light theme options for eye comfort
- Comprehensive file recovery and preview capabilities