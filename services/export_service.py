"""
CSV Data Export Service for Reports & Student Master Records.
"""

import csv
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from config.app_config import EXPORTS_DIR
from utils.logger import logger

class ExportService:
    @staticmethod
    def export_to_csv(
        headers: List[str],
        rows: List[List[str]],
        filename_prefix: str = "Export",
        output_path: Optional[str] = None
    ) -> tuple[bool, str]:
        """Exports data rows to CSV file format."""
        try:
            if not output_path:
                filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                output_path = str(EXPORTS_DIR / filename)

            with open(output_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)

            logger.info(f"Successfully exported CSV to: {output_path}")
            return True, output_path
        except Exception as e:
            logger.error(f"CSV Export error: {e}", exc_info=True)
            return False, f"Export error: {str(e)}"

    @staticmethod
    def generate_sample_student_csv(output_path: Optional[str] = None) -> tuple[bool, str]:
        """Generates a sample CSV template pre-filled with correct columns and example rows."""
        headers = [
            "Admission Number", "Roll Number", "Student Name", "Class", "Section",
            "Father Name", "Mother Name", "Mobile Number", "Address",
            "Date Of Admission", "Session", "Status"
        ]
        sample_rows = [
            ["ADM/2024/099", "199", "Aarav Sharma", "Class 10", "A", "Rajesh Sharma", "Sunita Sharma", "9876543210", "123 Green Park, New Delhi", "2024-04-01", "2024-2025", "Active"],
            ["ADM/2024/100", "200", "Ananya Verma", "Class 12", "B", "Sanjay Verma", "Meena Verma", "9811223344", "456 Vasant Kunj, New Delhi", "2024-04-01", "2024-2025", "Active"],
        ]
        if not output_path:
            output_path = str(EXPORTS_DIR / "sample_students_import.csv")

        return ExportService.export_to_csv(headers, sample_rows, filename_prefix="Sample_Students", output_path=output_path)
