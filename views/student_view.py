"""
Student Master Management View with Fixed Action Button Layout and Zero-Clipping Styling.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog
)
from PySide6.QtCore import Qt
from controllers.student_controller import StudentController
from dialogs.student_dialog import StudentDialog
from dialogs.student_ledger_dialog import StudentFeeLedgerDialog
from services.export_service import ExportService
from utils.helpers import format_date
from utils.table_delegate import apply_responsive_table_formatting
from components.academic_filter_widget import AcademicFilterWidget
from dialogs.student_details_dialog import StudentDetailsDialog

class StudentView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header Title Banner
        hdr_layout = QHBoxLayout()
        title_lbl = QLabel("Student Directory & Academic Structure")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a;")
        hdr_layout.addWidget(title_lbl)
        hdr_layout.addStretch()

        self.btn_sample = QPushButton("📄 Sample CSV")
        self.btn_sample.setProperty("class", "SecondaryBtn")
        self.btn_sample.setCursor(Qt.PointingHandCursor)
        self.btn_sample.clicked.connect(self.download_sample_csv)

        self.btn_import = QPushButton("📤 Import CSV")
        self.btn_import.setProperty("class", "SecondaryBtn")
        self.btn_import.setCursor(Qt.PointingHandCursor)
        self.btn_import.clicked.connect(self.import_csv)

        self.btn_export = QPushButton("📥 Export CSV")
        self.btn_export.setProperty("class", "SecondaryBtn")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_csv)

        self.btn_add_student = QPushButton("➕ Register New Student")
        self.btn_add_student.setFixedHeight(36)
        self.btn_add_student.setCursor(Qt.PointingHandCursor)
        self.btn_add_student.clicked.connect(self.add_student)

        hdr_layout.addWidget(self.btn_sample)
        hdr_layout.addWidget(self.btn_import)
        hdr_layout.addWidget(self.btn_export)
        hdr_layout.addWidget(self.btn_add_student)
        layout.addLayout(hdr_layout)

        # Integrated Academic Filter Widget
        self.academic_filter = AcademicFilterWidget(self, show_all_option=True, include_session=True)
        self.academic_filter.filters_changed.connect(self.load_students)
        layout.addWidget(self.academic_filter)

        # Filter & Search Controls Bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(36)
        self.txt_search.setPlaceholderText("🔍 Search by Adm No, Student Name, Aadhaar, Course, Branch, Mobile...")
        self.txt_search.textChanged.connect(self.load_students)

        self.cmb_status_filter = QComboBox()
        self.cmb_status_filter.setFixedHeight(36)
        self.cmb_status_filter.addItems(["Active Only", "All Status", "Inactive Only"])
        self.cmb_status_filter.currentIndexChanged.connect(self.load_students)

        self.lbl_selected_count = QLabel("Selected: 0")
        self.lbl_selected_count.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px; margin-left: 10px;")

        self.btn_promote = QPushButton("🎓 Promote Student(s)")
        self.btn_promote.setFixedHeight(36)
        self.btn_promote.setStyleSheet("background-color: #1e3a8a; color: #ffffff; font-weight: bold; padding: 0 12px; border-radius: 4px;")
        self.btn_promote.setCursor(Qt.PointingHandCursor)
        self.btn_promote.clicked.connect(self.promote_selected_students)

        self.btn_bulk_delete = QPushButton("🗑️ Delete Selected")
        self.btn_bulk_delete.setFixedHeight(36)
        self.btn_bulk_delete.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; padding: 0 12px; border-radius: 4px;")
        self.btn_bulk_delete.setCursor(Qt.PointingHandCursor)
        self.btn_bulk_delete.clicked.connect(self.delete_selected_students)

        filter_layout.addWidget(self.txt_search, stretch=3)
        filter_layout.addWidget(self.cmb_status_filter, stretch=1)
        filter_layout.addWidget(self.lbl_selected_count)
        filter_layout.addWidget(self.btn_promote)
        filter_layout.addWidget(self.btn_bulk_delete)
        layout.addLayout(filter_layout)

        # ERP Student Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "☐", "Admission / Enrollment No.", "Student Name", "Course / Branch",
            "Year / Semester", "Session", "Status", "Actions"
        ])
        
        self.table.setWordWrap(True)
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.sectionClicked.connect(self.on_header_section_clicked)
        
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Adm No
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Name
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Course/Branch
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Yr/Sem
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Session
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(7, QHeaderView.Fixed)           # Actions
        self.table.setColumnWidth(7, 120)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.itemDoubleClicked.connect(self.on_row_double_clicked)
        apply_responsive_table_formatting(self.table)

        layout.addWidget(self.table)

        self.populate_filters()
        self.load_students()

    def populate_filters(self):
        pass

    def load_students(self):
        search = self.txt_search.text().strip()
        academic_filters = self.academic_filter.get_filter_values()
        status_idx = self.cmb_status_filter.currentIndex()

        status = "Active" if status_idx == 0 else ("All" if status_idx == 1 else "Inactive")

        self.current_students = StudentController.get_all_students(
            search_query=search if search else "",
            class_filter="All",
            section_filter="All",
            session_filter=academic_filters.get("session") or "All",
            status_filter=status,
            course_filter=academic_filters.get("course") or "All",
            branch_filter=academic_filters.get("branch") or "All",
            year_filter=academic_filters.get("year") or "All",
            semester_filter=academic_filters.get("semester") or "All"
        )

        self.table.blockSignals(True)
        self.table.setRowCount(len(self.current_students))

        for row_idx, s in enumerate(self.current_students):
            # Column 0: Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, s)
            self.table.setItem(row_idx, 0, chk_item)

            # Column 1: Admission No
            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setData(Qt.UserRole, s)
            self.table.setItem(row_idx, 1, item_adm)
            self.table.setItem(row_idx, 2, QTableWidgetItem(s.name))
            
            course_branch = s.course or "General"
            if getattr(s, "branch", None):
                course_branch += f" ({s.branch})"
            self.table.setItem(row_idx, 3, QTableWidgetItem(course_branch))

            yr_sem_parts = []
            if getattr(s, "year", None):
                yr_sem_parts.append(s.year)
            if getattr(s, "semester", None):
                yr_sem_parts.append(s.semester)
            yr_sem_str = " - ".join(yr_sem_parts) if yr_sem_parts else "N/A"
            self.table.setItem(row_idx, 4, QTableWidgetItem(yr_sem_str))

            self.table.setItem(row_idx, 5, QTableWidgetItem(s.academic_session))
            self.table.setItem(row_idx, 6, QTableWidgetItem(s.status))

            # Compact Actions Widget (View, Ledger, Edit - NO DELETE)
            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(3)

            btn_view = QPushButton("👁️")
            btn_view.setFixedSize(30, 28)
            btn_view.setToolTip("View Complete Student Profile")
            btn_view.setStyleSheet("background-color: #0f766e; color: #ffffff; font-weight: bold; border-radius: 4px; border: none;")
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.clicked.connect(lambda _, st=s: self.view_student_details(st))

            btn_ledger = QPushButton("💰")
            btn_ledger.setFixedSize(30, 28)
            btn_ledger.setToolTip("Fee Ledger & Collect Fee")
            btn_ledger.setStyleSheet("background-color: #1e3a8a; color: #ffffff; font-weight: bold; border-radius: 4px; border: none;")
            btn_ledger.setCursor(Qt.PointingHandCursor)
            btn_ledger.clicked.connect(lambda _, st=s: self.view_student_fee_summary(st))

            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 28)
            btn_edit.setToolTip("Edit Student Details")
            btn_edit.setStyleSheet("background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 4px; border: none;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, st=s: self.edit_student(st))

            act_layout.addWidget(btn_view)
            act_layout.addWidget(btn_ledger)
            act_layout.addWidget(btn_edit)
            self.table.setCellWidget(row_idx, 7, action_widget)

        self.table.blockSignals(False)
        self.update_selection_counter()
        self.update_header_checkbox_text(self.is_all_selected())

    def on_row_double_clicked(self, item):
        row = item.row()
        adm_item = self.table.item(row, 1)
        if adm_item:
            student = adm_item.data(Qt.UserRole)
            if student:
                self.view_student_details(student)

    def select_all_students(self):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Checked)
        self.table.blockSignals(False)
        self.update_header_checkbox_text(True)
        self.update_selection_counter()

    def deselect_all_students(self):
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
                self.deselect_all_students()
            else:
                self.select_all_students()

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
        selected_count = sum(
            1 for row in range(self.table.rowCount())
            if self.table.item(row, 0) and self.table.item(row, 0).checkState() == Qt.Checked
        )
        self.lbl_selected_count.setText(f"Selected: {selected_count}")

    def delete_selected_students(self):
        selected_students = []
        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.Checked:
                student = chk_item.data(Qt.UserRole)
                if student:
                    selected_students.append(student)

        if not selected_students:
            QMessageBox.warning(self, "No Selection", "No students selected.\nPlease select at least one student to delete.")
            return

        from dialogs.admin_auth_dialog import AdminAuthDialog
        count = len(selected_students)
        auth_dlg = AdminAuthDialog(
            self,
            action_title="Bulk Student Delete Protection",
            action_context=f"Bulk Delete {count} Selected Student(s)",
            module="Student Master"
        )
        if not auth_dlg.exec():
            return

        reply = QMessageBox.question(
            self,
            "Confirm Bulk Delete Students",
            f"Are you sure you want to delete {count} selected student(s)?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            student_ids = [s.id for s in selected_students]
            success, msg, deleted_count = StudentController.delete_students_bulk(student_ids)
            if success:
                QMessageBox.information(self, "Bulk Delete Success", msg)
                self.load_students()
            else:
                QMessageBox.critical(self, "Bulk Delete Error", msg)

    def view_student_details(self, student):
        dlg = StudentDetailsDialog(self, student)
        dlg.exec()

    def view_student_fee_summary(self, student):
        dlg = StudentFeeLedgerDialog(self, student)
        dlg.exec()

    def add_student(self):
        dlg = StudentDialog(self)
        if dlg.exec():
            self.populate_filters()
            self.load_students()

    def edit_student(self, student):
        dlg = StudentDialog(self, student)
        if dlg.exec():
            self.populate_filters()
            self.load_students()

    def delete_student(self, student):
        from dialogs.admin_auth_dialog import AdminAuthDialog
        auth_dlg = AdminAuthDialog(
            self,
            action_title="Student Delete Protection",
            action_context=f"Delete Student: '{student.name}' ({student.admission_no})",
            module="Student Master"
        )
        if not auth_dlg.exec():
            return

        reply = QMessageBox.question(
            self, "Confirm Delete Student",
            f"Are you sure you want to delete student '{student.name}' ({student.admission_no})?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = StudentController.delete_student(student.id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_students()
            else:
                QMessageBox.critical(self, "Error", msg)

    def download_sample_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Sample CSV Template", "sample_students_import.csv", "CSV Files (*.csv)")
        if path:
            success, msg = ExportService.generate_sample_student_csv(output_path=path)
            if success:
                QMessageBox.information(self, "Sample Template Saved", f"Sample CSV template saved successfully to:\n{path}\n\nYou can open this file in Excel to fill in student data for import.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to save sample CSV: {msg}")

    def import_csv(self):
        from dialogs.student_import_dialog import StudentImportDialog
        dlg = StudentImportDialog(self)
        if dlg.exec():
            self.populate_filters()
            self.load_students()

    def export_csv(self):
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QCursor

        menu = QMenu(self)
        act_filter_csv = menu.addAction("📥 Export Current Filtered List (CSV)")
        act_filter_excel = menu.addAction("📊 Export Current Filtered List (Excel)")
        act_filter_pdf = menu.addAction("📄 Export Current Filtered List (PDF)")
        menu.addSeparator()
        act_db_csv = menu.addAction("📥 Export Entire Database (CSV)")
        act_db_excel = menu.addAction("📊 Export Entire Database (Excel)")
        act_db_pdf = menu.addAction("📄 Export Entire Database (PDF)")

        action = menu.exec(QCursor.pos())
        if not action:
            return

        headers = ["Admission / Enrollment No", "Student Name", "Student Photo", "Date of Birth", "Class / Course", "Section", "Father Name", "Mother Name", "Mobile", "Aadhaar Number", "Address", "Date of Admission", "Session", "Status"]

        if action in (act_filter_csv, act_filter_excel, act_filter_pdf):
            students = self.current_students
            title = "Student Directory (Filtered)"
        else:
            students = StudentController.get_all_students(status_filter="All")
            title = "Student Directory (Entire Database)"

        rows = [
            [
                s.admission_no,
                s.name,
                getattr(s, "photo_path", None) or "",
                format_date(getattr(s, "date_of_birth", None)) if getattr(s, "date_of_birth", None) else "",
                s.class_name,
                s.section or "",
                s.father_name,
                s.mother_name or "",
                s.mobile,
                getattr(s, "aadhaar_number", None) or "",
                s.address or "",
                format_date(s.admission_date),
                s.academic_session,
                s.status
            ]
            for s in students
        ]

        if action in (act_filter_csv, act_db_csv):
            fmt = "csv"
            filter_str = "CSV Files (*.csv)"
        elif action in (act_filter_excel, act_db_excel):
            fmt = "excel"
            filter_str = "Excel Files (*.xlsx)"
        else:
            fmt = "pdf"
            filter_str = "PDF Files (*.pdf)"

        path, _ = QFileDialog.getSaveFileName(self, f"Save {title}", "", filter_str)
        if not path:
            return

        try:
            if fmt == "csv":
                ExportService.export_to_csv(headers, rows, path)
            elif fmt == "excel":
                ExportService.export_to_excel(headers, rows, path)
            else:
                PDFService.generate_table_pdf(title, headers, rows, path)
            QMessageBox.information(self, "Export Complete", f"Exported {len(rows)} records successfully:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export data: {e}")

    def promote_selected_students(self):
        """Opens PromotionDialog for checked or selected students."""
        selected_students = self.get_selected_students()
        if not selected_students:
            # Fallback to current row selection if no checkboxes checked
            curr_row = self.table.currentRow()
            if curr_row >= 0:
                item = self.table.item(curr_row, 1)
                if item:
                    st = item.data(Qt.UserRole)
                    if st:
                        selected_students = [st]

        if not selected_students:
            QMessageBox.warning(self, "Selection Required", "Please check or select 1 or more students to promote.")
            return

        from dialogs.promotion_dialog import PromotionDialog
        dlg = PromotionDialog(self, students=selected_students)
        if dlg.exec() == QDialog.Accepted:
            self.load_students()

