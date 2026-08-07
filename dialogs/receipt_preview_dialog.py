"""
Receipt Print Preview & Comprehensive Action Dialog (Print, Export PDF, Admin Delete).
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QTextEdit, QFileDialog
)
from PySide6.QtCore import Qt
from models.receipt import Receipt
from services.pdf_service import PDFService
from services.print_service import PrintService
from controllers.receipt_controller import ReceiptController
from dialogs.admin_auth_dialog import AdminAuthDialog
from utils.logger import logger


class ReceiptPreviewDialog(QDialog):
    def __init__(self, parent=None, receipt: Optional[Receipt] = None, pdf_path: Optional[str] = None):
        super().__init__(parent)
        self.receipt = receipt
        self.pdf_path = pdf_path
        self.setWindowTitle(f"Receipt Details & Actions - {receipt.receipt_no if receipt else 'Document'}")
        self.resize(650, 520)

        # Ensure PDF is generated
        if not self.pdf_path and self.receipt:
            self.pdf_path = PDFService.generate_receipt_pdf(self.receipt)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        hdr_label = QLabel(f"Receipt No: <b>{self.receipt.receipt_no if self.receipt else 'Preview'}</b>")
        hdr_label.setStyleSheet("font-size: 16px; color: #1e3a8a; font-weight: bold;")
        layout.addWidget(hdr_label)

        # Receipt Summary Card Text
        if self.receipt:
            paid_amt = getattr(self.receipt, 'paid_amount', self.receipt.total_amount) or self.receipt.total_amount
            due_amt = getattr(self.receipt, 'due_amount', 0.0) or 0.0

            summary_txt = f"""
====================================================
                 FEE RECEIPT DETAILS
====================================================
Receipt Number : {self.receipt.receipt_no}
Date           : {self.receipt.receipt_date.strftime('%d-%m-%Y')}
Student Name   : {self.receipt.student.name}
Admission No   : {self.receipt.student.admission_no}
Course         : {self.receipt.student.course or 'UG'}
Class & Sec    : {self.receipt.student.class_name} ({self.receipt.student.section or 'A'})
Father's Name  : {self.receipt.student.father_name}
Academic Session: {self.receipt.academic_session}
Status         : {self.receipt.status}
----------------------------------------------------
ITEMS INCLUDED:
"""
            for item in self.receipt.items:
                summary_txt += f" - {item.category_name:<30}: ₹ {item.amount:,.2f}\n"

            summary_txt += f"""----------------------------------------------------
