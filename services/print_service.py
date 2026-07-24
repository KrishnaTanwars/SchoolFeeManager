"""
Windows Desktop Printing & PDF Viewing Service.
Uses Windows Shell APIs and Qt Desktop Services for zero-dependency printing & previewing.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QMessageBox
from utils.logger import logger

class PrintService:
    @staticmethod
    def print_pdf(pdf_path: str, parent: Optional[QWidget] = None) -> bool:
        """Sends PDF directly to Windows printer using native Windows Shell print verb."""
        abspath = Path(pdf_path).resolve()
        if not abspath.exists():
            if parent:
                QMessageBox.critical(parent, "Error", f"PDF file not found: {pdf_path}")
            return False

        try:
            if sys.platform == "win32":
                os.startfile(str(abspath), "print")
                logger.info(f"Sent PDF to Windows printer: {abspath}")
                if parent:
                    QMessageBox.information(parent, "Printing", f"Sent receipt/report to default Windows printer:\n{abspath.name}")
                return True
            else:
                # Fallback for non-Windows (lpr)
                subprocess.run(["lpr", str(abspath)], check=True)
                return True
        except Exception as e:
            logger.error(f"Printing error for {pdf_path}: {e}", exc_info=True)
            # Fallback to opening in viewer
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(abspath)))
            return False

    @staticmethod
    def preview_pdf(pdf_path: str, parent: Optional[QWidget] = None) -> bool:
        """Launches high-resolution PDF in default system PDF viewer."""
        abspath = Path(pdf_path).resolve()
        if not abspath.exists():
            if parent:
                QMessageBox.critical(parent, "Error", f"PDF file not found: {pdf_path}")
            return False

        try:
            success = QDesktopServices.openUrl(QUrl.fromLocalFile(str(abspath)))
            if success:
                logger.info(f"Opened PDF preview: {abspath}")
            else:
                logger.warning(f"Failed QDesktopServices openUrl for: {abspath}")
            return success
        except Exception as e:
            logger.error(f"PDF Preview error for {pdf_path}: {e}", exc_info=True)
            if parent:
                QMessageBox.critical(parent, "Preview Error", f"Failed to preview PDF: {str(e)}")
            return False
