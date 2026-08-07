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
    def export_to_excel(
        headers: List[str],
        rows: List[List[str]],
        filename_prefix: str = "Export_Ledger",
        output_path: Optional[str] = None
    ) -> tuple[bool, str]:
        """Exports data rows to Excel-compatible Spreadsheet format (.xlsx / .csv)."""
        try:
            if not output_path:
                filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                output_path = str(EXPORTS_DIR / filename)

            # Check if openpyxl is available, otherwise use clean TSV/CSV-Excel format
            try:
                import openpyxl
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Receipt Ledger"
                ws.append(headers)
                for row in rows:
                    ws.append(row)
                wb.save(output_path)
            except ImportError:
                # Fallback to UTF-8-SIG CSV/TSV format which opens natively in Microsoft Excel
                with open(output_path, mode='w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f, delimiter='\t')
                    writer.writerow(headers)
                    writer.writerows(rows)

            logger.info(f"Successfully exported Excel file to: {output_path}")
            return True, output_path
        except Exception as e:
            logger.error(f"Excel Export error: {e}", exc_info=True)
            return False, f"Excel Export error: {str(e)}"

    @staticmethod
    def export_to_pdf_ledger(
        title: str,
        headers: List[str],
        rows: List[List[str]],
        total_info: Optional[dict] = None,
        output_path: Optional[str] = None
    ) -> tuple[bool, str]:
        """Exports receipt ledger data rows to ReportLab PDF report."""
        try:
            from services.pdf_service import PDFService
            pdf_path = PDFService.generate_report_pdf(
                title=title,
                headers=headers,
                rows=rows,
                total_info=total_info,
                output_path=output_path
            )
            logger.info(f"Successfully exported PDF ledger to: {pdf_path}")
            return True, pdf_path
        except Exception as e:
            logger.error(f"PDF Ledger Export error: {e}", exc_info=True)
            return False, f"PDF Export error: {str(e)}"

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

