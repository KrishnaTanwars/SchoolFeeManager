"""
Academic Promotion Dialog.
Allows administrators to preview and execute single or batch student promotions with Admin Password verification.
"""

from typing import List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame
)
from PySide6.QtCore import Qt

from models.student import Student
from services.promotion_service import PromotionService
from services.session_service import SessionManager
from controllers.academic_controller import AcademicController
from controllers.auth_controller import AuthController

class PromotionDialog(QDialog):
    def __init__(self, parent=None, students: List[Student] = None):
        super().__init__(parent)
        self.students = students or []
        self.setWindowTitle(f"Academic Promotion — {len(self.students)} Student(s) Selected")
        self.setMinimumSize(680, 520)
        self.resize(750, 580)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header Title Card
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px; padding: 12px;")
        hdr_box = QVBoxLayout(hdr_frame)
        
        lbl_title = QLabel(f"🎓 Academic Promotion Portal ({len(self.students)} Selected)")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #0369a1; border: none;")
        lbl_desc = QLabel("Promote selected students to the next Academic Session, Year, and Semester. All changes are verified and executed atomically.")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 12px; color: #0891b2; border: none;")
        
        hdr_box.addWidget(lbl_title)
        hdr_box.addWidget(lbl_desc)
        main_layout.addWidget(hdr_frame)

        # Target Stage Configuration Group Box
        grp_config = QGroupBox("Target Promotion Parameters")
        grp_config.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        f_config = QFormLayout(grp_config)
        f_config.setSpacing(10)

        # Populate Academic Sessions
        self.cmb_session = QComboBox()
        all_sessions = SessionManager.get_all_sessions()
        curr_sess = SessionManager.get_current_session()
        self.cmb_session.addItems(all_sessions)
        if "2026-2027" in all_sessions:
            self.cmb_session.setCurrentText("2026-2027")
        elif curr_sess in all_sessions:
            self.cmb_session.setCurrentText(curr_sess)

        # Populate Years
        self.cmb_year = QComboBox()
        self.cmb_year.addItems(["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"])

        # Populate Semesters
        self.cmb_sem = QComboBox()
        self.cmb_sem.addItems(["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8", "Completed"])

        # Calculate initial recommendation based on first student
        if self.students:
            s0 = self.students[0]
            rec_yr, rec_sem = PromotionService.calculate_next_stage(s0.course, s0.year, s0.semester)
            if self.cmb_year.findText(rec_yr) >= 0:
                self.cmb_year.setCurrentText(rec_yr)
            if self.cmb_sem.findText(rec_sem) >= 0:
                self.cmb_sem.setCurrentText(rec_sem)

        f_config.addRow("Target Academic Session:", self.cmb_session)
        f_config.addRow("Target Academic Year:", self.cmb_year)
        f_config.addRow("Target Semester:", self.cmb_sem)

        main_layout.addWidget(grp_config)

        # Connect signals for dynamic live preview table updates
        self.cmb_session.currentTextChanged.connect(self.update_preview_table)
        self.cmb_year.currentTextChanged.connect(self.update_preview_table)
        self.cmb_sem.currentTextChanged.connect(self.update_preview_table)

        # Preview Table Group Box
        grp_preview = QGroupBox("Promotion Live Preview")
        grp_preview.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        v_preview = QVBoxLayout(grp_preview)

        self.tbl_preview = QTableWidget()
        self.tbl_preview.setColumnCount(5)
        self.tbl_preview.setHorizontalHeaderLabels(["Adm No", "Student Name", "Course", "Current Stage", "Proposed Target Stage"])
        self.tbl_preview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_preview.verticalHeader().setVisible(False)
        self.tbl_preview.setStyleSheet("QTableWidget { background-color: #ffffff; border: 1px solid #e2e8f0; font-size: 11px; } QHeaderView::section { font-weight: bold; background-color: #f1f5f9; }")
        v_preview.addWidget(self.tbl_preview)

        main_layout.addWidget(grp_preview)

        # Security Authentication Box
        grp_auth = QGroupBox("Administrator Authentication")
        grp_auth.setStyleSheet("QGroupBox { font-weight: bold; color: #b91c1c; }")
        f_auth = QFormLayout(grp_auth)
        
        self.txt_admin_password = QLineEdit()
        self.txt_admin_password.setEchoMode(QLineEdit.Password)
        self.txt_admin_password.setPlaceholderText("Enter administrator password to confirm promotion")
        f_auth.addRow("Admin Password:", self.txt_admin_password)

        main_layout.addWidget(grp_auth)

        # Action Button Bar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedWidth(100)
        btn_cancel.setFixedHeight(34)
        btn_cancel.clicked.connect(self.reject)

        self.btn_confirm = QPushButton("🎓 Confirm & Apply Promotion")
        self.btn_confirm.setStyleSheet("background-color: #1e3a8a; color: white; font-weight: bold; border-radius: 4px; padding: 6px 16px;")
        self.btn_confirm.setFixedHeight(34)
        self.btn_confirm.setCursor(Qt.PointingHandCursor)
        self.btn_confirm.clicked.connect(self.execute_promotion)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_confirm)
        main_layout.addLayout(btn_layout)

        self.update_preview_table()

    def update_preview_table(self):
        target_sess = self.cmb_session.currentText()
        target_yr = self.cmb_year.currentText()
        target_sem = self.cmb_sem.currentText()

        self.tbl_preview.setRowCount(len(self.students))
        for row, st in enumerate(self.students):
            curr_stage = f"{st.year or 'N/A'} / {st.semester or 'N/A'} ({st.academic_session})"
            target_stage = f"{target_yr} / {target_sem} ({target_sess})"

            self.tbl_preview.setItem(row, 0, QTableWidgetItem(st.admission_no))
            self.tbl_preview.setItem(row, 1, QTableWidgetItem(st.name))
            self.tbl_preview.setItem(row, 2, QTableWidgetItem(st.course or "General"))
            self.tbl_preview.setItem(row, 3, QTableWidgetItem(curr_stage))
            
            item_tgt = QTableWidgetItem(target_stage)
            item_tgt.setForeground(Qt.darkGreen)
            self.tbl_preview.setItem(row, 4, item_tgt)

    def execute_promotion(self):
        password = self.txt_admin_password.text().strip()
        if not password:
            QMessageBox.warning(self, "Security Required", "Please enter the Administrator Password to authorize promotion.")
            self.txt_admin_password.setFocus()
            return

        # Authenticate Admin Password
        if not AuthController.verify_admin_password(password):
            QMessageBox.critical(self, "Authentication Failed", "Invalid Administrator Password. Promotion cancelled.")
            self.txt_admin_password.clear()
            self.txt_admin_password.setFocus()
            return

        target_sess = self.cmb_session.currentText()
        target_yr = self.cmb_year.currentText()
        target_sem = self.cmb_sem.currentText()

        st_ids = [s.id for s in self.students]
        success, msg = PromotionService.bulk_promote_students(st_ids, target_sess, target_yr, target_sem)

        if success:
            QMessageBox.information(self, "Promotion Complete", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Promotion Blocked", f"Failed to promote students:\n\n{msg}")
