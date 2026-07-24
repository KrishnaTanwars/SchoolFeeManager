"""
Background Thread Worker System using PySide6 QThread and Signals.
Prevents UI freezing during database operations, PDF generation, backup, and printing.
"""

from typing import Callable, Any
from PySide6.QtCore import QThread, Signal, QObject
from utils.logger import logger

class WorkerSignals(QObject):
    finished = Signal(object)  # Emits result object
    error = Signal(str)       # Emits error string message
    progress = Signal(str)    # Emits progress message

class GenericWorker(QThread):
    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            logger.error(f"Background worker error executing {self.func.__name__}: {e}", exc_info=True)
            self.signals.error.emit(str(e))
