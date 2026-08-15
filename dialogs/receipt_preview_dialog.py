"""
Receipt Print Preview & Comprehensive Action Dialog (Print, Export PDF, Admin Delete).
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QTextBrowser, QFileDialog
)
from PySide6.QtCore import Qt
from models.receipt import Receipt
from services.pdf_service import PDFService
from services.print_service import PrintService
from controllers.receipt_controller import ReceiptController
from controllers.settings_controller import SettingsController
from dialogs.admin_auth_dialog import AdminAuthDialog
from utils.logger import logger


def generate_receipt_html(receipt: Receipt) -> str:
    """Generates professional HTML template for receipt preview matching printable PDF document."""
    school_info = SettingsController.get_school_info()
    school_name = school_info.school_name if school_info else "DPS International Public School"
    school_addr = school_info.address if school_info else "Plot 12, Sector 5, RK Puram, New Delhi - 110022"
    school_phone = school_info.phone if school_info else "+91 98765 43210, 011-26123456"
    school_email = school_info.email if school_info else "accounts@dpsschool.edu.in"

    student = getattr(receipt, "student", None)
    st_name = getattr(student, "name", "N/A") if student else "N/A"
    adm_no = getattr(student, "admission_no", "N/A") if student else "N/A"
    father_name = getattr(student, "father_name", "N/A") if student else "N/A"

    course_str = getattr(receipt, "course", None) or (getattr(student, "course", None) if student else None) or "General"
    branch_str = getattr(receipt, "branch", None) or (getattr(student, "branch", None) if student else None) or ""
    crs_br = f"{course_str}" + (f" ({branch_str})" if branch_str else "")

    year_str = getattr(receipt, "academic_year", None) or (getattr(student, "year", None) if student else None) or "N/A"
    sem_str = getattr(receipt, "semester", None) or (getattr(student, "semester", None) if student else None) or "N/A"
    yr_sem = f"{year_str} / {sem_str}"

    class_name = (getattr(student, "class_name", "") if student else "") or course_str
    section = (getattr(student, "section", "") if student else "") or "A"
    class_sec = f"{class_name} ({section})" if section else class_name

    rec_date = receipt.receipt_date.strftime('%d-%m-%Y') if receipt.receipt_date else "N/A"
    paid_amt = getattr(receipt, 'paid_amount', receipt.total_amount) or receipt.total_amount
    due_amt = getattr(receipt, 'due_amount', 0.0) or 0.0

    # Fee Head Particulars Table Rows
    fee_rows_html = ""
    if receipt.items:
        for idx, item in enumerate(receipt.items, 1):
            bg_color = "#f8fafc" if idx % 2 == 1 else "#ffffff"
            cat_name = getattr(item, "category_name", "Fee Head")
            amt_val = getattr(item, "amount", 0.0)
            fee_rows_html += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: center;">{idx}</td>
                <td style="padding: 7px 10px; border: 1px solid #cbd5e1; font-weight: 700; color: #0f172a;">{cat_name}</td>
                <td style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right; font-weight: 700;">₹ {amt_val:,.2f}</td>
            </tr>
            """
    else:
        fee_rows_html = f"""
        <tr>
            <td style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: center;">1</td>
            <td style="padding: 7px 10px; border: 1px solid #cbd5e1; font-weight: 700;">Tuition Fee</td>
            <td style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right; font-weight: 700;">₹ {receipt.total_amount:,.2f}</td>
        </tr>
        """

    # Summary Rows
    summary_rows = f"""
    <tr style="background-color: #f1f5f9; font-weight: bold;">
        <td colspan="2" style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right;">Total Calculated Fee:</td>
        <td style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right; color: #0f172a;">₹ {receipt.subtotal:,.2f}</td>
    </tr>
    """
    if receipt.discount_amount and receipt.discount_amount > 0:
        summary_rows += f"""
        <tr style="background-color: #f1f5f9; color: #15803d;">
            <td colspan="2" style="padding: 6px 10px; border: 1px solid #cbd5e1; text-align: right;">Discount (-):</td>
            <td style="padding: 6px 10px; border: 1px solid #cbd5e1; text-align: right;">- ₹ {receipt.discount_amount:,.2f}</td>
        </tr>
        """
    if receipt.fine_amount and receipt.fine_amount > 0:
        summary_rows += f"""
        <tr style="background-color: #f1f5f9; color: #b91c1c;">
            <td colspan="2" style="padding: 6px 10px; border: 1px solid #cbd5e1; text-align: right;">Fine / Penalty (+):</td>
            <td style="padding: 6px 10px; border: 1px solid #cbd5e1; text-align: right;">+ ₹ {receipt.fine_amount:,.2f}</td>
        </tr>
        """
    summary_rows += f"""
    <tr style="background-color: #e2e8f0; font-weight: bold; font-size: 12px;">
        <td colspan="2" style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right;">ACTUAL PAID AMOUNT:</td>
        <td style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right; color: #1e3a8a;">₹ {paid_amt:,.2f}</td>
    </tr>
    """
    if due_amt > 0:
        summary_rows += f"""
        <tr style="background-color: #fef2f2; font-weight: bold; color: #dc2626;">
            <td colspan="2" style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right;">OUTSTANDING DUE:</td>
            <td style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right;">₹ {due_amt:,.2f}</td>
        </tr>
        """
    else:
        summary_rows += f"""
        <tr style="background-color: #f0fdf4; font-weight: bold; color: #166534;">
            <td colspan="2" style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right;">OUTSTANDING DUE:</td>
            <td style="padding: 7px 10px; border: 1px solid #cbd5e1; text-align: right;">₹ 0.00 (PAID IN FULL)</td>
        </tr>
        """

    # Payment Details Section
    pm_upper = receipt.payment_mode.upper() if receipt.payment_mode else "CASH"
    payment_info_str = f"<b>Payment Mode:</b> {receipt.payment_mode}"
    if "UPI" in pm_upper or "QR" in pm_upper:
        if getattr(receipt, 'utr_number', None):
            payment_info_str += f" &nbsp;|&nbsp; <b>UTR No:</b> {receipt.utr_number}"
        if getattr(receipt, 'bank_name', None):
            payment_info_str += f" &nbsp;|&nbsp; <b>Bank:</b> {receipt.bank_name}"
    elif "CHEQUE" in pm_upper or "DD" in pm_upper or "DEMAND" in pm_upper:
        if getattr(receipt, 'cheque_number', None):
            payment_info_str += f" &nbsp;|&nbsp; <b>Cheque/DD No:</b> {receipt.cheque_number}"
        if getattr(receipt, 'cheque_date', None) and receipt.cheque_date:
            payment_info_str += f" &nbsp;|&nbsp; <b>Date:</b> {receipt.cheque_date.strftime('%d-%m-%Y')}"
        if getattr(receipt, 'bank_name', None):
            payment_info_str += f" &nbsp;|&nbsp; <b>Bank:</b> {receipt.bank_name}"
    elif "NET" in pm_upper or "NEFT" in pm_upper or "CARD" in pm_upper:
        if getattr(receipt, 'utr_number', None) or receipt.reference_no:
            payment_info_str += f" &nbsp;|&nbsp; <b>Txn/Ref No:</b> {getattr(receipt, 'utr_number', None) or receipt.reference_no}"
        if getattr(receipt, 'bank_name', None):
            payment_info_str += f" &nbsp;|&nbsp; <b>Bank:</b> {receipt.bank_name}"
    else:
        if receipt.reference_no:
            payment_info_str += f" &nbsp;|&nbsp; <b>Ref No:</b> {receipt.reference_no}"

    if receipt.remarks:
        payment_info_str += f" &nbsp;|&nbsp; <b>Remarks:</b> {receipt.remarks}"

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; margin: 0; padding: 4px; background-color: #f1f5f9; }}
            .receipt-card {{ border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; background: #ffffff; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); }}
            .header-table {{ width: 100%; border-bottom: 2px solid #1e3a8a; padding-bottom: 4px; margin-bottom: 6px; }}
            .school-title {{ color: #1e3a8a; font-size: 17px; font-weight: bold; margin: 0; text-align: center; }}
            .school-subtitle {{ color: #475569; font-size: 10.5px; margin-top: 2px; text-align: center; }}
            .badge-container {{ text-align: center; margin: 6px 0 8px 0; }}
            .badge {{ background-color: #1e3a8a; color: #ffffff; padding: 4px 14px; font-weight: bold; font-size: 11px; border-radius: 4px; display: inline-block; letter-spacing: 1px; }}
            .info-table {{ width: 100%; border-collapse: collapse; background-color: #f8fafc; border: 1px solid #cbd5e1; margin-bottom: 8px; font-size: 10.5px; }}
            .info-table td {{ padding: 3px 6px; border: 1px solid #e2e8f0; }}
            .info-label {{ font-weight: bold; color: #334155; width: 18%; }}
            .info-val {{ color: #0f172a; width: 32%; }}
            .fee-table {{ width: 100%; border-collapse: collapse; margin-bottom: 8px; font-size: 10.5px; border: 1px solid #cbd5e1; }}
            .fee-table th {{ background-color: #1e3a8a; color: #ffffff; padding: 5px 6px; font-weight: bold; text-align: left; }}
            .words-box {{ background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 5px 8px; font-size: 10.5px; border-radius: 4px; margin-bottom: 8px; }}
            .payment-box {{ background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 5px 8px; font-size: 10.5px; border-radius: 4px; margin-bottom: 10px; color: #334155; }}
            .sig-table {{ width: 100%; margin-top: 14px; font-size: 10.5px; color: #475569; }}
        </style>
    </head>
    <body>
        <div class="receipt-card">
            <table class="header-table">
                <tr>
                    <td align="center">
                        <div class="school-title">{school_name}</div>
                        <div class="school-subtitle">{school_addr}<br/>Ph: {school_phone} | Email: {school_email}</div>
                    </td>
                </tr>
            </table>

            <div class="badge-container">
                <span class="badge">FEE PAYMENT RECEIPT</span>
            </div>

            <table class="info-table">
                <tr>
                    <td class="info-label">Receipt No:</td>
                    <td class="info-val" style="font-weight: bold; color: #1e3a8a;">{receipt.receipt_no}</td>
                    <td class="info-label">Receipt Date:</td>
                    <td class="info-val">{rec_date}</td>
                </tr>
                <tr>
                    <td class="info-label">Admission / Enrollment No:</td>
                    <td class="info-val" style="font-weight: bold;">{adm_no}</td>
                    <td class="info-label">Academic Session:</td>
                    <td class="info-val">{receipt.academic_session}</td>
                </tr>
                <tr>
                    <td class="info-label">Student Name:</td>
                    <td class="info-val" style="font-weight: bold; color: #0f172a;">{st_name}</td>
                    <td class="info-label">Course / Branch:</td>
                    <td class="info-val">{crs_br}</td>
                </tr>
                <tr>
                    <td class="info-label">Father's Name:</td>
                    <td class="info-val">{father_name}</td>
                    <td class="info-label">Year / Semester:</td>
                    <td class="info-val">{yr_sem}</td>
                </tr>
                <tr>
                    <td class="info-label">Class / Section:</td>
                    <td class="info-val">{class_sec}</td>
                    <td class="info-label">Status:</td>
                    <td class="info-val" style="font-weight: bold; color: #15803d;">{receipt.status}</td>
                </tr>
            </table>

            <table class="fee-table">
                <thead>
                    <tr>
                        <th style="width: 10%; text-align: center;">S.No</th>
                        <th style="width: 65%;">Fee Head / Particular Description</th>
                        <th style="width: 25%; text-align: right;">Amount (₹)</th>
                    </tr>
                </thead>
                <tbody>
                    {fee_rows_html}
                </tbody>
                <tfoot>
                    {summary_rows}
                </tfoot>
            </table>

            <div class="words-box">
                <b>Amount in Words:</b> {receipt.amount_in_words}
            </div>

            <div class="payment-box">
                {payment_info_str}
            </div>

            <table class="sig-table">
                <tr>
                    <td align="left" style="width: 50%;">
                        <br/><br/>
                        _________________________________<br/>
                        <b>Student / Parent Signature</b>
                    </td>
                    <td align="right" style="width: 50%;">
                        <br/><br/>
                        _________________________________<br/>
                        <b>Authorized Accounts Signatory</b>
                    </td>
                </tr>
            </table>
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
        self.setMinimumSize(680, 520)
        self.resize(780, 680)

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

        # Professional Interactive HTML Document Viewer
        if self.receipt:
            txt_view = QTextBrowser()
            txt_view.setReadOnly(True)
            txt_view.setStyleSheet("""
                QTextBrowser {
                    background-color: #f8fafc;
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                }
            """)
            html_content = generate_receipt_html(self.receipt)
            txt_view.setHtml(html_content)
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
