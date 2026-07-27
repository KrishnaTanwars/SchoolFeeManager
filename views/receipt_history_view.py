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

        self.btn_export = QPushButton("📥  Export CSV")
        self.btn_export.setProperty("class", "SecondaryBtn")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_csv)

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
        
        # Explicit section resize modes: data columns stretch, Actions column fixed to 160px
        header = self.table.horizontalHeader()
        for col in range(8):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 160)

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
            act_layout.setContentsMargins(6, 4, 6, 4)
            act_layout.setAlignment(Qt.AlignCenter)

            btn_view = QPushButton("👁  View / Print")
            btn_view.setFixedHeight(30)
            btn_view.setMinimumWidth(130)
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #1e3a8a;
                    color: #ffffff;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 5px;
                    border: none;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.clicked.connect(lambda _, rec=r: self.view_receipt(rec))

            act_layout.addWidget(btn_view)
            self.table.setCellWidget(row_idx, 8, action_widget)

    def view_receipt(self, receipt):
        dlg = ReceiptPreviewDialog(self, receipt)
        dlg.exec()

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
