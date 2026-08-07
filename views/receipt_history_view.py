"""
Commercial ERP Receipt History & Search Ledger View with SQL Pagination, Multi-Filter Bar, 
Quick Date Presets, Bulk Actions, Export Engine, and Admin Security Audit Trail.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit,
    QMessageBox, QFileDialog, QCheckBox, QFrame, QMenu, QDialog, QFormLayout
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QCursor, QAction

from controllers.receipt_controller import ReceiptController
from controllers.report_controller import ReportController
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog
from dialogs.admin_auth_dialog import AdminAuthDialog
from services.export_service import ExportService
from services.pdf_service import PDFService
from services.security_service import SecurityService
from utils.helpers import format_currency, format_date
from utils.logger import logger


class DeleteReasonDialog(QDialog):
    """Modal dialog prompting for deletion reason for audit tracking."""
    def __init__(self, parent=None, title="Deletion Reason Required", context_text=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(400)
        self.reason = ""
        self.setup_ui(context_text)

    def setup_ui(self, context_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        lbl_info = QLabel(f"<b>{context_text}</b><br><span style='color: #64748b;'>Please state the reason for this deletion (required for audit records):</span>")
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)

        self.txt_reason = QLineEdit()
        self.txt_reason.setFixedHeight(34)
        self.txt_reason.setPlaceholderText("e.g. Duplicate entry, Wrong fee amount entered, Cancelled admission...")
        layout.addWidget(self.txt_reason)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedHeight(32)
        btn_cancel.clicked.connect(self.reject)

        btn_confirm = QPushButton("Confirm Deletion")
        btn_confirm.setFixedHeight(32)
        btn_confirm.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; padding: 0 14px;")
        btn_confirm.clicked.connect(self.on_confirm)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)
        layout.addLayout(btn_layout)

    def on_confirm(self):
        self.reason = self.txt_reason.text().strip()
        if not self.reason:
            QMessageBox.warning(self, "Reason Required", "Please enter a reason for cancelling/deleting this receipt.")
            return
        self.accept()


class ReceiptHistoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 1
        self.page_size = 25
        self.total_records = 0
        self.total_pages = 1
        self.selected_receipt_ids = set()

        self.setup_ui()
        self.load_receipts()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ---------------- 1. HEADER BANNER & ACTIONS ----------------
        hdr_layout = QHBoxLayout()
        title_lbl = QLabel("Receipt History & Search Ledger")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a;")
        hdr_layout.addWidget(title_lbl)
        hdr_layout.addStretch()

        self.btn_bulk_del = QPushButton("🗑️  Delete Selected")
        self.btn_bulk_del.setProperty("class", "SecondaryBtn")
        self.btn_bulk_del.setStyleSheet("background-color: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; font-weight: bold; padding: 6px 12px; border-radius: 6px;")
        self.btn_bulk_del.setCursor(Qt.PointingHandCursor)
        self.btn_bulk_del.clicked.connect(self.bulk_delete_selected)

        self.btn_export_menu = QPushButton("📥  Export Ledger ▾")
        self.btn_export_menu.setProperty("class", "SecondaryBtn")
        self.btn_export_menu.setStyleSheet("background-color: #f0f9ff; color: #0284c7; border: 1px solid #7dd3fc; font-weight: bold; padding: 6px 12px; border-radius: 6px;")
        self.btn_export_menu.setCursor(Qt.PointingHandCursor)
        self.btn_export_menu.clicked.connect(self.show_export_menu)

        self.btn_refresh = QPushButton("🔄  Refresh")
        self.btn_refresh.setProperty("class", "SecondaryBtn")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.load_receipts)

        hdr_layout.addWidget(self.btn_bulk_del)
        hdr_layout.addWidget(self.btn_export_menu)
        hdr_layout.addWidget(self.btn_refresh)
        main_layout.addLayout(hdr_layout)

        # ---------------- 2. KPI METRIC SUMMARY CARDS ----------------
        kpi_grid = QHBoxLayout()
        kpi_grid.setSpacing(12)

        self.card_today = self._create_kpi_card("TODAY'S COLLECTION", "₹ 0.00", "#059669")
        self.card_month = self._create_kpi_card("MONTHLY COLLECTION", "₹ 0.00", "#2563eb")
        self.card_receipts = self._create_kpi_card("RECEIPTS TODAY", "0", "#d97706")
        self.card_filtered = self._create_kpi_card("FILTERED LEDGER TOTAL", "₹ 0.00", "#7c3aed")

        kpi_grid.addWidget(self.card_today)
        kpi_grid.addWidget(self.card_month)
        kpi_grid.addWidget(self.card_receipts)
        kpi_grid.addWidget(self.card_filtered)
        main_layout.addLayout(kpi_grid)

        # ---------------- 3. ADVANCED SEARCH & FILTER TOOLBAR ----------------
        filter_box = QFrame()
        filter_box.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px;")
        filter_v = QVBoxLayout(filter_box)
        filter_v.setContentsMargins(8, 8, 8, 8)
        filter_v.setSpacing(8)

        # Row 1: Search box & Primary Dropdowns
        r1_layout = QHBoxLayout()
        r1_layout.setSpacing(8)

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(34)
        self.txt_search.setPlaceholderText("🔍 Live Search: Receipt No, Adm No, Student Name, Father, Mobile, Class, Mode...")
        self.txt_search.textChanged.connect(self.on_filter_changed)

        self.cmb_session = QComboBox()
        self.cmb_session.setFixedHeight(34)
        self.cmb_session.addItems(["Session: All", "2024-2025", "2025-2026", "2026-2027"])
        self.cmb_session.currentIndexChanged.connect(self.on_filter_changed)

        self.cmb_course = QComboBox()
        self.cmb_course.setFixedHeight(34)
        self.cmb_course.addItems(["Course: All", "UG", "PG", "Diploma", "School"])
        self.cmb_course.currentIndexChanged.connect(self.on_filter_changed)

        self.cmb_pay_mode = QComboBox()
        self.cmb_pay_mode.setFixedHeight(34)
        self.cmb_pay_mode.addItems(["Mode: All", "Cash", "UPI / QR", "Cheque", "Demand Draft (DD)", "Net Banking / NEFT", "Card"])
        self.cmb_pay_mode.currentIndexChanged.connect(self.on_filter_changed)

        self.cmb_status = QComboBox()
        self.cmb_status.setFixedHeight(34)
        self.cmb_status.addItems(["Status: All", "Paid", "Cancelled"])
        self.cmb_status.currentIndexChanged.connect(self.on_filter_changed)

        r1_layout.addWidget(self.txt_search, stretch=3)
        r1_layout.addWidget(self.cmb_session, stretch=1)
        r1_layout.addWidget(self.cmb_course, stretch=1)
        r1_layout.addWidget(self.cmb_pay_mode, stretch=1)
        r1_layout.addWidget(self.cmb_status, stretch=1)
        filter_v.addLayout(r1_layout)

        # Row 2: Date Pickers & Quick Filter Presets
        r2_layout = QHBoxLayout()
        r2_layout.setSpacing(6)

        lbl_from = QLabel("From:")
        lbl_from.setStyleSheet("font-weight: bold; color: #475569;")
        self.dt_from = QDateEdit()
        self.dt_from.setFixedHeight(32)
        self.dt_from.setCalendarPopup(True)
        self.dt_from.setDisplayFormat("dd-MM-yyyy")
        self.dt_from.setDate(QDate.currentDate().addDays(-90))
        self.dt_from.dateChanged.connect(self.on_filter_changed)

        lbl_to = QLabel("To:")
        lbl_to.setStyleSheet("font-weight: bold; color: #475569;")
        self.dt_to = QDateEdit()
        self.dt_to.setFixedHeight(32)
        self.dt_to.setCalendarPopup(True)
        self.dt_to.setDisplayFormat("dd-MM-yyyy")
        self.dt_to.setDate(QDate.currentDate())
        self.dt_to.dateChanged.connect(self.on_filter_changed)

        r2_layout.addWidget(lbl_from)
        r2_layout.addWidget(self.dt_from)
        r2_layout.addWidget(lbl_to)
        r2_layout.addWidget(self.dt_to)

        # Quick Date Preset Buttons
        btn_preset_today = QPushButton("Today")
        btn_preset_today.setFixedHeight(30)
        btn_preset_today.clicked.connect(lambda: self.apply_date_preset("today"))

        btn_preset_yesterday = QPushButton("Yesterday")
        btn_preset_yesterday.setFixedHeight(30)
        btn_preset_yesterday.clicked.connect(lambda: self.apply_date_preset("yesterday"))

        btn_preset_7d = QPushButton("Last 7 Days")
        btn_preset_7d.setFixedHeight(30)
        btn_preset_7d.clicked.connect(lambda: self.apply_date_preset("7days"))

        btn_preset_month = QPushButton("This Month")
        btn_preset_month.setFixedHeight(30)
        btn_preset_month.clicked.connect(lambda: self.apply_date_preset("month"))

        btn_preset_year = QPushButton("This Year")
        btn_preset_year.setFixedHeight(30)
        btn_preset_year.clicked.connect(lambda: self.apply_date_preset("year"))

        btn_preset_reset = QPushButton("↺ Reset Filters")
        btn_preset_reset.setFixedHeight(30)
        btn_preset_reset.setStyleSheet("background-color: #f1f5f9; color: #0f172a; font-weight: bold; border-radius: 4px;")
        btn_preset_reset.clicked.connect(self.reset_filters)

        r2_layout.addWidget(btn_preset_today)
        r2_layout.addWidget(btn_preset_yesterday)
        r2_layout.addWidget(btn_preset_7d)
        r2_layout.addWidget(btn_preset_month)
        r2_layout.addWidget(btn_preset_year)
        r2_layout.addWidget(btn_preset_reset)
        r2_layout.addStretch()

        filter_v.addLayout(r2_layout)
        main_layout.addWidget(filter_box)

        # ---------------- 4. PROFESSIONAL RECEIPT TABLE ----------------
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        
        # Header Checkbox setup
        self.chk_select_all = QCheckBox()
        self.chk_select_all.setToolTip("Select / Deselect All Page Receipts")
        self.chk_select_all.stateChanged.connect(self.on_select_all_changed)

        self.table.setHorizontalHeaderLabels([
            "", "Receipt No", "Date", "Adm No", "Student Name",
            "Course", "Class", "Payment Mode", "Amount (₹)", "Status", "Actions"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        header.setSectionResizeMode(10, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 125)
        self.table.setColumnWidth(2, 95)
        self.table.setColumnWidth(3, 105)
        self.table.setColumnWidth(5, 75)
        self.table.setColumnWidth(6, 95)
        self.table.setColumnWidth(7, 110)
        self.table.setColumnWidth(8, 115)
        self.table.setColumnWidth(9, 85)
        self.table.setColumnWidth(10, 210)

        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setAlternatingRowColors(True)

        main_layout.addWidget(self.table)

        # ---------------- 5. PAGINATION & SELECTION TOOLBAR ----------------
        page_layout = QHBoxLayout()
        page_layout.setSpacing(10)

        self.lbl_selection_count = QLabel("0 items selected")
        self.lbl_selection_count.setStyleSheet("font-weight: bold; color: #2563eb;")

        self.cmb_page_size = QComboBox()
        self.cmb_page_size.setFixedHeight(30)
        self.cmb_page_size.addItems(["25 per page", "50 per page", "100 per page", "200 per page"])
        self.cmb_page_size.currentIndexChanged.connect(self.on_page_size_changed)

        self.btn_first_page = QPushButton("⏮ First")
        self.btn_first_page.setFixedSize(65, 30)
        self.btn_first_page.clicked.connect(self.go_first_page)

        self.btn_prev_page = QPushButton("◀ Prev")
        self.btn_prev_page.setFixedSize(65, 30)
        self.btn_prev_page.clicked.connect(self.go_prev_page)

        self.lbl_page_info = QLabel("Page 1 of 1 (Total: 0 records)")
        self.lbl_page_info.setStyleSheet("font-weight: bold; color: #1e293b;")

        self.btn_next_page = QPushButton("Next ▶")
        self.btn_next_page.setFixedSize(65, 30)
        self.btn_next_page.clicked.connect(self.go_next_page)

        self.btn_last_page = QPushButton("Last ⏭")
        self.btn_last_page.setFixedSize(65, 30)
        self.btn_last_page.clicked.connect(self.go_last_page)

        page_layout.addWidget(self.lbl_selection_count)
        page_layout.addStretch()
        page_layout.addWidget(QLabel("Rows:"))
        page_layout.addWidget(self.cmb_page_size)
        page_layout.addWidget(self.btn_first_page)
        page_layout.addWidget(self.btn_prev_page)
        page_layout.addWidget(self.lbl_page_info)
        page_layout.addWidget(self.btn_next_page)
        page_layout.addWidget(self.btn_last_page)

        main_layout.addLayout(page_layout)

    def _create_kpi_card(self, title: str, initial_value: str, color: str) -> QWidget:
        card = QFrame()
        card.setProperty("class", "KPICard")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(14, 10, 14, 10)
        lbl_t = QLabel(title)
        lbl_t.setProperty("class", "KPITitle")
        lbl_v = QLabel(initial_value)
        lbl_v.setProperty("class", "KPIValue")
        lbl_v.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 800;")
        vbox.addWidget(lbl_t)
        vbox.addWidget(lbl_v)
        card.lbl_val = lbl_v
        return card

    def apply_date_preset(self, preset: str):
        today = QDate.currentDate()
        if preset == "today":
            self.dt_from.setDate(today)
            self.dt_to.setDate(today)
        elif preset == "yesterday":
            self.dt_from.setDate(today.addDays(-1))
            self.dt_to.setDate(today.addDays(-1))
        elif preset == "7days":
            self.dt_from.setDate(today.addDays(-7))
            self.dt_to.setDate(today)
        elif preset == "month":
            self.dt_from.setDate(QDate(today.year(), today.month(), 1))
            self.dt_to.setDate(today)
        elif preset == "year":
            self.dt_from.setDate(QDate(today.year(), 1, 1))
            self.dt_to.setDate(today)

    def reset_filters(self):
        self.txt_search.clear()
        self.cmb_session.setCurrentIndex(0)
        self.cmb_course.setCurrentIndex(0)
        self.cmb_pay_mode.setCurrentIndex(0)
        self.cmb_status.setCurrentIndex(0)
        self.dt_from.setDate(QDate.currentDate().addDays(-90))
        self.dt_to.setDate(QDate.currentDate())
        self.current_page = 1
        self.load_receipts()

    def on_filter_changed(self):
        self.current_page = 1
        self.load_receipts()

    def on_page_size_changed(self):
        size_str = self.cmb_page_size.currentText().split()[0]
        self.page_size = int(size_str)
        self.current_page = 1
        self.load_receipts()

    def go_first_page(self):
        if self.current_page > 1:
            self.current_page = 1
            self.load_receipts()

    def go_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_receipts()

    def go_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_receipts()

    def go_last_page(self):
        if self.current_page < self.total_pages:
            self.current_page = self.total_pages
            self.load_receipts()

    def load_receipts(self):
        # Update General KPI Summary Cards
        today_col = ReportController.get_today_collection()
        month_col = ReportController.get_monthly_collection()
        receipt_cnt = ReportController.get_receipts_today_count()

        self.card_today.lbl_val.setText(format_currency(today_col))
        self.card_month.lbl_val.setText(format_currency(month_col))
        self.card_receipts.lbl_val.setText(str(receipt_cnt))

        # Build Filter Options
        search = self.txt_search.text().strip()
        
        sess_txt = self.cmb_session.currentText()
        session_filter = sess_txt.replace("Session: ", "").strip()

        crs_txt = self.cmb_course.currentText()
        course_filter = crs_txt.replace("Course: ", "").strip()

        mode_txt = self.cmb_pay_mode.currentText()
        pay_mode_filter = mode_txt.replace("Mode: ", "").strip()

        stat_txt = self.cmb_status.currentText()
        status_filter = stat_txt.replace("Status: ", "").strip()

        qfrom = self.dt_from.date()
        qto = self.dt_to.date()
        date_from = date(qfrom.year(), qfrom.month(), qfrom.day())
        date_to = date(qto.year(), qto.month(), qto.day())

        # Execute High-Performance Paginated Query
        receipts, self.total_records, self.total_pages, summary = ReceiptController.get_receipts_paginated(
            search_query=search,
            date_from=date_from,
            date_to=date_to,
            session_filter=session_filter,
            course_filter=course_filter,
            class_filter="All",
            pay_mode_filter=pay_mode_filter,
            status_filter=status_filter,
            page=self.current_page,
            page_size=self.page_size
        )

        self.card_filtered.lbl_val.setText(format_currency(summary["total_amount"]))
        self.lbl_page_info.setText(f"Page {self.current_page} of {self.total_pages} (Total: {self.total_records} records)")

        # Enable/Disable Page Buttons
        self.btn_first_page.setEnabled(self.current_page > 1)
        self.btn_prev_page.setEnabled(self.current_page > 1)
        self.btn_next_page.setEnabled(self.current_page < self.total_pages)
        self.btn_last_page.setEnabled(self.current_page < self.total_pages)

        # Populate Table
        self.table.setRowCount(len(receipts))
        self.chk_select_all.setChecked(False)

        for row_idx, r in enumerate(receipts):
            # Column 0: Checkbox
            chk = QCheckBox()
            chk.setChecked(r.id in self.selected_receipt_ids)
            chk.stateChanged.connect(lambda state, rid=r.id: self.on_row_checkbox_changed(rid, state))
            chk_widget = QWidget()
            c_layout = QHBoxLayout(chk_widget)
            c_layout.addWidget(chk)
            c_layout.setAlignment(Qt.AlignCenter)
            c_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row_idx, 0, chk_widget)

            # Columns 1 to 9
            self.table.setItem(row_idx, 1, QTableWidgetItem(r.receipt_no))
            self.table.setItem(row_idx, 2, QTableWidgetItem(format_date(r.receipt_date)))
            self.table.setItem(row_idx, 3, QTableWidgetItem(r.student.admission_no if r.student else "N/A"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(r.student.name if r.student else "N/A"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(r.student.course if r.student else "N/A"))
            self.table.setItem(row_idx, 6, QTableWidgetItem(f"{r.student.class_name} ({r.student.section or 'A'})" if r.student else "N/A"))
            self.table.setItem(row_idx, 7, QTableWidgetItem(r.payment_mode))

            amt_item = QTableWidgetItem(format_currency(r.total_amount))
            amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 8, amt_item)

            stat_item = QTableWidgetItem(r.status)
            if r.status == "Paid":
                stat_item.setForeground(Qt.darkGreen)
            else:
                stat_item.setForeground(Qt.red)
            stat_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 9, stat_item)

            # Column 10: Action Buttons Widget
            act_widget = QWidget()
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(4)

            btn_view = QPushButton("👁 View")
            btn_view.setFixedHeight(26)
            btn_view.setStyleSheet("background-color: #1e3a8a; color: #ffffff; font-weight: bold; border-radius: 4px; font-size: 11px; padding: 0 6px;")
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.clicked.connect(lambda _, rec=r: self.view_receipt(rec))

            btn_print = QPushButton("🖨 Print")
            btn_print.setFixedHeight(26)
            btn_print.setStyleSheet("background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 4px; font-size: 11px; padding: 0 6px;")
            btn_print.setCursor(Qt.PointingHandCursor)
            btn_print.clicked.connect(lambda _, rec=r: self.print_receipt(rec))

            btn_pdf = QPushButton("📄 PDF")
            btn_pdf.setFixedHeight(26)
            btn_pdf.setStyleSheet("background-color: #059669; color: #ffffff; font-weight: bold; border-radius: 4px; font-size: 11px; padding: 0 6px;")
            btn_pdf.setCursor(Qt.PointingHandCursor)
            btn_pdf.clicked.connect(lambda _, rec=r: self.export_single_pdf(rec))

            btn_del = QPushButton("🚫 Del")
            btn_del.setFixedHeight(26)
            btn_del.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; border-radius: 4px; font-size: 11px; padding: 0 6px;")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, rec=r: self.cancel_receipt(rec))

            act_layout.addWidget(btn_view)
            act_layout.addWidget(btn_print)
            act_layout.addWidget(btn_pdf)
            act_layout.addWidget(btn_del)
            self.table.setCellWidget(row_idx, 10, act_widget)

        self.update_selection_counter()

    def on_row_checkbox_changed(self, rid: int, state: int):
        if state == Qt.Checked or state == 2:
            self.selected_receipt_ids.add(rid)
        else:
            self.selected_receipt_ids.discard(rid)
        self.update_selection_counter()

    def on_select_all_changed(self, state: int):
        is_checked = (state == Qt.Checked or state == 2)
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                chk = cell_widget.findChild(QCheckBox)
                if chk:
                    chk.setChecked(is_checked)

    def update_selection_counter(self):
        count = len(self.selected_receipt_ids)
        self.lbl_selection_count.setText(f"{count} items selected")
        self.btn_bulk_del.setEnabled(count > 0)

    # ---------------- RECEIPT ACTIONS ----------------
    def view_receipt(self, receipt):
        SecurityService.log_audit(
            action="View Receipt",
            module="Receipt History",
            details=f"Viewed receipt details '{receipt.receipt_no}'",
            status="Success"
        )
        dlg = ReceiptPreviewDialog(self, receipt)
        dlg.exec()

    def print_receipt(self, receipt):
        try:
            pdf_path = PDFService.generate_receipt_pdf(receipt)
            SecurityService.log_audit(
                action="Print Receipt",
                module="Receipt History",
                details=f"Generated print job for receipt '{receipt.receipt_no}'",
                status="Success"
            )
            import os
            os.startfile(pdf_path, "print")
        except Exception as e:
            QMessageBox.information(self, "Receipt PDF Generated", f"PDF receipt generated successfully at:\n{pdf_path}")

    def export_single_pdf(self, receipt):
        try:
            pdf_path = PDFService.generate_receipt_pdf(receipt)
            SecurityService.log_audit(
                action="Export PDF Receipt",
                module="Receipt History",
                details=f"Exported PDF receipt '{receipt.receipt_no}' to '{pdf_path}'",
                status="Success"
            )
            QMessageBox.information(self, "PDF Exported", f"Receipt PDF saved successfully:\n{pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "PDF Error", f"Could not export PDF: {str(e)}")

    def cancel_receipt(self, receipt):
        auth_dlg = AdminAuthDialog(
            self,
            action_title="Administrator Password Required",
            action_context=f"Delete / Cancel Receipt: '{receipt.receipt_no}'",
            module="Receipt History"
        )
        if not auth_dlg.exec():
            return

        reason_dlg = DeleteReasonDialog(self, context_text=f"Deleting Receipt '{receipt.receipt_no}'")
        if not reason_dlg.exec():
            return

        reply = QMessageBox.question(
            self, "Confirm Delete Receipt",
            f"Are you sure you want to cancel/delete receipt '{receipt.receipt_no}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = ReceiptController.cancel_receipt(receipt.id, reason=reason_dlg.reason)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_receipts()
            else:
                QMessageBox.critical(self, "Error", msg)

    def bulk_delete_selected(self):
        if not self.selected_receipt_ids:
            QMessageBox.warning(self, "No Selection", "Please select at least one receipt to delete.")
            return

        auth_dlg = AdminAuthDialog(
            self,
            action_title="Administrator Bulk Delete Protection",
            action_context=f"Bulk Delete {len(self.selected_receipt_ids)} Selected Receipts",
            module="Receipt History"
        )
        if not auth_dlg.exec():
            return

        reason_dlg = DeleteReasonDialog(self, context_text=f"Bulk Deleting {len(self.selected_receipt_ids)} Selected Receipts")
        if not reason_dlg.exec():
            return

        reply = QMessageBox.question(
            self, "Confirm Bulk Deletion",
            f"Are you sure you want to permanently delete {len(self.selected_receipt_ids)} selected receipts?\nThis operation is logged and cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg, count = ReceiptController.bulk_delete_receipts(list(self.selected_receipt_ids), reason=reason_dlg.reason)
            if success:
                QMessageBox.information(self, "Bulk Delete Result", msg)
                self.selected_receipt_ids.clear()
                self.load_receipts()
            else:
                QMessageBox.critical(self, "Bulk Delete Error", msg)

    # ---------------- EXPORT MENU ----------------
    def show_export_menu(self):
        menu = QMenu(self)
        
        act_csv_page = QAction("📄 Export Current Page (CSV)", self)
        act_csv_page.triggered.connect(lambda: self.export_ledger("csv", scope="page"))

        act_excel_page = QAction("📊 Export Current Page (Excel .xlsx)", self)
        act_excel_page.triggered.connect(lambda: self.export_ledger("excel", scope="page"))

        act_pdf_page = QAction("📜 Export Current Page (PDF Report)", self)
        act_pdf_page.triggered.connect(lambda: self.export_ledger("pdf", scope="page"))

        menu.addSeparator()

        act_csv_sel = QAction("📄 Export Selected Rows (CSV)", self)
        act_csv_sel.setEnabled(len(self.selected_receipt_ids) > 0)
        act_csv_sel.triggered.connect(lambda: self.export_ledger("csv", scope="selected"))

        act_excel_sel = QAction("📊 Export Selected Rows (Excel)", self)
        act_excel_sel.setEnabled(len(self.selected_receipt_ids) > 0)
        act_excel_sel.triggered.connect(lambda: self.export_ledger("excel", scope="selected"))

        menu.addSeparator()

        act_csv_all = QAction("🌐 Export Entire Filtered Ledger (CSV)", self)
        act_csv_all.triggered.connect(lambda: self.export_ledger("csv", scope="all"))

        act_excel_all = QAction("🌐 Export Entire Filtered Ledger (Excel)", self)
        act_excel_all.triggered.connect(lambda: self.export_ledger("excel", scope="all"))

        act_pdf_all = QAction("🌐 Export Entire Filtered Ledger (PDF Report)", self)
        act_pdf_all.triggered.connect(lambda: self.export_ledger("pdf", scope="all"))

        menu.addAction(act_csv_page)
        menu.addAction(act_excel_page)
        menu.addAction(act_pdf_page)
        menu.addSeparator()
        menu.addAction(act_csv_sel)
        menu.addAction(act_excel_sel)
        menu.addSeparator()
        menu.addAction(act_csv_all)
        menu.addAction(act_excel_all)
        menu.addAction(act_pdf_all)

        menu.exec(QCursor.pos())

    def export_ledger(self, fmt: str, scope: str = "page"):
        headers = ["Receipt No", "Date", "Admission No", "Student Name", "Course", "Class", "Payment Mode", "Subtotal (Rs.)", "Discount (Rs.)", "Fine (Rs.)", "Total Amount (Rs.)", "Status"]

        search = self.txt_search.text().strip()
        sess_txt = self.cmb_session.currentText().replace("Session: ", "").strip()
        crs_txt = self.cmb_course.currentText().replace("Course: ", "").strip()
        mode_txt = self.cmb_pay_mode.currentText().replace("Mode: ", "").strip()
        stat_txt = self.cmb_status.currentText().replace("Status: ", "").strip()

        qfrom = self.dt_from.date()
        qto = self.dt_to.date()
        date_from = date(qfrom.year(), qfrom.month(), qfrom.day())
        date_to = date(qto.year(), qto.month(), qto.day())

        if scope == "selected":
            all_recs = ReceiptController.get_all_receipts(search_query="", date_from=None, date_to=None)
            target_receipts = [r for r in all_recs if r.id in self.selected_receipt_ids]
        elif scope == "all":
            target_receipts = ReceiptController.get_all_receipts(
                search_query=search, date_from=date_from, date_to=date_to,
                session_filter=sess_txt, course_filter=crs_txt,
                pay_mode_filter=mode_txt, status_filter=stat_txt
            )
        else: # page
            target_receipts, _, _, _ = ReceiptController.get_receipts_paginated(
                search_query=search, date_from=date_from, date_to=date_to,
                session_filter=sess_txt, course_filter=crs_txt,
                pay_mode_filter=mode_txt, status_filter=stat_txt,
                page=self.current_page, page_size=self.page_size
            )

        rows = []
        for r in target_receipts:
            rows.append([
                r.receipt_no,
                format_date(r.receipt_date),
                r.student.admission_no if r.student else "N/A",
                r.student.name if r.student else "N/A",
                r.student.course if r.student else "N/A",
                f"{r.student.class_name} ({r.student.section or 'A'})" if r.student else "N/A",
                r.payment_mode,
                f"{r.subtotal:.2f}",
                f"{r.discount_amount:.2f}",
                f"{r.fine_amount:.2f}",
                f"{r.total_amount:.2f}",
                r.status
            ])

        filter_ext = "*.csv" if fmt == "csv" else ("*.xlsx" if fmt == "excel" else "*.pdf")
        default_name = f"Receipt_Ledger_{scope}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" + filter_ext[1:]
        path, _ = QFileDialog.getSaveFileName(self, f"Export Receipt Ledger ({fmt.upper()})", default_name, f"{fmt.upper()} Files ({filter_ext})")
        if not path:
            return

        if fmt == "csv":
            success, out_file = ExportService.export_to_csv(headers, rows, output_path=path)
        elif fmt == "excel":
            success, out_file = ExportService.export_to_excel(headers, rows, output_path=path)
        else: # pdf
            tot_amt = sum(r.total_amount for r in target_receipts)
            tot_info = {"Total Amount (Rs.)": f"Rs. {tot_amt:.2f}"}
            success, out_file = ExportService.export_to_pdf_ledger("Receipt History Ledger Report", headers, rows, total_info=tot_info, output_path=path)

        if success:
            SecurityService.log_audit(
                action=f"Export Ledger ({fmt.upper()})",
                module="Receipt History",
                details=f"Exported {len(target_receipts)} receipts to '{out_file}' (Scope: {scope})",
                status="Success"
            )
            QMessageBox.information(self, "Export Successful", f"Successfully exported {len(target_receipts)} records to:\n{out_file}")
        else:
            QMessageBox.critical(self, "Export Failed", f"Export error: {out_file}")
