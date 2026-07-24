"""
Receipt Print Preview & Action Dialog.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QTextEdit
)
from models.receipt import Receipt
from services.pdf_service import PDFService
from services.print_service import PrintService

class ReceiptPreviewDialog(QDialog):
    def __init__(self, parent=None, receipt: Optional[Receipt] = None, pdf_path: Optional[str] = None):
        super().__init__(parent)
        self.receipt = receipt
        self.pdf_path = pdf_path
        self.setWindowTitle(f"Receipt Preview - {receipt.receipt_no if receipt else 'Document'}")
        self.resize(600, 500)

        # Ensure PDF is generated
        if not self.pdf_path and self.receipt:
            self.pdf_path = PDFService.generate_receipt_pdf(self.receipt)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        hdr_label = QLabel(f"Receipt No: <b>{self.receipt.receipt_no if self.receipt else 'Preview'}</b>")
        hdr_label.setStyleSheet("font-size: 16px; color: #1e3a8a; padding: 5px;")
        layout.addWidget(hdr_label)

        # Receipt Summary Card
        if self.receipt:
            summary_txt = f"""
=====================================================
                 FEE RECEIPT DETAILS
=====================================================
Receipt Number : {self.receipt.receipt_no}
Date           : {self.receipt.receipt_date.strftime('%d-%m-%Y')}
Student Name   : {self.receipt.student.name}
Admission No   : {self.receipt.student.admission_no}
Class & Sec    : {self.receipt.student.class_name} ({self.receipt.student.section or 'A'})
Father's Name  : {self.receipt.student.father_name}
Academic Session: {self.receipt.academic_session}
-----------------------------------------------------
ITEMS PAID:
"""
            for item in self.receipt.items:
                summary_txt += f" - {item.category_name:<30}: ₹ {item.amount:,.2f}\n"

            summary_txt += f"""-----------------------------------------------------
Subtotal       : ₹ {self.receipt.subtotal:,.2f}
Discount (-)   : ₹ {self.receipt.discount_amount:,.2f}
Fine (+)       : ₹ {self.receipt.fine_amount:,.2f}
TOTAL PAID     : ₹ {self.receipt.total_amount:,.2f}
-----------------------------------------------------
Amount in Words: {self.receipt.amount_in_words}
Payment Mode   : {self.receipt.payment_mode}
=====================================================
"""
            txt_view = QTextEdit()
            txt_view.setReadOnly(True)
            txt_view.setFontFamily("Courier New")
            txt_view.setPlainText(summary_txt)
            layout.addWidget(txt_view)

        # Action buttons
        btn_layout = QHBoxLayout()

        self.btn_pdf_preview = QPushButton("Open Full A4 PDF Preview")
        self.btn_pdf_preview.setProperty("class", "SecondaryBtn")
        self.btn_pdf_preview.clicked.connect(self.open_pdf_preview)

        self.btn_print = QPushButton("Print Receipt (Ctrl+P)")
        self.btn_print.clicked.connect(self.print_receipt)

        self.btn_close = QPushButton("Close")
        self.btn_close.setProperty("class", "SecondaryBtn")
        self.btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_pdf_preview)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_print)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def open_pdf_preview(self):
        if self.pdf_path:
            PrintService.preview_pdf(self.pdf_path, self)

    def print_receipt(self):
        if self.pdf_path:
            PrintService.print_pdf(self.pdf_path, self)
