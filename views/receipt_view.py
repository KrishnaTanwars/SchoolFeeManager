"""
Fee Collection & Receipt Generation Form View.
"""

from typing import Dict, List, Optional
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDoubleSpinBox,
    QGroupBox, QFormLayout, QMessageBox, QCheckBox, QTextEdit, QCompleter
)
from PySide6.QtCore import Qt, QStringListModel
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from controllers.settings_controller import SettingsController
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog
from utils.helpers import format_currency, format_date
from utils.number_to_words import number_to_words_indian

class ReceiptView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_student = None
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

        for lbl in [self.lbl_adm_no, self.lbl_name, self.lbl_class, self.lbl_father, self.lbl_mobile, self.lbl_session]:
            lbl.setStyleSheet("font-weight: bold; color: #0f172a;")

        card_form.addRow("Admission No:", self.lbl_adm_no)
        card_form.addRow("Student Name:", self.lbl_name)
        card_form.addRow("Class & Sec:", self.lbl_class)
        card_form.addRow("Father's Name:", self.lbl_father)
        card_form.addRow("Mobile No:", self.lbl_mobile)
        card_form.addRow("Session:", self.lbl_session)

        left_layout.addWidget(self.card_student)
        left_layout.addStretch()

        split_layout.addWidget(left_box, stretch=1)

        # ---------------- RIGHT COLUMN: Fee Particulars & Totals ----------------
        right_box = QGroupBox("2. Fee Heads Particulars & Payment")
        right_layout = QVBoxLayout(right_box)

        # Fee Heads Table
        self.table_fees = QTableWidget()
        self.table_fees.setColumnCount(4)
        self.table_fees.setHorizontalHeaderLabels(["Select", "Fee Head Name", "Code", "Amount (₹)"])
        self.table_fees.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        right_layout.addWidget(self.table_fees)

        # Payment & Summary Form
        summary_form = QFormLayout()

        # Subtotal
        self.lbl_subtotal = QLabel("₹ 0.00")
        self.lbl_subtotal.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        summary_form.addRow("Subtotal:", self.lbl_subtotal)

        # Discount
        self.spn_discount = QDoubleSpinBox()
        self.spn_discount.setRange(0.0, 100000.0)
        self.spn_discount.setPrefix("₹ ")
        self.spn_discount.setDecimals(2)
        self.spn_discount.valueChanged.connect(self.recalculate_totals)
        summary_form.addRow("Discount (-):", self.spn_discount)

        # Fine
        self.spn_fine = QDoubleSpinBox()
        self.spn_fine.setRange(0.0, 50000.0)
        self.spn_fine.setPrefix("₹ ")
        self.spn_fine.setDecimals(2)
        self.spn_fine.valueChanged.connect(self.recalculate_totals)
        summary_form.addRow("Fine / Penalty (+):", self.spn_fine)

        # Grand Total
        self.lbl_total = QLabel("₹ 0.00")
        self.lbl_total.setStyleSheet("font-size: 18px; font-weight: bold; color: #10b981;")
        summary_form.addRow("<b>TOTAL AMOUNT:</b>", self.lbl_total)

        # Amount in Words
        self.lbl_words = QLabel("Zero Rupees Only")
        self.lbl_words.setStyleSheet("font-size: 11px; font-weight: bold; color: #475569; font-style: italic;")
        self.lbl_words.setWordWrap(True)
        summary_form.addRow("Amount in Words:", self.lbl_words)

        # Payment Mode & Ref
        pay_layout = QHBoxLayout()
        self.cmb_pay_mode = QComboBox()
        self.cmb_pay_mode.addItems(["Cash", "UPI / QR", "Cheque", "Demand Draft (DD)", "Net Banking / NEFT"])
        self.txt_ref_no = QLineEdit()
        self.txt_ref_no.setPlaceholderText("Ref/Cheque/Transaction No.")
        pay_layout.addWidget(self.cmb_pay_mode, stretch=1)
        pay_layout.addWidget(self.txt_ref_no, stretch=2)
        summary_form.addRow("Payment Mode & Ref:", pay_layout)

        # Remarks
        self.txt_remarks = QLineEdit()
        self.txt_remarks.setPlaceholderText("Optional fee remarks")
        summary_form.addRow("Remarks:", self.txt_remarks)

        right_layout.addLayout(summary_form)

        # Action Button
        self.btn_generate = QPushButton("GENERATE & PRINT RECEIPT")
        self.btn_generate.setFixedHeight(45)
        self.btn_generate.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.btn_generate.setProperty("class", "SuccessBtn")
        self.btn_generate.clicked.connect(self.generate_receipt)

        right_layout.addWidget(self.btn_generate)

        split_layout.addWidget(right_box, stretch=2)
        layout.addLayout(split_layout)

        self.refresh_view()

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
        else:
            self.clear_student_card()

    def clear_student_card(self):
        self.selected_student = None
        self.lbl_adm_no.setText("-")
        self.lbl_name.setText("-")
        self.lbl_class.setText("-")
        self.lbl_father.setText("-")
        self.lbl_mobile.setText("-")
        self.lbl_session.setText("-")

    def load_fee_heads(self):
        categories = FeeController.get_all_categories(active_only=True)
        self.table_fees.setRowCount(len(categories))

        for row_idx, cat in enumerate(categories):
            chk = QCheckBox()
            chk.stateChanged.connect(self.recalculate_totals)
            chk.setProperty("cat_data", cat)

            self.table_fees.setCellWidget(row_idx, 0, chk)
            self.table_fees.setItem(row_idx, 1, QTableWidgetItem(cat.name))
            self.table_fees.setItem(row_idx, 2, QTableWidgetItem(cat.code or ""))

            spn_amt = QDoubleSpinBox()
            spn_amt.setRange(0.0, 500000.0)
            spn_amt.setValue(cat.default_amount)
            spn_amt.setPrefix("₹ ")
            spn_amt.valueChanged.connect(self.recalculate_totals)

            self.table_fees.setCellWidget(row_idx, 3, spn_amt)

        self.recalculate_totals()

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
        self.lbl_words.setText(number_to_words_indian(grand_total))

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

        success, msg, receipt = ReceiptController.create_receipt(
            student_id=self.selected_student.id,
            academic_session=current_session,
            items=selected_items,
            discount_amount=self.spn_discount.value(),
            fine_amount=self.spn_fine.value(),
            payment_mode=self.cmb_pay_mode.currentText(),
            reference_no=self.txt_ref_no.text().strip(),
            remarks=self.txt_remarks.text().strip()
        )

        if success and receipt:
            QMessageBox.information(self, "Success", msg)

            # Reset fields
            self.spn_discount.setValue(0.0)
            self.spn_fine.setValue(0.0)
            self.txt_ref_no.clear()
            self.txt_remarks.clear()
            self.refresh_view()

            # Open Print Preview Dialog
            dlg = ReceiptPreviewDialog(self, receipt)
            dlg.exec()
        else:
            QMessageBox.critical(self, "Error", msg)
