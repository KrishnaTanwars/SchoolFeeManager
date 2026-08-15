"""
Reusable Academic Filter Component for Course, Branch, Academic Year, Semester, and Session Filtering.
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QFrame
)
from PySide6.QtCore import Signal, Qt
from controllers.academic_controller import AcademicController
from controllers.settings_controller import SettingsController

class AcademicFilterWidget(QFrame):
    """
    Unified, compact filter widget containing synced dropdowns for:
    Course, Branch, Academic Year, Semester, and Academic Session.
    Emits filters_changed(dict) on value selection.
    """
    filters_changed = Signal(dict)

    def __init__(self, parent=None, show_all_option: bool = True, include_session: bool = True):
        super().__init__(parent)
        self.show_all_option = show_all_option
        self.include_session = include_session

        self.setObjectName("AcademicFilterWidget")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            #AcademicFilterWidget {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px;
            }
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #334155;
            }
            QComboBox {
                min-width: 80px;
                max-width: 160px;
                padding: 4px 6px;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 12px;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(10)

        # Category Combo
        layout.addWidget(QLabel("Category:"))
        self.cmb_category = QComboBox()
        layout.addWidget(self.cmb_category)

        # Course Combo
        layout.addWidget(QLabel("Course:"))
        self.cmb_course = QComboBox()
        layout.addWidget(self.cmb_course)

        # Branch Combo
        layout.addWidget(QLabel("Branch:"))
        self.cmb_branch = QComboBox()
        layout.addWidget(self.cmb_branch)

        # Academic Year Combo
        layout.addWidget(QLabel("Year:"))
        self.cmb_year = QComboBox()
        layout.addWidget(self.cmb_year)

        # Semester Combo
        layout.addWidget(QLabel("Semester:"))
        self.cmb_semester = QComboBox()
        layout.addWidget(self.cmb_semester)

        # Academic Session Combo
        if self.include_session:
            layout.addWidget(QLabel("Session:"))
            self.cmb_session = QComboBox()
            layout.addWidget(self.cmb_session)

        layout.addStretch()

        self.populate_options()
        self.connect_signals()

    def populate_options(self):
        self.block_all_signals(True)

        prefix = ["All"] if self.show_all_option else []

        # Populate Category
        self.cmb_category.clear()
        self.cmb_category.addItems(prefix + ["UG", "PG"])

        # Populate Courses
        courses = AcademicController.get_courses()
        self.cmb_course.clear()
        self.cmb_course.addItems(prefix + courses)

        # Populate Branches
        branches = AcademicController.get_branches()
        self.cmb_branch.clear()
        self.cmb_branch.addItems(prefix + branches)

        # Populate Years
        years = AcademicController.get_years()
        self.cmb_year.clear()
        self.cmb_year.addItems(prefix + years)

        # Populate Semesters
        semesters = AcademicController.get_semesters()
        self.cmb_semester.clear()
        self.cmb_semester.addItems(prefix + semesters)

        # Populate Sessions
        if self.include_session:
            self.cmb_session.clear()
            sessions = SettingsController.get_academic_sessions()
            session_names = [s.session_name for s in sessions] if sessions else ["2024-2025", "2025-2026", "2026-2027"]
            self.cmb_session.addItems(prefix + session_names)

        self.block_all_signals(False)

    def block_all_signals(self, block: bool):
        self.cmb_category.blockSignals(block)
        self.cmb_course.blockSignals(block)
        self.cmb_branch.blockSignals(block)
        self.cmb_year.blockSignals(block)
        self.cmb_semester.blockSignals(block)
        if self.include_session:
            self.cmb_session.blockSignals(block)

    def connect_signals(self):
        self.cmb_category.currentTextChanged.connect(self.on_category_changed)
        self.cmb_course.currentTextChanged.connect(self.on_course_changed)
        self.cmb_branch.currentTextChanged.connect(self.on_filter_changed)
        self.cmb_year.currentTextChanged.connect(self.on_filter_changed)
        self.cmb_semester.currentTextChanged.connect(self.on_filter_changed)
        if self.include_session:
            self.cmb_session.currentTextChanged.connect(self.on_filter_changed)
            from services.session_service import session_manager
            session_manager.session_changed.connect(self.on_session_changed_signal)

    def on_category_changed(self, cat_text: str):
        self.block_all_signals(True)
        prefix = ["All"] if self.show_all_option else []
        courses = AcademicController.get_courses_by_category(cat_text)
        self.cmb_course.clear()
        self.cmb_course.addItems(prefix + courses)
        self.block_all_signals(False)
        self.on_course_changed(self.cmb_course.currentText())

    def on_course_changed(self, course_text: str):
        self.block_all_signals(True)
        prefix = ["All"] if self.show_all_option else []
        crs_val = "" if course_text == "All" else course_text
        years = AcademicController.get_years(course_name=crs_val)
        semesters = AcademicController.get_semesters(course_name=crs_val)

        curr_yr = self.cmb_year.currentText()
        self.cmb_year.clear()
        self.cmb_year.addItems(prefix + years)
        if curr_yr in years:
            self.cmb_year.setCurrentText(curr_yr)

        curr_sem = self.cmb_semester.currentText()
        self.cmb_semester.clear()
        self.cmb_semester.addItems(prefix + semesters)
        if curr_sem in semesters:
            self.cmb_semester.setCurrentText(curr_sem)

        self.block_all_signals(False)
        self.on_filter_changed()

    def on_session_changed_signal(self, new_session: str):
        if self.include_session:
            self.populate_options()

    def on_filter_changed(self):
        filters = self.get_filter_values()
        self.filters_changed.emit(filters)

    def get_filter_values(self) -> Dict[str, str]:
        cat = self.cmb_category.currentText().strip()
        c = self.cmb_course.currentText().strip()
        b = self.cmb_branch.currentText().strip()
        y = self.cmb_year.currentText().strip()
        sem = self.cmb_semester.currentText().strip()
        sess = self.cmb_session.currentText().strip() if self.include_session else "All"

        return {
            "category": "" if cat == "All" else cat,
            "course": "" if c == "All" else c,
            "branch": "" if b == "All" else b,
            "year": "" if y == "All" else y,
            "semester": "" if sem == "All" else sem,
            "session": "" if sess == "All" else sess,
        }

    def reset_filters(self):
        self.block_all_signals(True)
        if self.show_all_option:
            self.cmb_category.setCurrentText("All")
            self.cmb_course.setCurrentText("All")
            self.cmb_branch.setCurrentText("All")
            self.cmb_year.setCurrentText("All")
            self.cmb_semester.setCurrentText("All")
            if self.include_session:
                self.cmb_session.setCurrentText("All")
        self.block_all_signals(False)
        self.on_filter_changed()