Subtotal       : ₹ {self.receipt.subtotal:,.2f}
Discount       : ₹ {self.receipt.discount_amount:,.2f}
Fine           : ₹ {self.receipt.fine_amount:,.2f}
Total Fee      : ₹ {self.receipt.total_amount:,.2f}
PAID AMOUNT    : ₹ {paid_amt:,.2f}
OUTSTANDING DUE: ₹ {due_amt:,.2f}
----------------------------------------------------
Amount in Words: {self.receipt.amount_in_words}
----------------------------------------------------
PAYMENT DETAILS:
Payment Mode   : {self.receipt.payment_mode}
"""
            pm_upper = self.receipt.payment_mode.upper()
            if "UPI" in pm_upper or "QR" in pm_upper:
                if getattr(self.receipt, 'utr_number', None):
                    summary_txt += f"UTR Number     : {self.receipt.utr_number}\n"
                if getattr(self.receipt, 'bank_name', None):
                    summary_txt += f"Bank Name      : {self.receipt.bank_name}\n"
                if getattr(self.receipt, 'payment_date', None) and self.receipt.payment_date:
                    summary_txt += f"Payment Date   : {self.receipt.payment_date.strftime('%d-%m-%Y')}\n"
            elif "CHEQUE" in pm_upper or "DD" in pm_upper or "DEMAND" in pm_upper:
                if getattr(self.receipt, 'cheque_number', None):
                    summary_txt += f"Cheque/DD No   : {self.receipt.cheque_number}\n"
                if getattr(self.receipt, 'cheque_date', None) and self.receipt.cheque_date:
                    summary_txt += f"Cheque Date    : {self.receipt.cheque_date.strftime('%d-%m-%Y')}\n"
                if getattr(self.receipt, 'bank_name', None):
                    summary_txt += f"Bank Name      : {self.receipt.bank_name}\n"
            elif "NET" in pm_upper or "NEFT" in pm_upper:
                if getattr(self.receipt, 'utr_number', None) or self.receipt.reference_no:
                    summary_txt += f"Ref / UTR No   : {getattr(self.receipt, 'utr_number', None) or self.receipt.reference_no}\n"
                if getattr(self.receipt, 'bank_name', None):
                    summary_txt += f"Bank Name      : {self.receipt.bank_name}\n"
            else:
                if self.receipt.reference_no:
                    summary_txt += f"Reference No   : {self.receipt.reference_no}\n"

            if self.receipt.remarks:
                summary_txt += f"Remarks        : {self.receipt.remarks}\n"

            summary_txt += "=====================================================\n"
            txt_view = QTextEdit()
            txt_view.setReadOnly(True)
            txt_view.setFontFamily("Courier New")
            txt_view.setPlainText(summary_txt)
            layout.addWidget(txt_view)

        # Action Buttons Toolbar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_print = QPushButton("🖨 Print Receipt")
        self.btn_print.setFixedHeight(34)
        self.btn_print.setStyleSheet("background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; padding: 0 14px;")
        self.btn_print.setCursor(Qt.PointingHandCursor)
        self.btn_print.clicked.connect(self.print_receipt)

        self.btn_pdf_export = QPushButton("📄 Export PDF")
        self.btn_pdf_export.setFixedHeight(34)
        self.btn_pdf_export.setStyleSheet("background-color: #059669; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; padding: 0 14px;")
        self.btn_pdf_export.setCursor(Qt.PointingHandCursor)
        self.btn_pdf_export.clicked.connect(self.export_pdf)

        self.btn_delete = QPushButton("🚫 Delete (Admin)")
        self.btn_delete.setFixedHeight(34)
        self.btn_delete.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; padding: 0 14px;")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_receipt)

        self.btn_close = QPushButton("Close")
        self.btn_close.setFixedHeight(34)
        self.btn_close.setStyleSheet("background-color: #f1f5f9; color: #334155; font-weight: bold; border-radius: 4px; border: 1px solid #cbd5e1; padding: 0 14px;")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_print)
        btn_layout.addWidget(self.btn_pdf_export)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def print_receipt(self):
        if self.pdf_path:
            try:
                PrintService.print_pdf(self.pdf_path, self)
            except Exception as e:
                import os
                os.startfile(self.pdf_path, "print")

    def export_pdf(self):
        if not self.pdf_path and self.receipt:
            self.pdf_path = PDFService.generate_receipt_pdf(self.receipt)

        default_name = f"Receipt_{self.receipt.receipt_no.replace('/', '_')}.pdf" if self.receipt else "Receipt.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Save Receipt PDF", default_name, "PDF Files (*.pdf)")
        if path:
            import shutil
            shutil.copy(self.pdf_path, path)
            QMessageBox.information(self, "PDF Exported", f"Receipt PDF saved successfully to:\n{path}")

    def delete_receipt(self):
        if not self.receipt:
            return

        auth_dlg = AdminAuthDialog(
            self,
            action_title="Administrator Password Required",
            action_context=f"Cancel / Delete Receipt: '{self.receipt.receipt_no}'",
            module="Receipt History"
        )
        if not auth_dlg.exec():
            return

        from views.receipt_history_view import DeleteReasonDialog
        reason_dlg = DeleteReasonDialog(self, context_text=f"Deleting Receipt '{self.receipt.receipt_no}'")
        if not reason_dlg.exec():
            return

        reply = QMessageBox.question(
            self, "Confirm Delete Receipt",
            f"Are you sure you want to cancel/delete receipt '{self.receipt.receipt_no}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = ReceiptController.cancel_receipt(self.receipt.id, reason=reason_dlg.reason)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.accept()
                if self.parent() and hasattr(self.parent(), "load_receipts"):
                    self.parent().load_receipts()
            else:
                QMessageBox.critical(self, "Error", msg)
