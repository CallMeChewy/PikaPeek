# Gemini Project: PikaPeek

## Project Overview

PikaPeek is a sophisticated Python-based GUI application designed for exploring and recovering files from Borg backup repositories. It leverages GPU acceleration (specifically optimized for the NVIDIA RTX 4070 with Vulkan) to provide a high-performance user experience. The application's flagship feature is its "Dark GPU Explorer," which offers a visually appealing, dark-themed interface inspired by modern development tools.

The architecture separates the core logic (Borg interaction) from the user interface (PySide6), with a multi-threaded approach to ensure the UI remains responsive during long-running backup operations.

## Building and Running

### Dependencies

The primary dependency is PySide6, which can be installed via pip:

```bash
pip install -r Requirements.txt
```

### Running the Application

The application is launched using a series of shell scripts located in the `Scripts/Launchers/` directory. The primary launchers are:

*   **Dark GPU Explorer (Recommended):**
    ```bash
    ./Scripts/Launchers/launch-dark-gpu-explorer.sh
    ```
*   **GPU Explorer (Light Theme):**
    ```bash
    ./Scripts/Launchers/launch-gpu-explorer.sh
    ```
*   **Standard Explorer (No GPU Acceleration):**
    ```bash
    ./Scripts/Launchers/run-backup-explorer.sh
    ```

Desktop-friendly `.desktop` files are also provided for easy access from the GUI.

### Testing

The project includes unit tests for its core components. These can be run using `pytest`:

```bash
python -m pytest tests/
```

## Development Conventions

*   **Design Standard:** The project adheres to a specific design standard documented as "AIDEV-PascalCase-2.1".
*   **Development Guide:** A detailed development guide is available in `CLAUDE.md`, providing instructions for developers.
*   **Asynchronous Operations:** All Borg commands are executed in separate `QThread` workers to prevent the GUI from freezing.
*   **Configuration:** Application settings are managed in `Config/config.ini`.
*   **Modular Structure:** The project is organized into distinct modules:
    *   `Core/`: Handles all interactions with the Borg command-line tool.
    *   `Gui/`: Contains the PySide6 GUI components.
    *   `Extensions/`: Houses the main explorer applications.
    *   `Scripts/`: Includes launcher scripts and other utilities.
