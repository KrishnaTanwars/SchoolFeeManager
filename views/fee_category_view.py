"""
Fee Categories & Fee Heads Master Management View with Zero-Clipping Action Buttons.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from controllers.fee_controller import FeeController
from dialogs.fee_category_dialog import FeeCategoryDialog
from utils.helpers import format_currency, format_date
from utils.table_delegate import apply_responsive_table_formatting

class FeeCategoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header Title Banner
        hdr_layout = QHBoxLayout()
        title_lbl = QLabel("Fee Heads Master Configuration")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a;")
        hdr_layout.addWidget(title_lbl)
        hdr_layout.addStretch()

        self.btn_add = QPushButton("🏷️  + Register New Fee Head")
        self.btn_add.setFixedHeight(36)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_category)
        hdr_layout.addWidget(self.btn_add)

        layout.addLayout(hdr_layout)

        # Filter & Instant Search Toolbar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(36)
        self.txt_search.setPlaceholderText("🔍 Search Fee Head Description, Course (UG/PG), Status...")
        self.txt_search.textChanged.connect(self.load_categories)

        self.cmb_course_filter = QComboBox()
        self.cmb_course_filter.setFixedHeight(36)
        self.cmb_course_filter.addItems(["All Courses", "UG", "PG"])
        self.cmb_course_filter.currentIndexChanged.connect(self.load_categories)

        self.cmb_status_filter = QComboBox()
        self.cmb_status_filter.setFixedHeight(36)
        self.cmb_status_filter.addItems(["Active Only", "All Status", "Inactive Only"])
        self.cmb_status_filter.currentIndexChanged.connect(self.load_categories)

        filter_layout.addWidget(self.txt_search, stretch=4)
        filter_layout.addWidget(self.cmb_course_filter, stretch=1)
        filter_layout.addWidget(self.cmb_status_filter, stretch=1)

        layout.addLayout(filter_layout)

        # Table Widget (6 Columns)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Description / Fee Head", "Course", "Default Amount (₹)", "Status", "Created Date", "Actions"
        ])
        
        # Responsive Header Resize Allocation
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)          # Description
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Course
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Amount
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Created Date
        header.setSectionResizeMode(5, QHeaderView.Fixed)           # Actions
        self.table.setColumnWidth(5, 160)

        self.table.setAlternatingRowColors(True)
        apply_responsive_table_formatting(self.table)

        layout.addWidget(self.table)
        self.load_categories()

    def load_categories(self):
        search = self.txt_search.text().strip()
        course_val = self.cmb_course_filter.currentText()
        if course_val == "All Courses":
            course_val = "All"
        status_idx = self.cmb_status_filter.currentIndex()
        active_only = True if status_idx == 0 else False

        categories = FeeController.get_all_categories(
            active_only=active_only,
            course_filter=course_val,
            search_query=search
        )
        self.table.setRowCount(len(categories))

        for row_idx, cat in enumerate(categories):
            self.table.setItem(row_idx, 0, QTableWidgetItem(cat.name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(getattr(cat, "course", "UG")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(format_currency(cat.default_amount)))
            self.table.setItem(row_idx, 3, QTableWidgetItem("Active" if cat.is_active else "Inactive"))
            created_str = format_date(cat.created_at) if getattr(cat, "created_at", None) else "N/A"
            self.table.setItem(row_idx, 4, QTableWidgetItem(created_str))

            # Action button container
            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(4)

            btn_edit = QPushButton("✏️ Edit")
            btn_edit.setFixedHeight(28)
            btn_edit.setMinimumWidth(65)
            btn_edit.setStyleSheet("background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; padding: 0px 6px;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, c=cat: self.edit_category(c))

            btn_del = QPushButton("🗑️ Delete")
            btn_del.setFixedHeight(28)
            btn_del.setMinimumWidth(65)
            btn_del.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; padding: 0px 6px;")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, c=cat: self.delete_category(c))

            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_del)
            self.table.setCellWidget(row_idx, 5, action_widget)

    def add_category(self):
        dlg = FeeCategoryDialog(self)
        if dlg.exec():
            self.load_categories()

    def edit_category(self, category):
        dlg = FeeCategoryDialog(self, category)
        if dlg.exec():
            self.load_categories()

    def delete_category(self, category):
        from dialogs.admin_auth_dialog import AdminAuthDialog
        auth_dlg = AdminAuthDialog(
            self,
            action_title="Fee Head Delete Protection",
            action_context=f"Delete Fee Head: '{category.name}' ({getattr(category, 'course', 'UG')})",
            module="Fee Heads"
        )
        if not auth_dlg.exec():
            return

        reply = QMessageBox.question(
            self, "Confirm Delete Fee Head",
            f"Are you sure you want to delete fee head '{category.name}' ({getattr(category, 'course', 'UG')})?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = FeeController.delete_category(category.id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_categories()
            else:
                QMessageBox.critical(self, "Error", msg)
