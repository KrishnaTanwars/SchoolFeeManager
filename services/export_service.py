"""
Multi-Format Export Service for EduLedger ERP v1.9.0.
Exports data records to CSV, Excel (.xlsx), and ReportLab PDF documents.
"""

import csv
from typing import List, Optional, Tuple, Dict, Any
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
    ) -> Tuple[bool, str]:
        """Exports data rows to CSV file format."""
        try:
            if not output_path:
                filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                output_path = str(EXPORTS_DIR / filename)

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
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
        filename_prefix: str = "Export_Spreadsheet",
        output_path: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Exports data rows to Excel-compatible format (.xlsx)."""
        try:
            if not output_path:
                filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                output_path = str(EXPORTS_DIR / filename)

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            try:
                import openpyxl
                from openpyxl.styles import Font
                from config.app_config import STUDENT_PHOTOS_DIR

                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "EduLedger Data Export"
                ws.append(headers)

                # Identify photo column index if present
                photo_col_idx = -1
                for idx, h in enumerate(headers):
                    if h.lower() in ("student photo", "photo link", "photo path", "photo"):
                        photo_col_idx = idx
                        break

                font_hyperlink = Font(color="0000FF", underline="single")

                for row_data in rows:
                    row_cells = [str(c) if c is not None else "" for c in row_data]
                    ws.append(row_cells)
                    curr_row_idx = ws.max_row

                    if photo_col_idx >= 0 and photo_col_idx < len(row_data):
                        raw_photo = str(row_data[photo_col_idx]).strip() if row_data[photo_col_idx] else ""
                        cell = ws.cell(row=curr_row_idx, column=photo_col_idx + 1)
                        
                        if raw_photo and raw_photo.lower() not in ("none", "null", "no photo", "-", "n/a"):
                            # Robust path resolution across project structures
                            photo_file = None
                            candidates = [
                                STUDENT_PHOTOS_DIR / raw_photo,
                                STUDENT_PHOTOS_DIR / Path(raw_photo).name,
                                Path(raw_photo),
                                Path(__file__).resolve().parent.parent / raw_photo,
                                Path(__file__).resolve().parent.parent / "student_photos" / Path(raw_photo).name
                            ]
                            for cand in candidates:
                                if cand.exists():
                                    photo_file = cand.resolve()
                                    break
                            
                            if not photo_file:
                                # Default to resolved URI target under STUDENT_PHOTOS_DIR
                                photo_file = (STUDENT_PHOTOS_DIR / Path(raw_photo).name).resolve()

                            file_uri = photo_file.as_uri()
                            cell.value = f"View Photo ({Path(raw_photo).name})"
                            cell.hyperlink = file_uri
                            cell.font = font_hyperlink
                        else:
                            cell.value = "No Photo"

                wb.save(output_path)
            except ImportError:
                # Fallback to UTF-8-SIG TSV format which Excel opens directly
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
        total_info: Optional[Dict[str, str]] = None,
        output_path: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Exports tabular data rows to ReportLab PDF report."""
        try:
            from services.pdf_service import PDFService
            pdf_path = PDFService.generate_report_pdf(
                title=title,
                headers=headers,
                rows=rows,
                total_info=total_info,
                output_path=output_path
            )
            logger.info(f"Successfully exported PDF to: {pdf_path}")
            return True, pdf_path
        except Exception as e:
            logger.error(f"PDF Export error: {e}", exc_info=True)
            return False, f"PDF Export error: {str(e)}"

    @staticmethod
    def export_data_by_format(
        title: str,
        headers: List[str],
        rows: List[List[str]],
        fmt: str,
        filename_prefix: str = "Export",
        output_path: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Unified exporter supporting csv, excel, pdf formats."""
        fmt_lower = fmt.lower()
        if fmt_lower == "csv":
            return ExportService.export_to_csv(headers, rows, filename_prefix, output_path)
        elif fmt_lower in ("excel", "xlsx"):
            return ExportService.export_to_excel(headers, rows, filename_prefix, output_path)
        elif fmt_lower == "pdf":
            return ExportService.export_to_pdf_ledger(title, headers, rows, output_path=output_path)
        else:
            return False, f"Unsupported format: {fmt}"

    @staticmethod
    def generate_sample_student_csv(output_path: Optional[str] = None) -> Tuple[bool, str]:
        """Generates a sample CSV template pre-filled with correct columns and example rows."""
        from services.import_service import ImportService
        return ImportService.generate_sample_csv(output_path=output_path)
