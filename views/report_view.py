"""
Financial Analytics & Fee Collection Reports View with Enhanced QDateEdit Pickers.
"""

from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from controllers.report_controller import ReportController
from controllers.student_controller import StudentController
from services.pdf_service import PDFService
from services.export_service import ExportService
from services.print_service import PrintService
from utils.helpers import format_currency, format_date

class ReportView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_report_data = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        hdr = QHBoxLayout()
        title_lbl = QLabel("Fee Collection Reports & Financial Statement")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a;")
        hdr.addWidget(title_lbl)
        hdr.addStretch()

        self.btn_export_pdf = QPushButton("📄  Export Report PDF")
        self.btn_export_pdf.setFixedHeight(36)
        self.btn_export_pdf.setProperty("class", "SecondaryBtn")
        self.btn_export_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_export_pdf.clicked.connect(self.export_pdf)

        self.btn_export_csv = QPushButton("📥  Export CSV")
        self.btn_export_csv.setFixedHeight(36)
        self.btn_export_csv.setProperty("class", "SecondaryBtn")
        self.btn_export_csv.setCursor(Qt.PointingHandCursor)
        self.btn_export_csv.clicked.connect(self.export_csv)

        hdr.addWidget(self.btn_export_pdf)
        hdr.addWidget(self.btn_export_csv)
        layout.addLayout(hdr)

        # Filter Panel
        filter_box = QGroupBox("Report Filters & Criteria")
        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(10)

        self.cmb_report_type = QComboBox()
        self.cmb_report_type.setFixedHeight(36)
        self.cmb_report_type.addItems([
            "Daily Collection Report",
            "Monthly Collection Report",
            "Custom Date Range Report",
            "Class-Wise Collection Summary"
        ])
        self.cmb_report_type.currentIndexChanged.connect(self.on_report_type_changed)

        # Start Date Edit
        self.dt_start = QDateEdit()
        self.dt_start.setFixedHeight(36)
        self.dt_start.setMinimumWidth(130)
        self.dt_start.setCalendarPopup(True)
        self.dt_start.setDisplayFormat("dd-MM-yyyy")
        self.dt_start.setDate(QDate.currentDate())

        # End Date Edit
        self.dt_end = QDateEdit()
        self.dt_end.setFixedHeight(36)
        self.dt_end.setMinimumWidth(130)
        self.dt_end.setCalendarPopup(True)
        self.dt_end.setDisplayFormat("dd-MM-yyyy")
        self.dt_end.setDate(QDate.currentDate())

        self.cmb_class = QComboBox()
        self.cmb_class.setFixedHeight(36)
        self.cmb_class.addItem("All Classes", "All")
        classes = StudentController.get_distinct_classes()
        for c in classes:
            self.cmb_class.addItem(c, c)

        self.btn_generate = QPushButton("📊  Generate Report")
        self.btn_generate.setFixedHeight(36)
        self.btn_generate.setCursor(Qt.PointingHandCursor)
        self.btn_generate.clicked.connect(self.generate_report)

        filter_layout.addWidget(QLabel("Report Type:"), stretch=0)
        filter_layout.addWidget(self.cmb_report_type, stretch=2)
        filter_layout.addWidget(QLabel("Start Date:"), stretch=0)
        filter_layout.addWidget(self.dt_start, stretch=1)
        filter_layout.addWidget(QLabel("End Date:"), stretch=0)
        filter_layout.addWidget(self.dt_end, stretch=1)
        filter_layout.addWidget(QLabel("Class:"), stretch=0)
        filter_layout.addWidget(self.cmb_class, stretch=1)
        filter_layout.addWidget(self.btn_generate, stretch=1)

        layout.addWidget(filter_box)

        # Summary Metrics Box
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.lbl_card_count = QLabel("Total Receipts: <b>0</b>")
        self.lbl_card_col = QLabel("Total Collection: <b>₹ 0.00</b>")
        self.lbl_card_disc = QLabel("Total Discounts: <b>₹ 0.00</b>")
        self.lbl_card_fine = QLabel("Total Fines: <b>₹ 0.00</b>")

        for lbl in [self.lbl_card_count, self.lbl_card_col, self.lbl_card_disc, self.lbl_card_fine]:
            lbl.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; font-size: 13px; color: #1e3a8a;")
            metrics_layout.addWidget(lbl)

        layout.addLayout(metrics_layout)

        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Receipt No", "Date", "Student Name", "Class", "Subtotal", "Discount", "Fine", "Total Collected (₹)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        self.on_report_type_changed()
        self.generate_report()

    def on_report_type_changed(self):
        idx = self.cmb_report_type.currentIndex()
        if idx == 0:  # Daily
            self.dt_start.setEnabled(True)
            self.dt_end.setEnabled(False)
            self.dt_start.setDate(QDate.currentDate())
        elif idx == 1:  # Monthly
            self.dt_start.setEnabled(True)
            self.dt_end.setEnabled(False)
            self.dt_start.setDate(QDate.currentDate().addDays(-30))
        elif idx == 2:  # Custom Range
            self.dt_start.setEnabled(True)
            self.dt_end.setEnabled(True)
        elif idx == 3:  # Class Summary
            self.dt_start.setEnabled(False)
            self.dt_end.setEnabled(False)

    def generate_report(self):
        idx = self.cmb_report_type.currentIndex()
        class_filter = self.cmb_class.currentData() or "All"

        if idx == 3:  # Class-wise summary
            summary = ReportController.get_class_wise_summary()
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["Class Name", "Receipts Issued", "Total Collection (₹)"])
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.setRowCount(len(summary))

            tot_col = sum(s["total_collected"] for s in summary)
            tot_cnt = sum(s["receipt_count"] for s in summary)

            for r_idx, s in enumerate(summary):
                self.table.setItem(r_idx, 0, QTableWidgetItem(s["class_name"]))
                self.table.setItem(r_idx, 1, QTableWidgetItem(str(s["receipt_count"])))
                self.table.setItem(r_idx, 2, QTableWidgetItem(format_currency(s["total_collected"])))

            self.lbl_card_count.setText(f"Total Classes: <b>{len(summary)}</b>")
            self.lbl_card_col.setText(f"Total Collection: <b>{format_currency(tot_col)}</b>")
            self.lbl_card_disc.setText("Discounts: <b>N/A</b>")
            self.lbl_card_fine.setText("Fines: <b>N/A</b>")

            self.current_report_data = {
                "title": "Class-Wise Fee Collection Summary",
                "headers": ["Class Name", "Receipts Issued", "Total Collection (Rs.)"],
                "rows": [[s["class_name"], str(s["receipt_count"]), f"Rs. {s['total_collected']:,.2f}"] for s in summary]
            }
            return

        # Detailed Receipts Report
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Receipt No", "Date", "Student Name", "Class", "Subtotal", "Discount", "Fine", "Total Collected (₹)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        qstart = self.dt_start.date()
        qend = self.dt_end.date()

        date_from = date(qstart.year(), qstart.month(), qstart.day())
        date_to = date(qend.year(), qend.month(), qend.day()) if idx == 2 else date_from

        rep = ReportController.get_collection_report(
            date_from=date_from,
            date_to=date_to,
            class_filter=class_filter
        )

        receipts = rep["receipts"]
        self.table.setRowCount(len(receipts))

        rows_pdf = []
        for r_idx, r in enumerate(receipts):
            self.table.setItem(r_idx, 0, QTableWidgetItem(r.receipt_no))
            self.table.setItem(r_idx, 1, QTableWidgetItem(format_date(r.receipt_date)))
            self.table.setItem(r_idx, 2, QTableWidgetItem(r.student.name if r.student else "N/A"))
            self.table.setItem(r_idx, 3, QTableWidgetItem(r.student.class_name if r.student else "N/A"))
            self.table.setItem(r_idx, 4, QTableWidgetItem(f"{r.subtotal:,.2f}"))
            self.table.setItem(r_idx, 5, QTableWidgetItem(f"{r.discount_amount:,.2f}"))
            self.table.setItem(r_idx, 6, QTableWidgetItem(f"{r.fine_amount:,.2f}"))
            self.table.setItem(r_idx, 7, QTableWidgetItem(format_currency(r.total_amount)))

            rows_pdf.append([
                r.receipt_no, format_date(r.receipt_date), r.student.name if r.student else "N/A",
                r.student.class_name if r.student else "N/A", f"{r.subtotal:,.2f}",
                f"{r.discount_amount:,.2f}", f"{r.fine_amount:,.2f}", f"{r.total_amount:,.2f}"
            ])

        self.lbl_card_count.setText(f"Total Receipts: <b>{rep['total_receipts']}</b>")
        self.lbl_card_col.setText(f"Total Collection: <b>{format_currency(rep['total_collection'])}</b>")
        self.lbl_card_disc.setText(f"Total Discounts: <b>{format_currency(rep['total_discount'])}</b>")
        self.lbl_card_fine.setText(f"Total Fines: <b>{format_currency(rep['total_fine'])}</b>")

        self.current_report_data = {
            "title": self.cmb_report_type.currentText(),
            "headers": ["Receipt No", "Date", "Student Name", "Class", "Subtotal", "Discount", "Fine", "Total (Rs.)"],
            "rows": rows_pdf
        }

    def export_pdf(self):
        if not self.current_report_data:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Report PDF", "", "PDF Files (*.pdf)")
        if path:
            pdf_path = PDFService.generate_report_pdf(
                title=self.current_report_data["title"],
                headers=self.current_report_data["headers"],
                rows=self.current_report_data["rows"],
                output_path=path
            )
            QMessageBox.information(self, "Success", f"Report PDF saved to:\n{pdf_path}")
            PrintService.preview_pdf(pdf_path, self)

    def export_csv(self):
        if not self.current_report_data:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Report CSV", "", "CSV Files (*.csv)")
        if path:
            success, msg = ExportService.export_to_csv(
                headers=self.current_report_data["headers"],
                rows=self.current_report_data["rows"],
                output_path=path
            )
            if success:
                QMessageBox.information(self, "Success", f"Report CSV saved to:\n{path}")
            else:
                QMessageBox.critical(self, "Error", msg)
