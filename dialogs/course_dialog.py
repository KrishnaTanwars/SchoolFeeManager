"""
Add / Edit Course & Degree Program Dialog with Detailed Program Attributes.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QTextEdit, QTabWidget, QWidget
)
from PySide6.QtCore import Qt
from controllers.academic_controller import AcademicController

class CourseDialog(QDialog):
    def __init__(self, parent=None, course_data=None):
        super().__init__(parent)
        self.course_data = course_data  # If present, edit mode
        self.is_edit = course_data is not None

        if self.is_edit:
            self.setWindowTitle(f"Edit Course Program Master: {course_data.name}")
        else:
            self.setWindowTitle("Add New Academic Course / Degree Program Master")

        self.setMinimumSize(540, 440)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # Tab Widget for Organizing All Program Details
        self.tabs = QTabWidget()

        # --- TAB 1: BASIC & ACADEMIC STRUCTURE ---
        tab_basic = QWidget()
        layout_basic = QVBoxLayout(tab_basic)
        grp_basic = QGroupBox("Core Program Specifications")
        form_basic = QFormLayout(grp_basic)
        form_basic.setSpacing(10)

        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("e.g. BPHARM, BTECH, MBA, DPHARM")
        if self.is_edit:
            self.txt_code.setText(self.course_data.code or "")
        form_basic.addRow("Course Code *:", self.txt_code)

        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. B. Pharmacy (Bachelor of Pharmacy)")
        if self.is_edit:
            self.txt_name.setText(self.course_data.name or "")
        form_basic.addRow("Course Name *:", self.txt_name)

        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["UG", "PG", "Diploma", "Doctorate", "Certificate", "College", "School", "Institute"])
        if self.is_edit and getattr(self.course_data, "course_type", None):
            idx = self.cmb_type.findText(self.course_data.course_type)
            if idx >= 0:
                self.cmb_type.setCurrentIndex(idx)
        form_basic.addRow("Course Category / Type:", self.cmb_type)

        self.txt_department = QLineEdit()
        self.txt_department.setPlaceholderText("e.g. Department of Pharmaceutical Sciences")
        if self.is_edit:
            self.txt_department.setText(getattr(self.course_data, "department", "") or "")
        form_basic.addRow("Department / Faculty:", self.txt_department)

        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(1, 10)
        self.spin_duration.setValue(3)
        if self.is_edit:
            self.spin_duration.setValue(getattr(self.course_data, "duration_years", 3) or 3)
        form_basic.addRow("Duration (Years):", self.spin_duration)

        self.spin_semesters = QSpinBox()
        self.spin_semesters.setRange(0, 20)
        self.spin_semesters.setValue(6)
        if self.is_edit:
            self.spin_semesters.setValue(getattr(self.course_data, "total_semesters", 6) or 6)
        form_basic.addRow("Total Semesters:", self.spin_semesters)

        layout_basic.addWidget(grp_basic)
        self.tabs.addTab(tab_basic, "🎓 Basic & Structure")

        # --- TAB 2: ACCREDITATION, QUALIFICATION & FEES ---
        tab_accred = QWidget()
        layout_accred = QVBoxLayout(tab_accred)
        grp_accred = QGroupBox("Degree, Accreditation & Fee Baseline")
        form_accred = QFormLayout(grp_accred)
        form_accred.setSpacing(10)

        self.txt_degree = QLineEdit()
        self.txt_degree.setPlaceholderText("e.g. Bachelor of Pharmacy (B.Pharm)")
        if self.is_edit:
            self.txt_degree.setText(getattr(self.course_data, "degree_awarded", "") or "")
        form_accred.addRow("Degree / Qualification:", self.txt_degree)

        self.txt_affiliation = QLineEdit()
        self.txt_affiliation.setPlaceholderText("e.g. PCI & AICTE Approved / UGC Recognized")
        if self.is_edit:
            self.txt_affiliation.setText(getattr(self.course_data, "affiliation", "") or "")
        form_accred.addRow("Affiliation / Board:", self.txt_affiliation)

        self.txt_eligibility = QLineEdit()
        self.txt_eligibility.setPlaceholderText("e.g. 10+2 with PCB/PCM minimum 50% marks")
        if self.is_edit:
            self.txt_eligibility.setText(getattr(self.course_data, "eligibility_criteria", "") or "")
        form_accred.addRow("Eligibility Criteria:", self.txt_eligibility)

        self.spin_fee = QDoubleSpinBox()
        self.spin_fee.setRange(0, 10000000)
        self.spin_fee.setDecimals(2)
        self.spin_fee.setPrefix("₹ ")
        self.spin_fee.setSingleStep(5000)
        if self.is_edit:
            self.spin_fee.setValue(getattr(self.course_data, "baseline_annual_fee", 0.0) or 0.0)
        form_accred.addRow("Baseline Annual Fee:", self.spin_fee)

        layout_accred.addWidget(grp_accred)
        self.tabs.addTab(tab_accred, "📜 Accreditation & Fee")

        # --- TAB 3: OVERVIEW & DESCRIPTION ---
        tab_desc = QWidget()
        layout_desc = QVBoxLayout(tab_desc)
        grp_desc = QGroupBox("Program Overview & Syllabus Notes")
        vbox_desc = QVBoxLayout(grp_desc)

        self.txt_desc = QTextEdit()
        self.txt_desc.setPlaceholderText("Enter detailed course description, objectives, career opportunities, and syllabus notes...")
        if self.is_edit:
            self.txt_desc.setPlainText(getattr(self.course_data, "description", "") or "")
        vbox_desc.addWidget(self.txt_desc)

        layout_desc.addWidget(grp_desc)
        self.tabs.addTab(tab_desc, "📝 Overview & Notes")

        main_layout.addWidget(self.tabs)

        # Buttons Bar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save Course Program")
        self.btn_save.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
        self.btn_save.clicked.connect(self.save_course)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def save_course(self):
        code = self.txt_code.text().strip()
        name = self.txt_name.text().strip()
        c_type = self.cmb_type.currentText()
        duration = self.spin_duration.value()
        semesters = self.spin_semesters.value()
        department = self.txt_department.text().strip()
        degree = self.txt_degree.text().strip()
        affiliation = self.txt_affiliation.text().strip()
        eligibility = self.txt_eligibility.text().strip()
        fee = self.spin_fee.value()
        desc = self.txt_desc.toPlainText().strip()

        if not code:
            QMessageBox.warning(self, "Validation Error", "Course Code is required.")
            self.tabs.setCurrentIndex(0)
            self.txt_code.setFocus()
            return
        if not name:
            QMessageBox.warning(self, "Validation Error", "Course Name is required.")
            self.tabs.setCurrentIndex(0)
            self.txt_name.setFocus()
            return

        if self.is_edit:
            success, msg = AcademicController.update_course(
                self.course_data.id,
                code=code,
                name=name,
                course_type=c_type,
                duration_years=duration,
                total_semesters=semesters,
                department=department,
                degree_awarded=degree,
                affiliation=affiliation,
                eligibility_criteria=eligibility,
                baseline_annual_fee=fee,
                description=desc
            )
        else:
            success, msg = AcademicController.add_course(
                code=code,
                name=name,
                course_type=c_type,
                duration_years=duration,
                total_semesters=semesters,
                department=department,
                degree_awarded=degree,
                affiliation=affiliation,
                eligibility_criteria=eligibility,
                baseline_annual_fee=fee,
                description=desc
            )

        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
