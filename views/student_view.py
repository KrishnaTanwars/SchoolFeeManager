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

class StudentView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header Title Banner
        hdr_layout = QHBoxLayout()
        title_lbl = QLabel("Student Master Directory")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a;")
        hdr_layout.addWidget(title_lbl)
        hdr_layout.addStretch()

        self.btn_sample = QPushButton("📄  Download Sample CSV")
        self.btn_sample.setProperty("class", "SecondaryBtn")
        self.btn_sample.setCursor(Qt.PointingHandCursor)
        self.btn_sample.clicked.connect(self.download_sample_csv)

        self.btn_import = QPushButton("📤  Import Students")
        self.btn_import.setProperty("class", "SecondaryBtn")
        self.btn_import.setCursor(Qt.PointingHandCursor)
        self.btn_import.clicked.connect(self.import_csv)

        self.btn_export = QPushButton("📥  Export CSV")
        self.btn_export.setProperty("class", "SecondaryBtn")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_csv)

        self.btn_add_student = QPushButton("➕  Register New Student")
        self.btn_add_student.setFixedHeight(36)
        self.btn_add_student.setCursor(Qt.PointingHandCursor)
        self.btn_add_student.clicked.connect(self.add_student)

        hdr_layout.addWidget(self.btn_sample)
        hdr_layout.addWidget(self.btn_import)
        hdr_layout.addWidget(self.btn_export)
        hdr_layout.addWidget(self.btn_add_student)
        layout.addLayout(hdr_layout)

        # Filter & Search Controls Bar (Full Responsive Width)
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(36)
        self.txt_search.setPlaceholderText("🔍 Search by Name, Adm No, Roll No, Father/Mother Name, Mobile, Course...")
        self.txt_search.textChanged.connect(self.load_students)

        self.cmb_class_filter = QComboBox()
        self.cmb_class_filter.setFixedHeight(36)
        self.cmb_class_filter.addItem("All Classes", "All")
        self.cmb_class_filter.currentIndexChanged.connect(self.load_students)

        self.cmb_section_filter = QComboBox()
        self.cmb_section_filter.setFixedHeight(36)
        self.cmb_section_filter.addItem("All Sections", "All")
        self.cmb_section_filter.currentIndexChanged.connect(self.load_students)

        self.cmb_session_filter = QComboBox()
        self.cmb_session_filter.setFixedHeight(36)
        self.cmb_session_filter.addItem("All Sessions", "All")
        self.cmb_session_filter.currentIndexChanged.connect(self.load_students)

        self.cmb_status_filter = QComboBox()
        self.cmb_status_filter.setFixedHeight(36)
        self.cmb_status_filter.addItems(["Active Students Only", "All Students", "Inactive Only"])
        self.cmb_status_filter.currentIndexChanged.connect(self.load_students)

        filter_layout.addWidget(self.txt_search, stretch=4)
        filter_layout.addWidget(self.cmb_class_filter, stretch=1)
        filter_layout.addWidget(self.cmb_section_filter, stretch=1)
        filter_layout.addWidget(self.cmb_session_filter, stretch=1)
        filter_layout.addWidget(self.cmb_status_filter, stretch=1)

        layout.addLayout(filter_layout)

        # Full Width Professional Student Table
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Adm. No.", "Roll No.", "Student Name", "Course / Session",
            "Class", "Sec", "Father's Name", "Mother's Name", "Mobile No.",
            "Status", "Adm. Date", "Actions"
        ])
        
        # Responsive Section Resize Modes:
        # Text/String data columns stretch to fill space; fixed codes/numbers stay optimal
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Adm No
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Roll No
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Student Name
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Course/Session
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Class
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Section
        header.setSectionResizeMode(6, QHeaderView.Stretch)          # Father Name
        header.setSectionResizeMode(7, QHeaderView.Stretch)          # Mother Name
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents) # Mobile No
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)# Admission Date
        header.setSectionResizeMode(11, QHeaderView.Fixed)           # Actions
        self.table.setColumnWidth(11, 230)

        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        self.populate_filters()
        self.load_students()

    def populate_filters(self):
        self.cmb_class_filter.blockSignals(True)
        self.cmb_class_filter.clear()
        self.cmb_class_filter.addItem("All Classes", "All")
        classes = StudentController.get_distinct_classes()
        for c in classes:
            self.cmb_class_filter.addItem(c, c)
        self.cmb_class_filter.blockSignals(False)

        self.cmb_section_filter.blockSignals(True)
        self.cmb_section_filter.clear()
        self.cmb_section_filter.addItem("All Sections", "All")
        sections = StudentController.get_distinct_sections()
        for sec in sections:
            self.cmb_section_filter.addItem(f"Sec {sec}", sec)
        self.cmb_section_filter.blockSignals(False)

        self.cmb_session_filter.blockSignals(True)
        self.cmb_session_filter.clear()
        self.cmb_session_filter.addItem("All Sessions", "All")
        sessions = StudentController.get_distinct_sessions()
        for s in sessions:
            self.cmb_session_filter.addItem(s, s)
        self.cmb_session_filter.blockSignals(False)

    def load_students(self):
        search = self.txt_search.text().strip()
        class_val = self.cmb_class_filter.currentData() or "All"
        section_val = self.cmb_section_filter.currentData() or "All"
        session_val = self.cmb_session_filter.currentData() or "All"
        status_idx = self.cmb_status_filter.currentIndex()

        status = "Active" if status_idx == 0 else ("All" if status_idx == 1 else "Inactive")

        students = StudentController.get_all_students(
            search_query=search if search else "",
            class_filter=class_val,
            section_filter=section_val,
            session_filter=session_val,
            status_filter=status
        )

        self.table.setRowCount(len(students))

        for row_idx, s in enumerate(students):
            self.table.setItem(row_idx, 0, QTableWidgetItem(s.admission_no))
            self.table.setItem(row_idx, 1, QTableWidgetItem(s.roll_no or ""))
            self.table.setItem(row_idx, 2, QTableWidgetItem(s.name))
            course_sess = f"{s.course} ({s.academic_session})" if getattr(s, "course", None) else s.academic_session
            self.table.setItem(row_idx, 3, QTableWidgetItem(course_sess))
            self.table.setItem(row_idx, 4, QTableWidgetItem(s.class_name))
            self.table.setItem(row_idx, 5, QTableWidgetItem(s.section or "A"))
            self.table.setItem(row_idx, 6, QTableWidgetItem(s.father_name))
            self.table.setItem(row_idx, 7, QTableWidgetItem(s.mother_name or ""))
            self.table.setItem(row_idx, 8, QTableWidgetItem(s.mobile))
            self.table.setItem(row_idx, 9, QTableWidgetItem(s.status))
            self.table.setItem(row_idx, 10, QTableWidgetItem(format_date(s.admission_date)))

            # Action Buttons Container with zero-clipping inline padding
            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(4)

            btn_ledger = QPushButton("📜 Fee")
            btn_ledger.setFixedHeight(28)
            btn_ledger.setMinimumWidth(60)
            btn_ledger.setStyleSheet("background-color: #1e3a8a; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; padding: 0px 6px; margin: 0px; min-height: 24px;")
            btn_ledger.setCursor(Qt.PointingHandCursor)
            btn_ledger.clicked.connect(lambda _, st=s: self.view_student_fee_summary(st))

            btn_edit = QPushButton("✏️ Edit")
            btn_edit.setFixedHeight(28)
            btn_edit.setMinimumWidth(60)
            btn_edit.setStyleSheet("background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; padding: 0px 6px; margin: 0px; min-height: 24px;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, st=s: self.edit_student(st))

            btn_del = QPushButton("🗑️ Del")
            btn_del.setFixedHeight(28)
            btn_del.setMinimumWidth(60)
            btn_del.setStyleSheet("background-color: #dc2626; color: #ffffff; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; padding: 0px 6px; margin: 0px; min-height: 24px;")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, st=s: self.delete_student(st))

            act_layout.addWidget(btn_ledger)
            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_del)
            self.table.setCellWidget(row_idx, 11, action_widget)

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
        path, _ = QFileDialog.getOpenFileName(self, "Select Students CSV File to Import", "", "CSV Files (*.csv)")
        if path:
            result = StudentController.import_students_from_csv(path)
            if "error" in result:
                QMessageBox.critical(self, "Import Error", result["error"])
                return

            succ = result["success_count"]
            skip = result["skipped_count"]
            fail = result["failed_count"]
            tot = result["total_processed"]

            msg = f"=== CSV STUDENT IMPORT SUMMARY ===\n\n"
            msg += f"• Total Processed : {tot}\n"
            msg += f"• Successfully Added : {succ}\n"
            msg += f"• Skipped (Duplicates): {skip}\n"
            msg += f"• Failed Rows        : {fail}\n"

            if result["failed_rows"]:
                msg += f"\nFailure Details:\n" + "\n".join(result["failed_rows"][:10])
                if len(result["failed_rows"]) > 10:
                    msg += f"\n...and {len(result['failed_rows']) - 10} more."

            QMessageBox.information(self, "Import Completed", msg)
            self.populate_filters()
            self.load_students()

    def export_csv(self):
        headers = ["Admission No", "Roll No", "Student Name", "Class", "Section", "Father Name", "Mother Name", "Mobile", "Address", "Date of Admission", "Session", "Status"]
        students = StudentController.get_all_students()
        rows = [
            [s.admission_no, s.roll_no or "", s.name, s.class_name, s.section or "", s.father_name, s.mother_name or "", s.mobile, s.address or "", format_date(s.admission_date), s.academic_session, s.status]
            for s in students
        ]
        path, _ = QFileDialog.getSaveFileName(self, "Save Student Records CSV", "", "CSV Files (*.csv)")
        if path:
            success, msg = ExportService.export_to_csv(headers, rows, output_path=path)
            if success:
                QMessageBox.information(self, "Success", f"Exported {len(students)} student records to:\n{path}")
            else:
                QMessageBox.critical(self, "Export Error", msg)
