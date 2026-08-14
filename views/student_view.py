"""
Student Master Management View with Fixed Action Button Layout, Zero-Clipping Styling,
Current Active Session Defaulting, Session Filter beside Search, and Bulk Delete support.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt
from controllers.student_controller import StudentController
from controllers.settings_controller import SettingsController
from dialogs.student_dialog import StudentDialog
from dialogs.student_ledger_dialog import StudentFeeLedgerDialog
from services.export_service import ExportService
from services.session_service import session_manager
from utils.helpers import format_date
from utils.table_delegate import apply_responsive_table_formatting
from components.academic_filter_widget import AcademicFilterWidget
from dialogs.student_details_dialog import StudentDetailsDialog

class StudentView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_students = []
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

        # Integrated Academic Filter Widget (Course, Branch, Year, Semester)
        self.academic_filter = AcademicFilterWidget(self, show_all_option=True, include_session=False)
        self.academic_filter.filters_changed.connect(self.load_students)
        layout.addWidget(self.academic_filter)

        # Filter & Search Controls Bar (Search Box + Session Filter Beside Search + Status Filter)
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(36)
        self.txt_search.setPlaceholderText("🔍 Search by Adm No, Student Name, Course, Branch, Semester, Mobile...")
        self.txt_search.textChanged.connect(self.load_students)

        lbl_session = QLabel("Session:")
        lbl_session.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px;")

        self.cmb_session = QComboBox()
        self.cmb_session.setFixedHeight(36)
        self.cmb_session.setMinimumWidth(130)
        self.cmb_session.currentIndexChanged.connect(self.load_students)

        lbl_status = QLabel("Status:")
        lbl_status.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px;")

        self.cmb_status_filter = QComboBox()
        self.cmb_status_filter.setFixedHeight(36)
        self.cmb_status_filter.addItems(["Active Only", "All Status", "Inactive Only"])
        self.cmb_status_filter.currentIndexChanged.connect(self.load_students)

        filter_layout.addWidget(self.txt_search, stretch=4)
        filter_layout.addWidget(lbl_session)
        filter_layout.addWidget(self.cmb_session, stretch=2)
        filter_layout.addWidget(lbl_status)
        filter_layout.addWidget(self.cmb_status_filter, stretch=1)
        layout.addLayout(filter_layout)

        # Bulk Operations Action Bar
        bulk_layout = QHBoxLayout()
        bulk_layout.setSpacing(8)

        self.btn_select_all = QPushButton("☑ Select All")
        self.btn_select_all.setCursor(Qt.PointingHandCursor)
        self.btn_select_all.setProperty("class", "SecondaryBtn")
        self.btn_select_all.setFixedHeight(32)
        self.btn_select_all.clicked.connect(self.select_all_students)

        self.btn_deselect_all = QPushButton("☐ Deselect All")
        self.btn_deselect_all.setCursor(Qt.PointingHandCursor)
        self.btn_deselect_all.setProperty("class", "SecondaryBtn")
        self.btn_deselect_all.setFixedHeight(32)
        self.btn_deselect_all.clicked.connect(self.deselect_all_students)

        self.btn_delete_selected = QPushButton("🗑️ Delete Selected")
        self.btn_delete_selected.setCursor(Qt.PointingHandCursor)
        self.btn_delete_selected.setFixedHeight(32)
        self.btn_delete_selected.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; padding: 0 12px;")
        self.btn_delete_selected.clicked.connect(self.delete_selected_students)

        self.lbl_selected_count = QLabel("Selected: 0")
        self.lbl_selected_count.setStyleSheet("font-weight: 700; color: #475569; font-size: 13px; margin-left: 8px;")

        bulk_layout.addWidget(self.btn_select_all)
        bulk_layout.addWidget(self.btn_deselect_all)
        bulk_layout.addWidget(self.btn_delete_selected)
        bulk_layout.addWidget(self.lbl_selected_count)
        bulk_layout.addStretch()
        layout.addLayout(bulk_layout)

        # ERP Student Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "☐", "Admission No.", "Student Name", "Course / Branch", "Year / Semester",
            "Session", "Status", "Actions"
        ])
        
        self.table.setWordWrap(True)
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        header.setSectionResizeMode(0, QHeaderView.Fixed)           # Checkbox Column
        self.table.setColumnWidth(0, 38)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Admission No.
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Student Name
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Course / Branch
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Year / Semester
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Session
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(7, QHeaderView.Fixed)           # Actions
        self.table.setColumnWidth(7, 160)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemDoubleClicked.connect(self.on_row_double_clicked)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_section_clicked)
        self.table.itemChanged.connect(self.on_item_changed)
        apply_responsive_table_formatting(self.table)

        layout.addWidget(self.table)

        # Connect to Centralized Active Session Manager
        session_manager.session_changed.connect(self.on_active_session_changed)

        self.populate_filters()
        self.load_students()

    def populate_filters(self):
        self.cmb_session.blockSignals(True)
        self.cmb_session.clear()

        sessions = SettingsController.get_academic_sessions()
        session_names = [s.session_name for s in sessions] if sessions else ["2024-2025", "2025-2026", "2026-2027"]

        active_session = session_manager.get_active_session()
        if active_session and active_session not in session_names:
            session_names.insert(0, active_session)

        # Order: Active session first, followed by other sessions, then "All Sessions"
        ordered_sessions = [active_session] + [s for s in session_names if s != active_session] + ["All Sessions"]
        self.cmb_session.addItems(ordered_sessions)
        self.cmb_session.setCurrentText(active_session)
        self.cmb_session.blockSignals(False)

    def on_active_session_changed(self, new_session: str):
        """Called when Active Academic Session changes globally in Settings."""
        self.populate_filters()
        self.load_students()

    def load_students(self):
        self.table.blockSignals(True)
        search = self.txt_search.text().strip()
        academic_filters = self.academic_filter.get_filter_values()
        status_idx = self.cmb_status_filter.currentIndex()

        status = "Active" if status_idx == 0 else ("All" if status_idx == 1 else "Inactive")

        selected_sess = self.cmb_session.currentText().strip()
        session_filter_val = "All" if selected_sess == "All Sessions" else selected_sess

        self.current_students = StudentController.get_all_students(
            search_query=search if search else "",
            class_filter="All",
            section_filter="All",
            session_filter=session_filter_val,
            status_filter=status,
            course_filter=academic_filters.get("course") or "All",
            branch_filter=academic_filters.get("branch") or "All",
            year_filter=academic_filters.get("year") or "All",
            semester_filter=academic_filters.get("semester") or "All"
        )

        self.table.setRowCount(len(self.current_students))

        for row_idx, s in enumerate(self.current_students):
            # Checkbox item
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, s)
            self.table.setItem(row_idx, 0, chk_item)

            # Admission No item
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

            # Compact Icon Actions Container (👁️, 💰, ✏️, 🗑️)
            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(3)

            btn_view = QPushButton("👁️")
            btn_view.setFixedSize(30, 28)
            btn_view.setToolTip("View Complete Student Record")
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

            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(30, 28)
            btn_del.setToolTip("Delete Student (Requires Admin Password)")
            btn_del.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; border-radius: 4px; border: none;")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, st=s: self.delete_student(st))

            act_layout.addWidget(btn_view)
            act_layout.addWidget(btn_ledger)
            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_del)
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

        headers = ["Admission No", "Roll No", "Student Name", "Class", "Section", "Father Name", "Mother Name", "Mobile", "Address", "Date of Admission", "Session", "Status"]

        if action in (act_filter_csv, act_filter_excel, act_filter_pdf):
            students = self.current_students
            title = "Student Directory (Filtered)"
        else:
            students = StudentController.get_all_students(status_filter="All")
            title = "Student Directory (Entire Database)"

        rows = [
            [s.admission_no, s.roll_no or "", s.name, s.class_name, s.section or "", s.father_name, s.mother_name or "", s.mobile, s.address or "", format_date(s.admission_date), s.academic_session, s.status]
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
        if path:
            success, msg = ExportService.export_data_by_format(title, headers, rows, fmt, filename_prefix="Students", output_path=path)
            if success:
                QMessageBox.information(self, "Export Successful", f"Exported {len(students)} student records to:\n{msg}")
            else:
                QMessageBox.critical(self, "Export Error", msg)
