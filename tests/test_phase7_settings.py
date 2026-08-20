"""
Unit tests for Phase 7 – Professional Settings & Administration Module (v1.7.0).
"""

import pytest
from datetime import datetime
from config.database import init_db, get_db
from models.user import User
from models.settings import SchoolInformation, AcademicSession
from models.audit import AuditLog, BackupHistory
from services.security_service import SecurityService
from services.backup_service import BackupService
from controllers.auth_controller import AuthController
from controllers.settings_controller import SettingsController


@pytest.fixture(autouse=True)
def setup_database():
    """Ensure database schema is initialized before running tests."""
    init_db()


def test_admin_auth_verification():
    """Verify administrator password authentication and failed log generation."""
    # Ensure default admin account exists
    db = get_db()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            AuthController.create_user("admin", "admin123", "System Administrator", "Admin")
    finally:
        db.close()

    # Valid password test
    assert SecurityService.verify_admin_password("admin123", module="Settings") is True

    # Invalid password test
    assert SecurityService.verify_admin_password("wrong_password_999", module="Settings") is False


def test_school_information_crud():
    """Verify loading and updating extended school information fields."""
    update_data = {
        "school_name": "Test International Academy",
        "address": "456 Education Hub",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pin_code": "400001",
        "phone": "+91 99999 88888",
        "email": "contact@testacademy.edu.in",
        "website": "www.testacademy.edu.in",
        "principal_name": "Dr. S. K. Mehta",
        "receipt_prefix": "REC/TEST/",
        "receipt_footer": "Official Test Receipt Footer Note"
    }

    success, msg = SettingsController.update_school_info(update_data)
    assert success is True

    info = SettingsController.get_school_info()
    assert info is not None
    assert info.school_name == "Test International Academy"
    assert info.city == "Mumbai"
    assert info.state == "Maharashtra"
    assert info.pin_code == "400001"
    assert info.principal_name == "Dr. S. K. Mehta"
    assert info.receipt_prefix == "REC/TEST/"


def test_user_management_crud():
    """Verify user account creation, edit, password reset/change, status toggle, and deletion."""
    test_username = "test_operator_p7"
    
    # Clean up prior test runs if existing
    db = get_db()
    try:
        existing = db.query(User).filter(User.username == test_username).first()
        if existing:
            db.delete(existing)
            db.commit()
    finally:
        db.close()

    # 1. Create User
    assert AuthController.create_user(test_username, "pass1234", "Test Op User", "Operator") is True

    # Retrieve user
    users = AuthController.get_all_users()
    target_user = next((u for u in users if u.username == test_username), None)
    assert target_user is not None
    assert target_user.role == "Operator"
    assert target_user.status == "Active"

    # 2. Update User (Edit Role & Status)
    success, msg = AuthController.update_user(target_user.id, "Updated Op User", "Viewer", "Disabled")
    assert success is True

    users_updated = AuthController.get_all_users()
    target_user_updated = next((u for u in users_updated if u.username == test_username), None)
    assert target_user_updated.full_name == "Updated Op User"
    assert target_user_updated.role == "Viewer"
    assert target_user_updated.status == "Disabled"

    # 3. Reset Password
    res_success, res_msg = AuthController.reset_password(target_user.id, "newpass5678")
    assert res_success is True

    # 4. Delete User
    del_success, del_msg = AuthController.delete_user(target_user.id)
    assert del_success is True


def test_database_stats_and_optimization():
    """Verify database statistics retrieval, vacuum optimization, and integrity check."""
    stats = SettingsController.get_database_stats()
    assert "db_path" in stats
    assert "db_size" in stats
    assert stats["student_count"] >= 0
    assert stats["receipt_count"] >= 0
    assert stats["fee_head_count"] >= 0

    opt_success, opt_msg = SettingsController.optimize_database()
    assert opt_success is True

    ver_success, ver_msg = SettingsController.verify_database_integrity()
    assert ver_success is True


def test_backup_history_and_creation():
    """Verify database backup creation and backup log recording."""
    success, msg, backup_path = BackupService.create_backup()
    assert success is True
    assert backup_path != ""

    db = get_db()
    try:
        latest = db.query(BackupHistory).order_by(BackupHistory.created_at.desc()).first()
        assert latest is not None
        assert latest.status == "Success"
    finally:
        db.close()


def test_audit_logs_query():
    """Verify audit log filtered search and query retrieval."""
    logs = SettingsController.get_audit_logs(module="All")
    assert isinstance(logs, list)
    assert len(logs) > 0


def test_application_preferences():
    """Verify saving and retrieving application preferences."""
    test_prefs = {
        "window_size": "1600x900",
        "sidebar_expanded": True,
        "theme": "Professional Navy",
        "auto_backup": True,
        "currency_symbol": "₹",
        "date_format": "DD/MM/YYYY"
    }

    save_success, msg = SettingsController.save_preferences(test_prefs)
    assert save_success is True

    loaded_prefs = SettingsController.get_preferences()
    assert loaded_prefs["window_size"] == "1600x900"
    assert loaded_prefs["sidebar_expanded"] is True


def test_window_size_apply_logic():
    """Verify MainWindow reacts to window size changes and applies requested geometry."""
    from PySide6.QtWidgets import QApplication
    from views.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    win = MainWindow()

    win.apply_window_size("1600x900")
    assert win.width() == 1600
    assert win.height() == 900

    win.apply_window_size("1280x750")
    assert win.width() == 1280
    assert win.height() == 750

    win.apply_window_size("1280x800")
    assert win.width() == 1280
    assert win.height() == 800

    win.apply_window_size("Maximize")
    assert win.isMaximized() is True

