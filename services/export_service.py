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
