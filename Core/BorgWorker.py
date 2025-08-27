from PySide6.QtCore import QThread, Signal
from Core.BorgManager import BorgManager

class BorgWorker(QThread):
    finished = Signal(bool, object, str) # success, result, error_message

    def __init__(self, borg_executable_path: str, operation: str, *args, is_initial_load: bool = False, **kwargs):
        super().__init__()
        self.borg_executable_path = borg_executable_path
        self.operation = operation
        self.args = args
        self.is_initial_load = is_initial_load
        self.kwargs = kwargs

    def run(self):
        borg_manager = BorgManager(self.borg_executable_path)
        success = False
        result = None
        error_message = ""

        try:
            if self.operation == "list_archives":
                success, result, error_message = borg_manager.list_archives(*self.args)
            elif self.operation == "list_archive_contents":
                success, result, error_message = borg_manager.list_archive_contents(*self.args)
            elif self.operation == "mount":
                success, error_message = borg_manager.mount(*self.args)
                result = None # Mount operation doesn't return a specific result beyond success/error
            elif self.operation == "unmount":
                success, error_message = borg_manager.unmount(*self.args)
                result = None # Unmount operation doesn't return a specific result beyond success/error
            elif self.operation == "extract":
                success, error_message = borg_manager.extract(*self.args)
                result = None # Extract operation doesn't return a specific result beyond success/error
            else:
                success = False
                error_message = f"Unknown operation: {self.operation}"
        except Exception as e:
            success = False
            error_message = str(e)

        self.finished.emit(success, result, error_message)
