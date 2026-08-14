"""
Student Fee Payment Summary & Transaction History Ledger Dialog.
Displays total lifetime fee paid till date, outstanding due, and receipt list for a student.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QWidget, QFrame,
    QScrollArea
)
from PySide6.QtCore import Qt
from models.student import Student
from controllers.receipt_controller import ReceiptController
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog
from utils.helpers import format_currency, format_date
from utils.table_delegate import apply_responsive_table_formatting

class StudentFeeLedgerDialog(QDialog):
    def __init__(self, parent=None, student: Optional[Student] = None):
        super().__init__(parent)
        self.student = student
        self.setWindowTitle(f"Student Fee Payment History - {student.name if student else 'Ledger'}")
        self.setMinimumSize(550, 450)
        self.resize(750, 520)
        self.setup_ui()

    def setup_ui(self):
        dialog_vbox = QVBoxLayout(self)
        dialog_vbox.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        if not self.student:
            layout.addWidget(QLabel("No student selected."))
            scroll.setWidget(container)
            dialog_vbox.addWidget(scroll)
            return

        summary = ReceiptController.get_student_fee_summary(self.student.id)

        # Header Title
        title_lbl = QLabel(f"Fee Payment Summary & History for: <b>{self.student.name}</b>")
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet("font-size: 16px; color: #1e3a8a; font-weight: bold;")
        layout.addWidget(title_lbl)

        # KPI Summary Cards Layout
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)

        # 1. Total Paid Card
        card_paid = QFrame()
        card_paid.setStyleSheet("background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px;")
        v_paid = QVBoxLayout(card_paid)
        v_paid.setContentsMargins(8, 6, 8, 6)
        lbl_p_title = QLabel("TOTAL FEE PAID TILL DATE")
        lbl_p_title.setWordWrap(True)
        lbl_p_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #166534;")
        lbl_p_val = QLabel(format_currency(summary['total_paid']))
        lbl_p_val.setWordWrap(True)
        lbl_p_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #15803d;")
        v_paid.addWidget(lbl_p_title)
        v_paid.addWidget(lbl_p_val)

        # 2. Current Outstanding Due Card
        card_due = QFrame()
        card_due.setStyleSheet("background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 10px;")
        v_due = QVBoxLayout(card_due)
        v_due.setContentsMargins(8, 6, 8, 6)
        lbl_d_title = QLabel("CURRENT OUTSTANDING DUE")
        lbl_d_title.setWordWrap(True)
        lbl_d_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #991b1b;")
        lbl_d_val = QLabel(format_currency(summary['latest_due']))
        lbl_d_val.setWordWrap(True)
        lbl_d_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #b91c1c;")
        v_due.addWidget(lbl_d_title)
        v_due.addWidget(lbl_d_val)

        # 3. Total Receipts Count Card
        card_cnt = QFrame()
        card_cnt.setStyleSheet("background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 10px;")
        v_cnt = QVBoxLayout(card_cnt)
        v_cnt.setContentsMargins(8, 6, 8, 6)
        lbl_c_title = QLabel("TOTAL RECEIPTS ISSUED")
        lbl_c_title.setWordWrap(True)
        lbl_c_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #075985;")
        lbl_c_val = QLabel(f"{summary['receipts_count']} Receipts")
        lbl_c_val.setWordWrap(True)
        lbl_c_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #0369a1;")
        v_cnt.addWidget(lbl_c_title)
        v_cnt.addWidget(lbl_c_val)

        kpi_layout.addWidget(card_paid)
        kpi_layout.addWidget(card_due)
        kpi_layout.addWidget(card_cnt)
        layout.addLayout(kpi_layout)

        # Transactions History Table
        hist_group = QGroupBox("Payment Receipt Transactions History")
        hist_layout = QVBoxLayout(hist_group)
        hist_layout.setContentsMargins(8, 8, 8, 8)

        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Receipt No", "Date", "Total Fee", "Paid Amount", "Remaining Due", "Payment Mode", "Action"
        ])
        header = table.horizontalHeader()
        for col in range(6):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        table.setColumnWidth(6, 120)
        table.setAlternatingRowColors(True)
        apply_responsive_table_formatting(table)

        receipts = summary['receipts']
        table.setRowCount(len(receipts))

        for row_idx, r in enumerate(receipts):
            paid_amt = getattr(r, 'paid_amount', r.total_amount) or r.total_amount
            due_amt = getattr(r, 'due_amount', 0.0) or 0.0

            table.setItem(row_idx, 0, QTableWidgetItem(r.receipt_no))
            table.setItem(row_idx, 1, QTableWidgetItem(format_date(r.receipt_date)))
            table.setItem(row_idx, 2, QTableWidgetItem(format_currency(r.total_amount)))
            table.setItem(row_idx, 3, QTableWidgetItem(format_currency(paid_amt)))
            table.setItem(row_idx, 4, QTableWidgetItem(format_currency(due_amt)))
            table.setItem(row_idx, 5, QTableWidgetItem(r.payment_mode))

            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setAlignment(Qt.AlignCenter)

            btn_view = QPushButton("👁 View")
            btn_view.setFixedHeight(26)
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #1e3a8a;
                    color: white;
                    font-weight: bold;
                    border-radius: 4px;
                    border: none;
                    font-size: 11px;
                    padding: 2px 8px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.clicked.connect(lambda _, rec=r: self.view_receipt(rec))

            act_layout.addWidget(btn_view)
            table.setCellWidget(row_idx, 6, action_widget)

        hist_layout.addWidget(table)
        layout.addWidget(hist_group)

        # Close Button
        btn_close = QPushButton("Close")
        btn_close.setFixedHeight(34)
        btn_close.setStyleSheet("background-color: #64748b; color: white; font-weight: bold; border-radius: 5px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

        scroll.setWidget(container)
        dialog_vbox.addWidget(scroll)

    def view_receipt(self, receipt):
        dlg = ReceiptPreviewDialog(self, receipt)
        dlg.exec()
