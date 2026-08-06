"""
Receipt History Ledger View with Zero-Clipping Action Buttons.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from datetime import date
from controllers.receipt_controller import ReceiptController
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog
from services.export_service import ExportService
from utils.helpers import format_currency, format_date

class ReceiptHistoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title Banner
        hdr_layout = QHBoxLayout()
        title_lbl = QLabel("Receipt History & Search Ledger")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a;")
        hdr_layout.addWidget(title_lbl)
        hdr_layout.addStretch()

        self.btn_bulk_del = QPushButton("🗑️  Bulk Clear Cancelled")
        self.btn_bulk_del.setProperty("class", "SecondaryBtn")
        self.btn_bulk_del.setCursor(Qt.PointingHandCursor)
        self.btn_bulk_del.clicked.connect(self.bulk_delete_receipts)

        self.btn_export = QPushButton("📥  Export CSV")
        self.btn_export.setProperty("class", "SecondaryBtn")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_csv)

        hdr_layout.addWidget(self.btn_bulk_del)
        hdr_layout.addWidget(self.btn_export)
        layout.addLayout(hdr_layout)

        # KPI Summary Cards Banner
        from PySide6.QtWidgets import QFrame, QGridLayout
        from controllers.report_controller import ReportController

        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(12)

        self.card_today = self._create_kpi_card("TODAY'S COLLECTION", "₹ 0.00", "#059669")
        self.card_month = self._create_kpi_card("MONTHLY COLLECTION", "₹ 0.00", "#2563eb")
        self.card_receipts = self._create_kpi_card("RECEIPTS ISSUED TODAY", "0", "#d97706")

        kpi_grid.addWidget(self.card_today, 0, 0)
        kpi_grid.addWidget(self.card_month, 0, 1)
        kpi_grid.addWidget(self.card_receipts, 0, 2)

        layout.addLayout(kpi_grid)

        # Filter & Search Bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(36)
        self.txt_search.setPlaceholderText("🔍 Search Receipt No, Student Name, Adm No, Mobile...")
        self.txt_search.textChanged.connect(self.load_receipts)

        self.dt_from = QDateEdit()
        self.dt_from.setFixedHeight(36)
        self.dt_from.setMinimumWidth(130)
        self.dt_from.setCalendarPopup(True)
        self.dt_from.setDisplayFormat("dd-MM-yyyy")
        self.dt_from.setDate(QDate.currentDate().addDays(-30))
        self.dt_from.dateChanged.connect(self.load_receipts)

        self.dt_to = QDateEdit()
        self.dt_to.setFixedHeight(36)
        self.dt_to.setMinimumWidth(130)
        self.dt_to.setCalendarPopup(True)
        self.dt_to.setDisplayFormat("dd-MM-yyyy")
        self.dt_to.setDate(QDate.currentDate())
        self.dt_to.dateChanged.connect(self.load_receipts)

        filter_layout.addWidget(self.txt_search, stretch=3)
        filter_layout.addWidget(QLabel("From:"), stretch=0)
        filter_layout.addWidget(self.dt_from, stretch=1)
        filter_layout.addWidget(QLabel("To:"), stretch=0)
        filter_layout.addWidget(self.dt_to, stretch=1)

        layout.addLayout(filter_layout)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Receipt No", "Date", "Student Name", "Adm No", "Class",
            "Payment Mode", "Total Amount", "Status", "Actions"
        ])
        
        # Explicit section resize modes: data columns stretch, Actions column fixed to 220px
        header = self.table.horizontalHeader()
        for col in range(8):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 220)

        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)
        self.load_receipts()

    def _create_kpi_card(self, title: str, initial_value: str, color: str) -> QWidget:
        from PySide6.QtWidgets import QFrame
        card = QFrame()
        card.setProperty("class", "KPICard")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(16, 12, 16, 12)
        lbl_t = QLabel(title)
        lbl_t.setProperty("class", "KPITitle")
        lbl_v = QLabel(initial_value)
        lbl_v.setProperty("class", "KPIValue")
        lbl_v.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 800;")
        vbox.addWidget(lbl_t)
        vbox.addWidget(lbl_v)
        card.lbl_val = lbl_v
        return card

    def load_receipts(self):
        from controllers.report_controller import ReportController
        today_col = ReportController.get_today_collection()
        month_col = ReportController.get_monthly_collection()
        receipt_cnt = ReportController.get_receipts_today_count()

        self.card_today.lbl_val.setText(format_currency(today_col))
        self.card_month.lbl_val.setText(format_currency(month_col))
        self.card_receipts.lbl_val.setText(str(receipt_cnt))

        search = self.txt_search.text().strip()
        qfrom = self.dt_from.date()
        qto = self.dt_to.date()

        date_from = date(qfrom.year(), qfrom.month(), qfrom.day())
        date_to = date(qto.year(), qto.month(), qto.day())

        receipts = ReceiptController.get_all_receipts(
            search_query=search if search else None,
            date_from=date_from,
            date_to=date_to
        )

        self.table.setRowCount(len(receipts))

        for row_idx, r in enumerate(receipts):
            self.table.setItem(row_idx, 0, QTableWidgetItem(r.receipt_no))
            self.table.setItem(row_idx, 1, QTableWidgetItem(format_date(r.receipt_date)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(r.student.name if r.student else "N/A"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(r.student.admission_no if r.student else "N/A"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{r.student.class_name} ({r.student.section or 'A'})" if r.student else "N/A"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(r.payment_mode))
            self.table.setItem(row_idx, 6, QTableWidgetItem(format_currency(r.total_amount)))
            self.table.setItem(row_idx, 7, QTableWidgetItem(r.status))

            # Actions container with zero-clipping inline padding
            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(6)

            btn_view = QPushButton("👁 View")
            btn_view.setFixedHeight(28)
            btn_view.setMinimumWidth(80)
            btn_view.setStyleSheet("background-color: #1e3a8a; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; padding: 0px 6px;")
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.clicked.connect(lambda _, rec=r: self.view_receipt(rec))

            btn_del = QPushButton("🚫 Cancel")
            btn_del.setFixedHeight(28)
            btn_del.setMinimumWidth(80)
            btn_del.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; padding: 0px 6px;")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, rec=r: self.cancel_receipt(rec))

            act_layout.addWidget(btn_view)
            act_layout.addWidget(btn_del)
            self.table.setCellWidget(row_idx, 8, action_widget)

    def view_receipt(self, receipt):
        dlg = ReceiptPreviewDialog(self, receipt)
        dlg.exec()

    def cancel_receipt(self, receipt):
        from dialogs.admin_auth_dialog import AdminAuthDialog
        auth_dlg = AdminAuthDialog(
            self,
            action_title="Receipt Delete Protection",
            action_context=f"Cancel/Delete Receipt: '{receipt.receipt_no}'",
            module="Receipt History"
        )
        if not auth_dlg.exec():
            return

        reply = QMessageBox.question(
            self, "Confirm Delete Receipt",
            f"Are you sure you want to cancel/delete receipt '{receipt.receipt_no}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = ReceiptController.cancel_receipt(receipt.id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_receipts()
            else:
                QMessageBox.critical(self, "Error", msg)

    def bulk_delete_receipts(self):
        from dialogs.admin_auth_dialog import AdminAuthDialog
        auth_dlg = AdminAuthDialog(
            self,
            action_title="Bulk Delete Protection",
            action_context="Purge All Cancelled Receipts",
            module="Receipt History"
        )
        if not auth_dlg.exec():
            return

        reply = QMessageBox.question(
            self, "Confirm Bulk Delete Receipts",
            "Are you sure you want to bulk purge all cancelled receipts?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg, cnt = ReceiptController.bulk_delete_receipts()
            if success:
                QMessageBox.information(self, "Bulk Delete Result", msg)
                self.load_receipts()
            else:
                QMessageBox.critical(self, "Error", msg)

    def export_csv(self):
        headers = ["Receipt No", "Date", "Student Name", "Admission No", "Class", "Subtotal", "Discount", "Fine", "Total Amount", "Payment Mode", "Status"]
        receipts = ReceiptController.get_all_receipts()
        rows = [
            [
                r.receipt_no, format_date(r.receipt_date), r.student.name, r.student.admission_no,
                r.student.class_name, f"{r.subtotal:.2f}", f"{r.discount_amount:.2f}", f"{r.fine_amount:.2f}",
                f"{r.total_amount:.2f}", r.payment_mode, r.status
            ]
            for r in receipts
        ]
        path, _ = QFileDialog.getSaveFileName(self, "Export Receipt History CSV", "", "CSV Files (*.csv)")
        if path:
            success, msg = ExportService.export_to_csv(headers, rows, output_path=path)
            if success:
                QMessageBox.information(self, "Success", f"Exported {len(receipts)} receipts to:\n{path}")
            else:
                QMessageBox.critical(self, "Export Error", msg)
