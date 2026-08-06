"""
Fee Collection & Receipt Generation Form View with Dynamic Payment Mode Fields & Flexible Partial Payments.
"""

from typing import Dict, List, Optional
from datetime import date, datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDoubleSpinBox,
    QGroupBox, QFormLayout, QMessageBox, QCheckBox, QTextEdit, QCompleter, QDateEdit
)
from PySide6.QtCore import Qt, QStringListModel, QDate
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from controllers.settings_controller import SettingsController
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog
from utils.helpers import format_currency, format_date
from utils.number_to_words import number_to_words_indian

COMMON_INDIAN_BANKS = [
    "State Bank of India (SBI)",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Punjab National Bank (PNB)",
    "Bank of Baroda",
    "Kotak Mahindra Bank",
    "Canara Bank",
    "Union Bank of India",
    "IDFC FIRST Bank",
    "IndusInd Bank",
    "Other Bank"
]

class ReceiptView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_student = None
        self._user_edited_paid = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Header
        hdr = QHBoxLayout()
        title_lbl = QLabel("Fee Collection & Receipt Generation")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e3a8a;")
        hdr.addWidget(title_lbl)
        hdr.addStretch()

        self.lbl_next_rec = QLabel("Next Receipt No: <b>Auto</b>")
        self.lbl_next_rec.setStyleSheet("font-size: 13px; color: #475569;")
        hdr.addWidget(self.lbl_next_rec)

        layout.addLayout(hdr)

        # Main Split: Left (Student Search & Info), Right (Fee Particulars & Payment)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(15)

        # ---------------- LEFT COLUMN: Student Selection ----------------
        left_box = QGroupBox("1. Select Student")
        left_layout = QVBoxLayout(left_box)

        # Student Search Box
        lbl_search = QLabel("Search Student (Name / Adm No / Phone):")
        self.txt_student_search = QLineEdit()
        self.txt_student_search.setPlaceholderText("Type student name or admission number...")
        self.txt_student_search.textChanged.connect(self.search_students)

        left_layout.addWidget(lbl_search)
        left_layout.addWidget(self.txt_student_search)

        # Student List Combo/Select
        self.cmb_students = QComboBox()
        self.cmb_students.currentIndexChanged.connect(self.on_student_selected)
        left_layout.addWidget(self.cmb_students)

        # Student Details Card
        self.card_student = QGroupBox("Student Profile Summary")
        card_form = QFormLayout(self.card_student)
        
        self.lbl_adm_no = QLabel("-")
        self.lbl_name = QLabel("-")
        self.lbl_class = QLabel("-")
        self.lbl_father = QLabel("-")
        self.lbl_mobile = QLabel("-")
        self.lbl_session = QLabel("-")
        self.lbl_total_paid = QLabel("₹ 0.00")
        self.lbl_total_paid.setStyleSheet("font-weight: bold; color: #059669;")
        self.lbl_prev_due = QLabel("₹ 0.00")
        self.lbl_prev_due.setStyleSheet("font-weight: bold; color: #dc2626;")

        for lbl in [self.lbl_adm_no, self.lbl_name, self.lbl_class, self.lbl_father, self.lbl_mobile, self.lbl_session]:
            lbl.setStyleSheet("font-weight: bold; color: #0f172a;")

        card_form.addRow("Admission No:", self.lbl_adm_no)
        card_form.addRow("Student Name:", self.lbl_name)
        card_form.addRow("Class & Sec:", self.lbl_class)
        card_form.addRow("Father's Name:", self.lbl_father)
        card_form.addRow("Mobile No:", self.lbl_mobile)
        card_form.addRow("Session:", self.lbl_session)
        card_form.addRow("Total Paid Till Date:", self.lbl_total_paid)
        card_form.addRow("Previous Due:", self.lbl_prev_due)

        left_layout.addWidget(self.card_student)
        left_layout.addStretch()

        split_layout.addWidget(left_box, stretch=1)

        # ---------------- RIGHT COLUMN: Fee Particulars & Totals ----------------
        right_box = QGroupBox("2. Fee Heads Particulars & Flexible Payment")
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(12, 10, 12, 10)
        right_layout.setSpacing(8)

        # Fee Heads Table (Guaranteed 240px height so all Fee Heads are fully visible!)
        self.table_fees = QTableWidget()
        self.table_fees.setColumnCount(4)
        self.table_fees.setHorizontalHeaderLabels(["Select", "Fee Head Name", "Course", "Amount (₹)"])
        self.table_fees.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_fees.verticalHeader().setDefaultSectionSize(32)
        self.table_fees.setMinimumHeight(240)

        right_layout.addWidget(self.table_fees, stretch=2)

        # Bottom 2-Column Layout: Totals (Left) & Payment Mode / Action (Right)
        bottom_h_layout = QHBoxLayout()
        bottom_h_layout.setSpacing(15)

        # Left Column: Fee Totals Form
        totals_form = QFormLayout()
        totals_form.setContentsMargins(0, 0, 0, 0)
        totals_form.setSpacing(6)

        self.lbl_subtotal = QLabel("₹ 0.00")
        self.lbl_subtotal.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        totals_form.addRow("Subtotal:", self.lbl_subtotal)

        self.spn_discount = QDoubleSpinBox()
        self.spn_discount.setRange(0.0, 100000.0)
        self.spn_discount.setPrefix("₹ ")
        self.spn_discount.setDecimals(2)
        self.spn_discount.valueChanged.connect(self.recalculate_totals)
        totals_form.addRow("Discount (-):", self.spn_discount)

        self.spn_fine = QDoubleSpinBox()
        self.spn_fine.setRange(0.0, 50000.0)
        self.spn_fine.setPrefix("₹ ")
        self.spn_fine.setDecimals(2)
        self.spn_fine.valueChanged.connect(self.recalculate_totals)
        totals_form.addRow("Fine / Penalty (+):", self.spn_fine)

        self.lbl_total = QLabel("₹ 0.00")
        self.lbl_total.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e3a8a;")
        totals_form.addRow("Total Calculated Fee:", self.lbl_total)

        self.spn_paid_amount = QDoubleSpinBox()
        self.spn_paid_amount.setRange(0.0, 500000.0)
        self.spn_paid_amount.setPrefix("₹ ")
        self.spn_paid_amount.setDecimals(2)
        self.spn_paid_amount.setStyleSheet("font-size: 14px; font-weight: bold; color: #059669;")
        self.spn_paid_amount.valueChanged.connect(self.on_paid_amount_edited)
        totals_form.addRow("<b>ACTUAL PAID AMOUNT:</b>", self.spn_paid_amount)

        self.lbl_due_amount = QLabel("₹ 0.00")
        self.lbl_due_amount.setStyleSheet("font-size: 14px; font-weight: bold; color: #dc2626;")
        totals_form.addRow("<b>Remaining Due:</b>", self.lbl_due_amount)

        self.lbl_words = QLabel("Zero Rupees Only")
        self.lbl_words.setStyleSheet("font-size: 11px; font-weight: bold; color: #475569; font-style: italic;")
        self.lbl_words.setWordWrap(True)
        totals_form.addRow("Amount in Words:", self.lbl_words)

        bottom_h_layout.addLayout(totals_form, stretch=1)

        # Right Column: Payment Mode & Dynamic Fields
        pay_box = QVBoxLayout()
        pay_box.setContentsMargins(0, 0, 0, 0)
        pay_box.setSpacing(6)

        pay_form = QFormLayout()
        pay_form.setContentsMargins(0, 0, 0, 0)
        pay_form.setSpacing(6)

        self.cmb_pay_mode = QComboBox()
        self.cmb_pay_mode.addItems(["Cash", "UPI / QR", "Cheque", "Demand Draft (DD)", "Net Banking / NEFT"])
        self.cmb_pay_mode.currentIndexChanged.connect(self.update_payment_mode_fields)
        pay_form.addRow("Payment Mode:", self.cmb_pay_mode)

        self.txt_utr_no = QLineEdit()
        self.txt_utr_no.setPlaceholderText("Enter 12-digit UPI UTR / Transaction No")
        self.lbl_utr_no = QLabel("UTR Number:")

        self.txt_cheque_no = QLineEdit()
        self.txt_cheque_no.setPlaceholderText("Enter 6-digit Cheque / DD Number")
        self.lbl_cheque_no = QLabel("Cheque / DD Number:")

        self.dt_cheque_date = QDateEdit()
        self.dt_cheque_date.setCalendarPopup(True)
        self.dt_cheque_date.setDate(QDate.currentDate())
        self.lbl_cheque_date = QLabel("Cheque Date:")

        self.cmb_bank_name = QComboBox()
        self.cmb_bank_name.setEditable(True)
        self.cmb_bank_name.addItems(COMMON_INDIAN_BANKS)
        self.lbl_bank_name = QLabel("Bank Name:")

        self.dt_payment_date = QDateEdit()
        self.dt_payment_date.setCalendarPopup(True)
        self.dt_payment_date.setDate(QDate.currentDate())
        self.lbl_payment_date = QLabel("Payment Date:")

        self.txt_ref_no = QLineEdit()
        self.txt_ref_no.setPlaceholderText("Optional reference no.")
        self.lbl_ref_no = QLabel("Reference No:")

        pay_form.addRow(self.lbl_utr_no, self.txt_utr_no)
        pay_form.addRow(self.lbl_cheque_no, self.txt_cheque_no)
        pay_form.addRow(self.lbl_cheque_date, self.dt_cheque_date)
        pay_form.addRow(self.lbl_bank_name, self.cmb_bank_name)
        pay_form.addRow(self.lbl_payment_date, self.dt_payment_date)
        pay_form.addRow(self.lbl_ref_no, self.txt_ref_no)

        self.txt_remarks = QLineEdit()
        self.txt_remarks.setPlaceholderText("Optional fee remarks")
        pay_form.addRow("Remarks:", self.txt_remarks)

        pay_box.addLayout(pay_form)

        self.btn_generate = QPushButton("GENERATE & PRINT RECEIPT")
        self.btn_generate.setFixedHeight(42)
        self.btn_generate.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.btn_generate.setProperty("class", "SuccessBtn")
        self.btn_generate.clicked.connect(self.generate_receipt)

        pay_box.addWidget(self.btn_generate)

        bottom_h_layout.addLayout(pay_box, stretch=1)

        right_layout.addLayout(bottom_h_layout, stretch=1)

        split_layout.addWidget(right_box, stretch=2)
        layout.addLayout(split_layout)

        self.update_payment_mode_fields()
        self.refresh_view()

    def update_payment_mode_fields(self):
        mode = self.cmb_pay_mode.currentText().upper()

        # Hide all by default
        self.lbl_utr_no.hide()
        self.txt_utr_no.hide()
        self.lbl_cheque_no.hide()
        self.txt_cheque_no.hide()
        self.lbl_cheque_date.hide()
        self.dt_cheque_date.hide()
        self.lbl_bank_name.hide()
        self.cmb_bank_name.hide()
        self.lbl_payment_date.hide()
        self.dt_payment_date.hide()
        self.lbl_ref_no.hide()
        self.txt_ref_no.hide()

        if "CASH" in mode:
            # Cash: Keep all dynamic fields hidden
            pass
        elif "UPI" in mode or "QR" in mode:
            self.lbl_utr_no.setText("UTR Number:")
            self.txt_utr_no.setPlaceholderText("Enter 12-digit UPI UTR / Transaction No")
            self.lbl_utr_no.show()
            self.txt_utr_no.show()
            self.lbl_bank_name.show()
            self.cmb_bank_name.show()
            self.lbl_payment_date.show()
            self.dt_payment_date.show()
        elif "CHEQUE" in mode or "DD" in mode or "DEMAND" in mode:
            self.lbl_cheque_no.setText("Cheque / DD Number:")
            self.lbl_cheque_no.show()
            self.txt_cheque_no.show()
            self.lbl_cheque_date.show()
            self.dt_cheque_date.show()
            self.lbl_bank_name.show()
            self.cmb_bank_name.show()
        elif "NET" in mode or "NEFT" in mode:
            self.lbl_utr_no.setText("Transaction / Ref No:")
            self.txt_utr_no.setPlaceholderText("Enter NEFT / IMPS / Ref Number")
            self.lbl_utr_no.show()
            self.txt_utr_no.show()
            self.lbl_bank_name.show()
            self.cmb_bank_name.show()
            self.lbl_payment_date.show()
            self.dt_payment_date.show()
        else:
            self.lbl_ref_no.show()
            self.txt_ref_no.show()

    def refresh_view(self):
        self.lbl_next_rec.setText(f"Next Receipt No: <b>{ReceiptController.generate_next_receipt_number()}</b>")
        self.search_students()
        self.load_fee_heads()

    def search_students(self):
        query = self.txt_student_search.text().strip()
        students = StudentController.get_all_students(search_query=query, status_filter="Active")
        self.cmb_students.blockSignals(True)
        self.cmb_students.clear()

        if not students:
            self.cmb_students.addItem("-- No Active Students Found --", None)
            self.clear_student_card()
        else:
            for s in students:
                display_str = f"{s.name} | Adm: {s.admission_no} | Class: {s.class_name} ({s.section or 'A'}) | Phone: {s.mobile}"
                self.cmb_students.addItem(display_str, s)

        self.cmb_students.blockSignals(False)
        self.on_student_selected()

    def on_student_selected(self):
        s = self.cmb_students.currentData()
        self.selected_student = s
        if s:
            self.lbl_adm_no.setText(s.admission_no)
            self.lbl_name.setText(s.name)
            self.lbl_class.setText(f"{s.class_name} ({s.section or 'A'})")
            self.lbl_father.setText(s.father_name)
            self.lbl_mobile.setText(s.mobile)
            self.lbl_session.setText(s.academic_session)

            # Query student fee summary (Total Paid Till Date & Outstanding Due)
            summary = ReceiptController.get_student_fee_summary(s.id)
            self.lbl_total_paid.setText(format_currency(summary['total_paid']))
            self.lbl_prev_due.setText(format_currency(summary['latest_due']))
        else:
            self.clear_student_card()

        # Reload Fee Heads filtered by Student's Course
        self.load_fee_heads()

    def clear_student_card(self):
        self.selected_student = None
        self.lbl_adm_no.setText("-")
        self.lbl_name.setText("-")
        self.lbl_class.setText("-")
        self.lbl_father.setText("-")
        self.lbl_mobile.setText("-")
        self.lbl_session.setText("-")
        self.lbl_total_paid.setText("₹ 0.00")
        self.lbl_prev_due.setText("₹ 0.00")
        self.load_fee_heads()

    def load_fee_heads(self):
        course_filter = "All"
        if self.selected_student and getattr(self.selected_student, "course", None):
            st_course = str(self.selected_student.course).strip().upper()
            if "PG" in st_course or "POST" in st_course or "M.SC" in st_course or "M.A" in st_course or "M.COM" in st_course:
                course_filter = "PG"
            elif "UG" in st_course or "UNDER" in st_course or "B.SC" in st_course or "B.A" in st_course or "B.COM" in st_course or "B.CA" in st_course:
                course_filter = "UG"

        categories = FeeController.get_all_categories(active_only=True, course_filter=course_filter)
        self.table_fees.setRowCount(len(categories))

        for row_idx, cat in enumerate(categories):
            chk = QCheckBox()
            chk.stateChanged.connect(self.recalculate_totals)
            chk.setProperty("cat_data", cat)

            self.table_fees.setCellWidget(row_idx, 0, chk)
            self.table_fees.setItem(row_idx, 1, QTableWidgetItem(cat.name))
            self.table_fees.setItem(row_idx, 2, QTableWidgetItem(getattr(cat, "course", "UG")))

            spn_amt = QDoubleSpinBox()
            spn_amt.setRange(0.0, 500000.0)
            spn_amt.setValue(cat.default_amount)
            spn_amt.setPrefix("₹ ")
            spn_amt.valueChanged.connect(self.recalculate_totals)

            self.table_fees.setCellWidget(row_idx, 3, spn_amt)

        self._user_edited_paid = False
        self.recalculate_totals()

    def on_paid_amount_edited(self):
        self._user_edited_paid = True
        self.calculate_due()

    def calculate_due(self):
        subtotal = 0.0
        for r in range(self.table_fees.rowCount()):
            chk = self.table_fees.cellWidget(r, 0)
            spn_amt = self.table_fees.cellWidget(r, 3)
            if chk and chk.isChecked() and spn_amt:
                subtotal += spn_amt.value()

        discount = self.spn_discount.value()
        fine = self.spn_fine.value()
        grand_total = max(0.0, subtotal - discount + fine)

        paid_val = self.spn_paid_amount.value()
        due_val = max(0.0, grand_total - paid_val)

        self.lbl_due_amount.setText(format_currency(due_val))
        self.lbl_words.setText(number_to_words_indian(paid_val))

    def recalculate_totals(self):
        subtotal = 0.0
        for r in range(self.table_fees.rowCount()):
            chk = self.table_fees.cellWidget(r, 0)
            spn_amt = self.table_fees.cellWidget(r, 3)
            if chk and chk.isChecked() and spn_amt:
                subtotal += spn_amt.value()

        discount = self.spn_discount.value()
        fine = self.spn_fine.value()
        grand_total = max(0.0, subtotal - discount + fine)

        self.lbl_subtotal.setText(format_currency(subtotal))
        self.lbl_total.setText(format_currency(grand_total))

        if not self._user_edited_paid:
            self.spn_paid_amount.blockSignals(True)
            self.spn_paid_amount.setValue(grand_total)
            self.spn_paid_amount.blockSignals(False)

        self.calculate_due()

    def generate_receipt(self):
        if not self.selected_student:
            QMessageBox.warning(self, "Validation Error", "Please select a student first.")
            return

        selected_items = []
        for r in range(self.table_fees.rowCount()):
            chk = self.table_fees.cellWidget(r, 0)
            spn_amt = self.table_fees.cellWidget(r, 3)
            if chk and chk.isChecked() and spn_amt:
                cat = chk.property("cat_data")
                selected_items.append({
                    "fee_category_id": cat.id,
                    "category_name": cat.name,
                    "amount": spn_amt.value()
                })

        if not selected_items:
            QMessageBox.warning(self, "Validation Error", "Please check at least one fee head category.")
            return

        session_info = SettingsController.get_school_info()
        current_session = session_info.current_session if session_info else "2024-2025"

        # Date values
        q_cq_date = self.dt_cheque_date.date()
        cq_date = date(q_cq_date.year(), q_cq_date.month(), q_cq_date.day())

        q_pay_date = self.dt_payment_date.date()
        pay_date = date(q_pay_date.year(), q_pay_date.month(), q_pay_date.day())

        success, msg, receipt = ReceiptController.create_receipt(
            student_id=self.selected_student.id,
            academic_session=current_session,
            items=selected_items,
            discount_amount=self.spn_discount.value(),
            fine_amount=self.spn_fine.value(),
            payment_mode=self.cmb_pay_mode.currentText(),
            reference_no=self.txt_ref_no.text().strip(),
            remarks=self.txt_remarks.text().strip(),
            paid_amount=self.spn_paid_amount.value(),
            utr_number=self.txt_utr_no.text().strip(),
            cheque_number=self.txt_cheque_no.text().strip(),
            cheque_date=cq_date,
            bank_name=self.cmb_bank_name.currentText().strip(),
            payment_date=pay_date
        )

        if success and receipt:
            QMessageBox.information(self, "Success", msg)

            # Reset fields
            self.spn_discount.setValue(0.0)
            self.spn_fine.setValue(0.0)
            self.txt_utr_no.clear()
            self.txt_cheque_no.clear()
            self.txt_ref_no.clear()
            self.txt_remarks.clear()
            self._user_edited_paid = False
            self.refresh_view()

            # Open Print Preview Dialog
            dlg = ReceiptPreviewDialog(self, receipt)
            dlg.exec()
        else:
            QMessageBox.critical(self, "Error", msg)
