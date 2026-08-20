"""
Course Program Details Viewer Dialog — Displays complete metadata and attributes of a program.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QFormLayout, QTextEdit, QFrame, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from dialogs.course_dialog import CourseDialog

class CourseDetailsDialog(QDialog):
    def __init__(self, parent=None, course_data=None):
        super().__init__(parent)
        self.course_data = course_data
        self.setWindowTitle(f"Course Program Master Details — {course_data.name if course_data else ''}")
        self.setMinimumSize(560, 500)
        self.setup_ui()

    def setup_ui(self):
        if not self.course_data:
            return

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Header Frame
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #1e3a8a; border-radius: 6px; padding: 12px;")
        hdr_layout = QHBoxLayout(hdr_frame)

        v_hdr = QVBoxLayout()
        lbl_title = QLabel(f"🎓 {self.course_data.name}")
        lbl_title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 800;")
        lbl_sub = QLabel(f"Code: {self.course_data.code} | Category: {self.course_data.course_type or 'UG'} | Status: {'Active' if self.course_data.is_active else 'Inactive'}")
        lbl_sub.setStyleSheet("color: #93c5fd; font-size: 12px; font-weight: 600;")
        v_hdr.addWidget(lbl_title)
        v_hdr.addWidget(lbl_sub)

        hdr_layout.addLayout(v_hdr, stretch=1)
        main_layout.addWidget(hdr_frame)

        # Scroll Container for Details
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 1. Academic Specifications Box
        grp_spec = QGroupBox("1. Academic Specifications")
        grp_spec.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        form_spec = QFormLayout(grp_spec)
        form_spec.setSpacing(8)

        form_spec.addRow("Course Code:", self._make_val_label(self.course_data.code))
        form_spec.addRow("Course Full Name:", self._make_val_label(self.course_data.name))
        form_spec.addRow("Category / Level:", self._make_val_label(self.course_data.course_type or "UG"))
        form_spec.addRow("Department / Faculty:", self._make_val_label(getattr(self.course_data, "department", "General") or "General"))
        form_spec.addRow("Program Duration:", self._make_val_label(f"{self.course_data.duration_years} Years"))
        form_spec.addRow("Semester Structure:", self._make_val_label(f"{self.course_data.total_semesters} Semesters"))
        layout.addWidget(grp_spec)

        # 2. Accreditation & Fees Box
        grp_acc = QGroupBox("2. Qualification, Accreditation & Fees")
        grp_acc.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        form_acc = QFormLayout(grp_acc)
        form_acc.setSpacing(8)

        form_acc.addRow("Degree Awarded:", self._make_val_label(getattr(self.course_data, "degree_awarded", "-") or "Not Specified"))
        form_acc.addRow("Board / Affiliation:", self._make_val_label(getattr(self.course_data, "affiliation", "-") or "Not Specified"))
        form_acc.addRow("Eligibility Criteria:", self._make_val_label(getattr(self.course_data, "eligibility_criteria", "-") or "Not Specified"))
        
        fee_val = getattr(self.course_data, "baseline_annual_fee", 0.0) or 0.0
        fee_str = f"₹ {fee_val:,.2f}" if fee_val > 0 else "Default System Rate"
        form_acc.addRow("Baseline Annual Fee:", self._make_val_label(fee_str, bold=True, color="#059669"))

        layout.addWidget(grp_acc)

        # 3. Overview & Description Box
        grp_desc = QGroupBox("3. Program Overview & Syllabus Notes")
        grp_desc.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        vbox_d = QVBoxLayout(grp_desc)

        txt_desc = QTextEdit()
        txt_desc.setReadOnly(True)
        desc_content = getattr(self.course_data, "description", "") or "No detailed description provided."
        txt_desc.setPlainText(desc_content)
        txt_desc.setMaximumHeight(100)
        vbox_d.addWidget(txt_desc)
        layout.addWidget(grp_desc)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_edit = QPushButton("✏ Edit Program Details")
        self.btn_edit.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;")
        self.btn_edit.clicked.connect(self.edit_program)

        self.btn_delete = QPushButton("🗑 Delete Program")
        self.btn_delete.setStyleSheet("background-color: #dc2626; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_program)

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_close)
        main_layout.addLayout(btn_layout)

    def _make_val_label(self, text: str, bold: bool = False, color: str = "#1e293b") -> QLabel:
        lbl = QLabel(str(text))
        style = f"font-size: 13px; color: {color};"
        if bold:
            style += " font-weight: bold;"
        lbl.setStyleSheet(style)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        return lbl

    def edit_program(self):
        dlg = CourseDialog(self, course_data=self.course_data)
        if dlg.exec():
            self.accept()

    def delete_program(self):
        from PySide6.QtWidgets import QMessageBox
        from controllers.academic_controller import AcademicController
        reply = QMessageBox.question(
            self, "Confirm Delete Course",
            f"Are you sure you want to permanently delete course program '{self.course_data.name}' ({self.course_data.code})?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = AcademicController.delete_course(self.course_data.id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", msg)
