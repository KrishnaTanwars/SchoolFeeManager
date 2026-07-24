"""
Fee Categories & Fee Heads Master Management View with Zero-Clipping Action Buttons.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from controllers.fee_controller import FeeController
from dialogs.fee_category_dialog import FeeCategoryDialog
from utils.helpers import format_currency

class FeeCategoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title Banner
        hdr_layout = QHBoxLayout()
        title_lbl = QLabel("Fee Heads & Categories Master Configuration")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a;")
        hdr_layout.addWidget(title_lbl)
        hdr_layout.addStretch()

        self.btn_add = QPushButton("🏷️  + Add New Fee Category / Head")
        self.btn_add.setFixedHeight(36)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_category)
        hdr_layout.addWidget(self.btn_add)

        layout.addLayout(hdr_layout)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Category Name", "Short Code", "Default Amount (₹)", "Status", "Description", "Actions"
        ])
        
        # Explicit section resize modes: data columns stretch, Actions column fixed to 140px
        header = self.table.horizontalHeader()
        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 140)

        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)
        self.load_categories()

    def load_categories(self):
        categories = FeeController.get_all_categories()
        self.table.setRowCount(len(categories))

        for row_idx, cat in enumerate(categories):
            self.table.setItem(row_idx, 0, QTableWidgetItem(cat.name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(cat.code or ""))
            self.table.setItem(row_idx, 2, QTableWidgetItem(format_currency(cat.default_amount)))
            self.table.setItem(row_idx, 3, QTableWidgetItem("Active" if cat.is_active else "Inactive"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(cat.description or ""))

            # Action button container with zero-clipping inline padding
            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(6)

            btn_edit = QPushButton("✏️ Edit Head")
            btn_edit.setFixedHeight(28)
            btn_edit.setMinimumWidth(110)
            btn_edit.setStyleSheet("background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; padding: 0px 6px; margin: 0px; min-height: 24px;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, c=cat: self.edit_category(c))

            act_layout.addWidget(btn_edit)
            self.table.setCellWidget(row_idx, 5, action_widget)

    def add_category(self):
        dlg = FeeCategoryDialog(self)
        if dlg.exec():
            self.load_categories()

    def edit_category(self, category):
        dlg = FeeCategoryDialog(self, category)
        if dlg.exec():
            self.load_categories()
