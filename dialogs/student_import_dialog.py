"""
Interactive Bulk Student Import & Data Validation Wizard Dialog for EduLedger ERP v1.9.0.
Features CSV/Excel file selection, sample template downloads, pre-import validation preview,
duplicate detection, row skipping, import summary, and downloadable CSV error reports.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QStackedWidget,
    QGroupBox, QCheckBox, QComboBox, QFrame
)
from PySide6.QtCore import Qt

from services.import_service import ImportService
from utils.logger import logger


class StudentImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Student Import & Validation Wizard")
        self.resize(1000, 680)

        self.file_path = ""
        self.raw_rows = []
        self.validation_result = {}
        self.parsed_items = []

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Wizard Step Header
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #1e3a8a; border-radius: 6px; padding: 10px 14px;")
        hdr_layout = QHBoxLayout(hdr_frame)
        
        self.lbl_wizard_title = QLabel("Bulk Student Import Wizard")
        self.lbl_wizard_title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        
        self.lbl_step_indicator = QLabel("Step 1 of 3: Select File")
        self.lbl_step_indicator.setStyleSheet("color: #93c5fd; font-size: 12px; font-weight: 600;")

        hdr_layout.addWidget(self.lbl_wizard_title)
        hdr_layout.addStretch()
        hdr_layout.addWidget(self.lbl_step_indicator)
        main_layout.addWidget(hdr_frame)

        # Stacked Pages
        self.stack = QStackedWidget()

        # Step 1: File Selection
        self.page_select = QWidget()
        self.setup_step1_select()
        self.stack.addWidget(self.page_select)

        # Step 2: Validation Preview
        self.page_preview = QWidget()
        self.setup_step2_preview()
        self.stack.addWidget(self.page_preview)

        # Step 3: Summary
        self.page_summary = QWidget()
        self.setup_step3_summary()
        self.stack.addWidget(self.page_summary)

        main_layout.addWidget(self.stack)

    # ---------------- STEP 1: FILE SELECTION ----------------
    def setup_step1_select(self):
        layout = QVBoxLayout(self.page_select)
        layout.setSpacing(16)

        # File Drop Zone Frame
        drop_box = QGroupBox("Select Import File (CSV or Excel .xlsx)")
        drop_box.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        v_drop = QVBoxLayout(drop_box)
        v_drop.setContentsMargins(20, 24, 20, 24)
        v_drop.setSpacing(12)

        lbl_icon = QLabel("📁")
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 48px;")

        self.lbl_file_status = QLabel("Click 'Browse File' to select a CSV or Excel (.xlsx) student database file.")
        self.lbl_file_status.setAlignment(Qt.AlignCenter)
        self.lbl_file_status.setStyleSheet("font-size: 13px; color: #475569; font-weight: 600;")

        self.btn_browse = QPushButton("🔍  Browse CSV / Excel File")
        self.btn_browse.setFixedHeight(38)
        self.btn_browse.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; border-radius: 6px; padding: 0 20px;")
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self.browse_file)

        v_drop.addWidget(lbl_icon)
        v_drop.addWidget(self.lbl_file_status)
        v_drop.addWidget(self.btn_browse, alignment=Qt.AlignCenter)

        layout.addWidget(drop_box)

        # Sample Templates Box
        tmpl_box = QGroupBox("Download Official Import Templates")
        tmpl_layout = QHBoxLayout(tmpl_box)
        tmpl_layout.setContentsMargins(14, 14, 14, 14)

        lbl_tmpl_info = QLabel("Download a pre-formatted template with sample records and correct field column headers:")
        lbl_tmpl_info.setStyleSheet("font-size: 12px; color: #334155;")

        self.btn_sample_csv = QPushButton("📥  Sample CSV Template")
        self.btn_sample_csv.setFixedHeight(34)
        self.btn_sample_csv.setProperty("class", "SecondaryBtn")
        self.btn_sample_csv.clicked.connect(self.download_sample_csv)

        self.btn_sample_excel = QPushButton("📊  Sample Excel Template")
        self.btn_sample_excel.setFixedHeight(34)
        self.btn_sample_excel.setProperty("class", "SecondaryBtn")
        self.btn_sample_excel.clicked.connect(self.download_sample_excel)

        tmpl_layout.addWidget(lbl_tmpl_info, stretch=1)
        tmpl_layout.addWidget(self.btn_sample_csv)
        tmpl_layout.addWidget(self.btn_sample_excel)

        layout.addWidget(tmpl_box)
        layout.addStretch()

        # Step 1 Footer
        foot_layout = QHBoxLayout()
        foot_layout.addStretch()
        
        self.btn_next_step1 = QPushButton("Validate & Preview Rows →")
        self.btn_next_step1.setFixedHeight(36)
        self.btn_next_step1.setEnabled(False)
        self.btn_next_step1.setStyleSheet("background-color: #059669; color: white; font-weight: bold; border-radius: 5px; padding: 0 16px;")
        self.btn_next_step1.clicked.connect(self.run_file_validation)

        foot_layout.addWidget(self.btn_next_step1)
        layout.addLayout(foot_layout)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Student Import File", "", "Supported Files (*.csv *.xlsx *.xls);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        if path:
            self.file_path = path
            self.lbl_file_status.setText(f"Selected File: <b>{Path(path).name}</b>")
            self.btn_next_step1.setEnabled(True)

    def download_sample_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Sample CSV Template", "sample_student_import.csv", "CSV Files (*.csv)")
        if path:
            success, msg = ImportService.generate_sample_csv(path)
            if success:
                QMessageBox.information(self, "Template Saved", f"Sample CSV template saved to:\n{path}")
            else:
                QMessageBox.critical(self, "Error", msg)

    def download_sample_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Sample Excel Template", "sample_student_import.xlsx", "Excel Files (*.xlsx)")
        if path:
            success, msg = ImportService.generate_sample_excel(path)
            if success:
                QMessageBox.information(self, "Template Saved", f"Sample Excel template saved to:\n{path}")
            else:
                QMessageBox.critical(self, "Error", msg)

    # ---------------- STEP 2: PREVIEW & VALIDATION ----------------
    def setup_step2_preview(self):
        layout = QVBoxLayout(self.page_preview)
        layout.setSpacing(10)

        # Summary Bar
        sum_bar = QHBoxLayout()
        
        self.lbl_total_count = QLabel("Total: <b>0</b>")
        self.lbl_valid_count = QLabel("Valid: <b style='color: #16a34a;'>0</b>")
        self.lbl_duplicate_count = QLabel("Duplicates: <b style='color: #d97706;'>0</b>")
        self.lbl_invalid_count = QLabel("Invalid: <b style='color: #dc2626;'>0</b>")

        for lbl in [self.lbl_total_count, self.lbl_valid_count, self.lbl_duplicate_count, self.lbl_invalid_count]:
            lbl.setStyleSheet("background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 5px; padding: 6px 12px; font-size: 12px;")
            sum_bar.addWidget(lbl)

        sum_bar.addStretch()

        sum_bar.addWidget(QLabel("Show:"))
        self.cmb_filter_status = QComboBox()
        self.cmb_filter_status.addItems(["All Rows", "Only Valid", "Only Duplicates", "Only Invalid"])
        self.cmb_filter_status.currentTextChanged.connect(self.filter_preview_table)
        sum_bar.addWidget(self.cmb_filter_status)

        layout.addLayout(sum_bar)

        # Preview Table
        self.table_preview = QTableWidget()
        self.table_preview.setColumnCount(10)
        self.table_preview.setHorizontalHeaderLabels([
            "Import?", "Row #", "Status", "Admission No", "Student Name", "Class / Sec", "Course", "Father Name", "Mobile", "Validation Issues"
        ])
        self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_preview.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table_preview.horizontalHeader().setSectionResizeMode(9, QHeaderView.Stretch)
        self.table_preview.setAlternatingRowColors(True)

        layout.addWidget(self.table_preview)

        # Step 2 Footer
        foot_layout = QHBoxLayout()

        self.btn_back_step2 = QPushButton("⬅ Back to Select File")
        self.btn_back_step2.setProperty("class", "SecondaryBtn")
        self.btn_back_step2.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.btn_export_errors = QPushButton("📥  Download Error Log CSV")
        self.btn_export_errors.setProperty("class", "SecondaryBtn")
        self.btn_export_errors.clicked.connect(self.download_error_log)

        self.btn_commit_import = QPushButton("🚀  Import Valid Students")
        self.btn_commit_import.setStyleSheet("background-color: #059669; color: white; font-weight: bold; border-radius: 5px; padding: 6px 16px;")
        self.btn_commit_import.clicked.connect(self.execute_import)

        foot_layout.addWidget(self.btn_back_step2)
        foot_layout.addWidget(self.btn_export_errors)
        foot_layout.addStretch()
        foot_layout.addWidget(self.btn_commit_import)

        layout.addLayout(foot_layout)

    def run_file_validation(self):
        if not self.file_path:
            return

        success, headers, raw_rows, msg = ImportService.read_students_file(self.file_path)
        if not success:
            QMessageBox.critical(self, "File Read Error", msg)
            return

        self.raw_rows = raw_rows
        self.validation_result = ImportService.validate_and_parse_students(raw_rows)
        self.parsed_items = self.validation_result["items"]

        # Update Summary Labels
        self.lbl_total_count.setText(f"Total Rows: <b>{self.validation_result['total_rows']}</b>")
        self.lbl_valid_count.setText(f"Valid: <b style='color: #16a34a;'>{self.validation_result['valid_count']}</b>")
        self.lbl_duplicate_count.setText(f"Duplicates: <b style='color: #d97706;'>{self.validation_result['duplicate_count']}</b>")
        self.lbl_invalid_count.setText(f"Invalid: <b style='color: #dc2626;'>{self.validation_result['invalid_count']}</b>")

        self.filter_preview_table()
        self.lbl_step_indicator.setText("Step 2 of 3: Validate & Preview Rows")
        self.stack.setCurrentIndex(1)

    def filter_preview_table(self):
        status_filter = self.cmb_filter_status.currentText()
        filtered = self.parsed_items
        if status_filter == "Only Valid":
            filtered = [i for i in self.parsed_items if i["validation_status"] == "Valid"]
        elif status_filter == "Only Duplicates":
            filtered = [i for i in self.parsed_items if i["validation_status"] == "Duplicate"]
        elif status_filter == "Only Invalid":
            filtered = [i for i in self.parsed_items if i["validation_status"] == "Invalid"]

        self.table_preview.setRowCount(len(filtered))

        for idx, item in enumerate(filtered):
            # Checkbox
            chk = QCheckBox()
            chk.setChecked(item["is_importable"])
            chk.setEnabled(item["validation_status"] == "Valid")
            chk.toggled.connect(lambda checked, it=item: it.update({"is_importable": checked}))
            self.table_preview.setCellWidget(idx, 0, chk)

            self.table_preview.setItem(idx, 1, QTableWidgetItem(str(item["row_num"])))
            
            # Status Item
            status_item = QTableWidgetItem(item["validation_status"])
            if item["validation_status"] == "Valid":
                status_item.setForeground(Qt.darkGreen)
            elif item["validation_status"] == "Duplicate":
                status_item.setForeground(Qt.darkYellow)
            else:
                status_item.setForeground(Qt.red)
            self.table_preview.setItem(idx, 2, status_item)

            self.table_preview.setItem(idx, 3, QTableWidgetItem(item["admission_no"]))
            self.table_preview.setItem(idx, 4, QTableWidgetItem(item["name"]))
            self.table_preview.setItem(idx, 5, QTableWidgetItem(f"{item['class_name']} ({item['section']})"))
            self.table_preview.setItem(idx, 6, QTableWidgetItem(item["course"]))
            self.table_preview.setItem(idx, 7, QTableWidgetItem(item["father_name"]))
            self.table_preview.setItem(idx, 8, QTableWidgetItem(item["mobile"]))
            self.table_preview.setItem(idx, 9, QTableWidgetItem(item["issues"]))

    def download_error_log(self):
        errors = self.validation_result.get("errors_report", [])
        if not errors:
            QMessageBox.information(self, "No Errors", "There are no validation errors or skipped rows to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Import Error Log", "import_error_log.csv", "CSV Files (*.csv)")
        if path:
            success, msg = ImportService.export_error_report(errors, path)
            if success:
                QMessageBox.information(self, "Saved", f"Import error report saved to:\n{msg}")
            else:
                QMessageBox.critical(self, "Error", msg)

    # ---------------- STEP 3: EXECUTION & SUMMARY ----------------
    def setup_step3_summary(self):
        layout = QVBoxLayout(self.page_summary)
        layout.setSpacing(16)

        sum_box = QGroupBox("Import Execution Final Summary")
        v_sum = QVBoxLayout(sum_box)
        v_sum.setContentsMargins(20, 20, 20, 20)
        v_sum.setSpacing(12)

        self.lbl_summary_icon = QLabel("🎉")
        self.lbl_summary_icon.setAlignment(Qt.AlignCenter)
        self.lbl_summary_icon.setStyleSheet("font-size: 48px;")

        self.lbl_summary_details = QLabel("Import process completed.")
        self.lbl_summary_details.setAlignment(Qt.AlignCenter)
        self.lbl_summary_details.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e3a8a;")

        v_sum.addWidget(self.lbl_summary_icon)
        v_sum.addWidget(self.lbl_summary_details)

        layout.addWidget(sum_box)
        layout.addStretch()

        foot_layout = QHBoxLayout()
        foot_layout.addStretch()

        self.btn_done = QPushButton("Done / Close")
        self.btn_done.setFixedHeight(36)
        self.btn_done.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; border-radius: 5px; padding: 0 20px;")
        self.btn_done.clicked.connect(self.accept)

        foot_layout.addWidget(self.btn_done)
        layout.addLayout(foot_layout)

    def execute_import(self):
        importable_items = [i for i in self.parsed_items if i.get("is_importable")]
        if not importable_items:
            QMessageBox.warning(self, "No Valid Rows", "There are no valid student rows selected for import.")
            return

        reply = QMessageBox.question(
            self, "Confirm Bulk Import",
            f"Are you sure you want to import {len(importable_items)} valid student records into EduLedger ERP?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        success, count, msg = ImportService.commit_imported_students(importable_items)
        if success:
            skipped_cnt = len(self.parsed_items) - count
            self.lbl_summary_details.setText(
                f"<b>{count} Students Successfully Imported into Database!</b><br><br>"
                f"<span style='color: #475569;'>Total Rows Processed: {len(self.parsed_items)}<br>"
                f"Skipped / Failed Rows: {skipped_cnt}</span>"
            )
            self.lbl_step_indicator.setText("Step 3 of 3: Import Complete")
            self.stack.setCurrentIndex(2)
        else:
            QMessageBox.critical(self, "Import Execution Failed", msg)
