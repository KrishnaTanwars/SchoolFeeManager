"""
Fee Categories & Fee Heads Master Management View with Bulk Checkboxes, Select All/Deselect All, and Zero-Clipping Styling.
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
        self.cmb_course_filter.addItems(["All Courses", "UG (B. Pharmacy)", "PG (M. Pharmacy)"])
        self.cmb_course_filter.currentIndexChanged.connect(self.load_categories)

        self.cmb_status_filter = QComboBox()
        self.cmb_status_filter.setFixedHeight(36)
        self.cmb_status_filter.addItems(["Active Only", "All Status", "Inactive Only"])
        self.cmb_status_filter.currentIndexChanged.connect(self.load_categories)

        self.lbl_selected_count = QLabel("Selected: 0")
        self.lbl_selected_count.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px; margin-left: 8px;")

        self.btn_bulk_delete = QPushButton("🗑️ Delete Selected")
        self.btn_bulk_delete.setFixedHeight(36)
        self.btn_bulk_delete.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; padding: 0 12px; border-radius: 4px;")
        self.btn_bulk_delete.setCursor(Qt.PointingHandCursor)
        self.btn_bulk_delete.clicked.connect(self.delete_selected_categories)

        filter_layout.addWidget(self.txt_search, stretch=3)
        filter_layout.addWidget(self.cmb_course_filter, stretch=2)
        filter_layout.addWidget(self.cmb_status_filter, stretch=1)
        filter_layout.addWidget(self.lbl_selected_count)
        filter_layout.addWidget(self.btn_bulk_delete)

        layout.addLayout(filter_layout)

        # Table Widget (7 Columns: Checkbox, Name, Course, Amount, Status, Created Date, Actions)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "☐", "Description / Fee Head", "Course Category / Course", "Default Amount (₹)", "Status", "Created Date", "Actions"
        ])
        
        # Responsive Header Resize Allocation
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.sectionClicked.connect(self.on_header_section_clicked)

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Checkbox
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Description
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Course
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Amount
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Created Date
        header.setSectionResizeMode(6, QHeaderView.Fixed)           # Actions
        self.table.setColumnWidth(6, 80)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemChanged.connect(self.on_item_changed)
        apply_responsive_table_formatting(self.table)

        layout.addWidget(self.table)
        self.load_categories()

    def load_categories(self):
        search = self.txt_search.text().strip()
        selected_course = self.cmb_course_filter.currentText()
        if "UG" in selected_course:
            course_val = "UG"
        elif "PG" in selected_course:
            course_val = "PG"
        else:
            course_val = "All"

        status_idx = self.cmb_status_filter.currentIndex()
        active_only = True if status_idx == 0 else False

        self.current_categories = FeeController.get_all_categories(
            active_only=active_only,
            course_filter=course_val,
            search_query=search
        )

        self.table.blockSignals(True)
        self.table.setRowCount(len(self.current_categories))

        for row_idx, cat in enumerate(self.current_categories):
            # Column 0: Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, cat)
            self.table.setItem(row_idx, 0, chk_item)

            # Column 1: Fee Head Name
            self.table.setItem(row_idx, 1, QTableWidgetItem(cat.name))
            
            raw_crs = str(getattr(cat, "course", "UG") or "UG").strip()
            if raw_crs == "UG":
                disp_crs = "UG — B. Pharmacy"
            elif raw_crs == "PG":
                disp_crs = "PG — M. Pharmacy"
            else:
                disp_crs = "Shared (UG & PG)"

            self.table.setItem(row_idx, 2, QTableWidgetItem(disp_crs))
            self.table.setItem(row_idx, 3, QTableWidgetItem(format_currency(cat.default_amount)))
            self.table.setItem(row_idx, 4, QTableWidgetItem("Active" if cat.is_active else "Inactive"))
            created_str = format_date(cat.created_at) if getattr(cat, "created_at", None) else "N/A"
            self.table.setItem(row_idx, 5, QTableWidgetItem(created_str))

            # Column 6: Action button container (Edit only - NO Delete button)
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

            act_layout.addWidget(btn_edit)
            self.table.setCellWidget(row_idx, 6, action_widget)

        self.table.blockSignals(False)
        self.update_selection_counter()
        self.update_header_checkbox_text(self.is_all_selected())

    def get_selected_categories(self) -> list:
        """Returns list of FeeCategory objects currently checked in the table."""
        selected = []
        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.Checked:
                cat = chk_item.data(Qt.UserRole)
                if cat:
                    selected.append(cat)
        return selected

    def select_all_categories(self):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Checked)
        self.table.blockSignals(False)
        self.update_header_checkbox_text(True)
        self.update_selection_counter()

    def deselect_all_categories(self):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Unchecked)
        self.table.blockSignals(False)
        self.update_header_checkbox_text(False)
        self.update_selection_counter()

    def on_header_section_clicked(self, logical_index: int):
        if logical_index == 0:
            if self.is_all_selected():
                self.deselect_all_categories()
            else:
                self.select_all_categories()

    def is_all_selected(self) -> bool:
        count = self.table.rowCount()
        if count == 0:
            return False
        for row in range(count):
            item = self.table.item(row, 0)
            if not item or item.checkState() != Qt.Checked:
                return False
        return True

    def update_header_checkbox_text(self, checked: bool):
        hdr_item = self.table.horizontalHeaderItem(0)
        if hdr_item:
            hdr_item.setText("☑" if checked else "☐")

    def on_item_changed(self, item):
        if item.column() == 0:
            self.update_selection_counter()
            self.update_header_checkbox_text(self.is_all_selected())

    def update_selection_counter(self):
        selected_count = len(self.get_selected_categories())
        self.lbl_selected_count.setText(f"Selected: {selected_count}")

    def delete_selected_categories(self):
        selected_categories = self.get_selected_categories()
        if not selected_categories:
            QMessageBox.warning(self, "No Selection", "No fee heads selected.\nPlease select at least one fee head to delete.")
            return

        from dialogs.admin_auth_dialog import AdminAuthDialog
        count = len(selected_categories)
        auth_dlg = AdminAuthDialog(
            self,
            action_title="Bulk Fee Head Delete Protection",
            action_context=f"Bulk Delete {count} Selected Fee Head(s)",
            module="Fee Heads"
        )
        if not auth_dlg.exec():
            return

        reply = QMessageBox.question(
            self,
            "Confirm Bulk Delete Fee Heads",
            f"Are you sure you want to delete {count} selected fee head(s)?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            cat_ids = [c.id for c in selected_categories]
            success, msg, deleted_count = FeeController.delete_categories_bulk(cat_ids)
            if success:
                QMessageBox.information(self, "Bulk Delete Complete", msg)
                self.load_categories()
            else:
                QMessageBox.critical(self, "Bulk Delete Error", msg)

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
