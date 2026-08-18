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


from controllers.settings_controller import SettingsController

def generate_receipt_html(receipt: Receipt) -> str:
    school_info = SettingsController.get_school_info()
    school_name = getattr(school_info, "name", None) or "EduLedger Institute of Technology & Management"
    school_addr = getattr(school_info, "address", None) or "Main Campus, Knowledge Park, Education Hub"
    school_city = getattr(school_info, "city", None) or "New Delhi"
    school_state = getattr(school_info, "state", None) or "Delhi"
    school_pin = getattr(school_info, "pin_code", None) or "110001"
    school_phone = getattr(school_info, "phone", None) or "011-23456789"

    st = receipt.student
    paid_amt = getattr(receipt, 'paid_amount', receipt.total_amount) or receipt.total_amount
    due_amt = getattr(receipt, 'due_amount', 0.0) or 0.0

    fee_rows_html = ""
    if receipt.items:
        for idx, item in enumerate(receipt.items, start=1):
            cat_name = getattr(item, "category_name", "Fee Head")
            fee_rows_html += f"""
            <tr>
                <td style="text-align: center; border: 1px solid #cbd5e1; padding: 4px 6px;">{idx}</td>
                <td style="border: 1px solid #cbd5e1; padding: 4px 6px;">{cat_name}</td>
                <td style="text-align: right; border: 1px solid #cbd5e1; padding: 4px 6px;">₹ {item.amount:,.2f}</td>
            </tr>
            """
    else:
        fee_rows_html = f"""
        <tr>
            <td style="text-align: center; border: 1px solid #cbd5e1; padding: 4px 6px;">1</td>
            <td style="border: 1px solid #cbd5e1; padding: 4px 6px;">Tuition & Academic Fees</td>
            <td style="text-align: right; border: 1px solid #cbd5e1; padding: 4px 6px;">₹ {receipt.total_amount:,.2f}</td>
        </tr>
        """

    payment_details_str = f"<b>Mode:</b> {receipt.payment_mode}"
    if receipt.reference_no:
        payment_details_str += f" | <b>Ref / Txn No:</b> {receipt.reference_no}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; color: #0f172a; margin: 0; padding: 8px; }}
        .header {{ text-align: center; margin-bottom: 6px; border-bottom: 2px solid #1e3a8a; padding-bottom: 4px; }}
        .school-name {{ font-size: 16px; font-weight: 800; color: #1e3a8a; margin: 0; text-transform: uppercase; }}
        .school-sub {{ font-size: 10px; color: #475569; margin-top: 2px; }}
        .badge-row {{ text-align: center; margin: 6px 0; }}
        .badge {{ background-color: #1e3a8a; color: #ffffff; padding: 3px 12px; font-weight: 800; font-size: 11px; border-radius: 3px; display: inline-block; }}
        .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 6px; font-size: 10.5px; }}
        .info-table td {{ padding: 3px 4px; vertical-align: top; }}
        .info-label {{ font-weight: 700; color: #334155; width: 18%; }}
        .info-val {{ color: #0f172a; width: 32%; }}
        .fee-table {{ width: 100%; border-collapse: collapse; margin-bottom: 6px; font-size: 10px; border: 1px solid #cbd5e1; }}
        .fee-table th {{ background-color: #1e3a8a; color: #ffffff; padding: 4px 6px; font-weight: bold; text-align: left; border: 1px solid #1e3a8a; }}
        .summary-box {{ background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 6px; margin-bottom: 6px; font-size: 10.5px; }}
        .footer {{ text-align: right; margin-top: 15px; font-size: 10px; font-weight: 700; color: #1e3a8a; }}
    </style>
    </head>
    <body>
        <div class="header">
            <div class="school-name">{school_name}</div>
            <div class="school-sub">{school_addr}, {school_city}, {school_state} - {school_pin} | Ph: {school_phone}</div>
        </div>

        <div class="badge-row">
            <span class="badge">FEE PAYMENT RECEIPT</span>
        </div>

        <table class="info-table">
            <tr>
                <td class="info-label">Receipt No:</td>
                <td class="info-val"><b>{receipt.receipt_no}</b></td>
                <td class="info-label">Receipt Date:</td>
                <td class="info-val">{receipt.receipt_date.strftime('%d-%m-%Y')}</td>
            </tr>
            <tr>
                <td class="info-label">Admission No:</td>
                <td class="info-val"><b>{st.admission_no}</b></td>
                <td class="info-label">Enrollment No:</td>
                <td class="info-val"><b>{getattr(st, "enrollment_no", None) or "N/A"}</b></td>
            </tr>
            <tr>
                <td class="info-label">Student Name:</td>
                <td class="info-val"><b>{st.name}</b></td>
                <td class="info-label">Father's Name:</td>
                <td class="info-val">{st.father_name}</td>
            </tr>
            <tr>
                <td class="info-label">Course / Program:</td>
                <td class="info-val">{getattr(st, 'course', None) or 'General'}</td>
                <td class="info-label">Year / Semester:</td>
                <td class="info-val">{getattr(st, 'year', None) or 'N/A'} / {getattr(st, 'semester', None) or 'N/A'}</td>
            </tr>
        </table>

        <table class="fee-table">
            <thead>
                <tr>
                    <th style="width: 8%; text-align: center;">#</th>
                    <th style="width: 65%;">Fee Head / Particular Description</th>
                    <th style="width: 27%; text-align: right;">Amount (₹)</th>
                </tr>
            </thead>
            <tbody>
                {fee_rows_html}
            </tbody>
        </table>

        <div class="summary-box">
            <table style="width: 100%; font-size: 10.5px;">
                <tr>
                    <td><b>Total Calculated Fee:</b> ₹ {receipt.total_amount:,.2f}</td>
                    <td style="text-align: right;"><b>Total Amount Paid:</b> <span style="color: #166534; font-weight: 800;">₹ {paid_amt:,.2f}</span></td>
                </tr>
                <tr>
                    <td><b>Amount in Words:</b> {receipt.amount_in_words}</td>
                    <td style="text-align: right;"><b>Balance Due:</b> <span style="color: {'#dc2626' if due_amt > 0 else '#166534'}; font-weight: 800;">₹ {due_amt:,.2f}</span></td>
                </tr>
                <tr>
                    <td colspan="2" style="padding-top: 4px;">{payment_details_str}</td>
                </tr>
            </table>
        </div>

        <div class="footer">
            <br>
            Authorized Signatory / Cashier Stamp
        </div>
    </body>
    </html>
    """
    return html

class ReceiptPreviewDialog(QDialog):
    def __init__(self, parent=None, receipt: Optional[Receipt] = None, pdf_path: Optional[str] = None):
        super().__init__(parent)
        self.receipt = receipt
        self.pdf_path = pdf_path
        self.setWindowTitle(f"Receipt Details & Actions - {receipt.receipt_no if receipt else 'Document'}")
        self.setMinimumSize(540, 520)
        self.resize(680, 620)

        # Ensure PDF is generated
        if not self.pdf_path and self.receipt:
            self.pdf_path = PDFService.generate_receipt_pdf(self.receipt)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        hdr_label = QLabel(f"Receipt No: <b>{self.receipt.receipt_no if self.receipt else 'Preview'}</b>")
        hdr_label.setStyleSheet("font-size: 16px; color: #1e3a8a; font-weight: bold;")
        layout.addWidget(hdr_label)

        if self.receipt:
            txt_view = QTextEdit()
            txt_view.setReadOnly(True)
            txt_view.setHtml(generate_receipt_html(self.receipt))
            layout.addWidget(txt_view)

        # Action Buttons Toolbar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_print = QPushButton("🖨 Print Receipt")
        self.btn_print.setFixedHeight(34)
        self.btn_print.setStyleSheet("background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; padding: 0 14px;")
        self.btn_print.setCursor(Qt.PointingHandCursor)
        self.btn_print.clicked.connect(self.print_receipt)

        self.btn_open_pdf = QPushButton("📂 Open PDF")
        self.btn_open_pdf.setFixedHeight(34)
        self.btn_open_pdf.setStyleSheet("background-color: #1e3a8a; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; padding: 0 14px;")
        self.btn_open_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_open_pdf.clicked.connect(self.open_pdf)

        self.btn_pdf_export = QPushButton("📄 Save PDF As...")
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
        btn_layout.addWidget(self.btn_open_pdf)
        btn_layout.addWidget(self.btn_pdf_export)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def open_pdf(self):
        if not self.pdf_path and self.receipt:
            self.pdf_path = PDFService.generate_receipt_pdf(self.receipt)

        if self.pdf_path and Path(self.pdf_path).exists():
            import os
            try:
                os.startfile(self.pdf_path)
            except Exception as e:
                QMessageBox.critical(self, "Error Opening PDF", f"Could not open PDF file:\n{str(e)}")
        else:
            QMessageBox.warning(self, "File Not Found", "Generated PDF file was not found.")

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
