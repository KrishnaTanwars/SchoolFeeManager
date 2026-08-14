"""
Global Search Overlay Dialog for EduLedger ERP v1.9.0.
Searches across Students, Receipts, Fee Heads, Reports, Admission Nos, Receipt Nos, and Mobile Nos.
Supports instant keyboard navigation (Ctrl+K).
"""

from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt

from config.database import get_db
from models.student import Student
from models.receipt import Receipt
from models.fee_category import FeeCategory
from utils.helpers import format_currency, format_date


class GlobalSearchDialog(QDialog):
    def __init__(self, parent=None, on_navigate_callback=None):
        super().__init__(parent)
        self.setWindowTitle("EduLedger Global Search (Ctrl+K)")
        self.setMinimumSize(500, 360)
        self.resize(700, 480)
        self.on_navigate_callback = on_navigate_callback
        self.results_data = []

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # Search Bar Box
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #ffffff; border: 2px solid #2563eb; border-radius: 8px; padding: 4px 8px;")
        hdr_layout = QHBoxLayout(hdr_frame)

        lbl_icon = QLabel("🔍")
        lbl_icon.setStyleSheet("font-size: 18px;")

        self.txt_query = QLineEdit()
        self.txt_query.setPlaceholderText("Search Students, Receipts, Fee Heads, Reports, Admission Nos, Mobile Nos...")
        self.txt_query.setStyleSheet("border: none; font-size: 14px; font-weight: 600; color: #0f172a;")
        self.txt_query.textChanged.connect(self.run_global_search)

        lbl_esc = QLabel("ESC to exit")
        lbl_esc.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold;")

        hdr_layout.addWidget(lbl_icon)
        hdr_layout.addWidget(self.txt_query, stretch=1)
        hdr_layout.addWidget(lbl_esc)

        main_layout.addWidget(hdr_frame)

        # Results List Widget
        self.list_results = QListWidget()
        self.list_results.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px 14px;
                border-bottom: 1px solid #f1f5f9;
            }
            QListWidget::item:hover {
                background-color: #eff6ff;
            }
            QListWidget::item:selected {
                background-color: #1e3a8a;
                color: #ffffff;
            }
        """)
        self.list_results.itemClicked.connect(self.on_item_selected)
        self.list_results.itemActivated.connect(self.on_item_selected)
        self.list_results.itemDoubleClicked.connect(self.on_item_selected)

        main_layout.addWidget(self.list_results)

        # Initial Search Load
        self.run_global_search()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            curr_item = self.list_results.currentItem()
            if curr_item:
                self.on_item_selected(curr_item)
        elif event.key() == Qt.Key_Down:
            if self.txt_query.hasFocus():
                if self.list_results.count() > 0:
                    self.list_results.setFocus()
                    self.list_results.setCurrentRow(0)
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Up:
            if self.list_results.hasFocus() and self.list_results.currentRow() <= 0:
                self.txt_query.setFocus()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def run_global_search(self):
        query = self.txt_query.text().strip().lower()
        self.list_results.clear()
        self.results_data.clear()

        db = get_db()
        try:
            # 1. Search Students (Max 8)
            sq = db.query(Student).filter(Student.status == "Active")
            if query:
                pattern = f"%{query}%"
                sq = sq.filter(
                    (Student.name.ilike(pattern)) |
                    (Student.admission_no.ilike(pattern)) |
                    (Student.roll_no.ilike(pattern)) |
                    (Student.mobile.ilike(pattern)) |
                    (Student.father_name.ilike(pattern)) |
                    (Student.class_name.ilike(pattern)) |
                    (Student.course.ilike(pattern)) |
                    (Student.branch.ilike(pattern)) |
                    (Student.semester.ilike(pattern))
                )
            students = sq.order_by(Student.name.asc()).limit(8).all()

            for s in students:
                c_info = f"{s.course or 'General'}"
                if getattr(s, "branch", None):
                    c_info += f" ({s.branch})"
                if getattr(s, "semester", None):
                    c_info += f" - {s.semester}"
                item_text = f"👤 Student: {s.name} | Adm No: {s.admission_no} | {c_info} | Mob: {s.mobile}"
                data = {"type": "student", "id": s.id, "target_view": "students", "title": s.name}
                
                l_item = QListWidgetItem(item_text)
                self.list_results.addItem(l_item)
                self.results_data.append(data)

            # 2. Search Receipts (Max 8)
            rq = db.query(Receipt).filter(Receipt.status == "Paid")
            if query:
                pattern = f"%{query}%"
                rq = rq.join(Student).filter(
                    (Receipt.receipt_no.ilike(pattern)) |
                    (Receipt.remarks.ilike(pattern)) |
                    (Receipt.payment_mode.ilike(pattern)) |
                    (Student.name.ilike(pattern)) |
                    (Student.admission_no.ilike(pattern))
                )
            receipts = rq.order_by(Receipt.receipt_date.desc()).limit(8).all()

            for r in receipts:
                st_name = r.student.name if r.student else "Student"
                item_text = f"📜 Receipt: {r.receipt_no} | Student: {st_name} | Date: {format_date(r.receipt_date)} | Paid: {format_currency(r.paid_amount or r.total_amount)} | Mode: {r.payment_mode}"
                data = {"type": "receipt", "id": r.id, "receipt_no": r.receipt_no, "target_view": "history"}

                l_item = QListWidgetItem(item_text)
                self.list_results.addItem(l_item)
                self.results_data.append(data)

            # 3. Search Fee Heads (Max 5)
            fq = db.query(FeeCategory)
            if query:
                pattern = f"%{query}%"
                fq = fq.filter(
                    (FeeCategory.name.ilike(pattern)) |
                    (FeeCategory.course.ilike(pattern))
                )
            categories = fq.order_by(FeeCategory.name.asc()).limit(5).all()

            for c in categories:
                item_text = f"🏷 Fee Head: {c.name} | Course: {c.course} | Default Amount: {format_currency(c.default_amount)}"
                data = {"type": "fee_head", "id": c.id, "target_view": "fees", "title": c.name}

                l_item = QListWidgetItem(item_text)
                self.list_results.addItem(l_item)
                self.results_data.append(data)

            # 4. Search Reports Shortcuts
            reports_shortcuts = [
                ("📊 Daily Collection Report", "daily", "reports"),
                ("🗓 Monthly Collection Report", "monthly", "reports"),
                ("🏫 Class-wise Collection Report", "class_wise", "reports"),
                ("⚠️ Outstanding Fee Report", "outstanding", "reports"),
                ("📖 Student Ledger Report", "ledger", "reports")
            ]
            for title, report_key, target in reports_shortcuts:
                if not query or query in title.lower() or query in report_key:
                    item_text = f"📈 Report: {title}"
                    data = {"type": "report", "report_key": report_key, "target_view": target}
                    l_item = QListWidgetItem(item_text)
                    self.list_results.addItem(l_item)
                    self.results_data.append(data)

            # Empty Results Fallback
            if self.list_results.count() == 0:
                empty_item = QListWidgetItem("⚠️ No matching records found.")
                empty_item.setFlags(Qt.NoItemFlags)
                empty_item.setForeground(Qt.gray)
                self.list_results.addItem(empty_item)

        finally:
            db.close()

    def on_item_selected(self, item: QListWidgetItem):
        row = self.list_results.row(item)
        if 0 <= row < len(self.results_data):
            data = self.results_data[row]
            if self.on_navigate_callback:
                self.on_navigate_callback(data)
            self.accept()
