"""
Centralized Reusable Administrator Authentication Service Wrapper.
Provides clean facade API functions (verify_admin_password, show_admin_dialog, authenticate)
for all ERP views and controllers.
"""

from services.security_service import SecurityService
from dialogs.admin_auth_dialog import AdminAuthDialog

def verify_admin_password(password: str, module: str = "General") -> bool:
    """Verifies administrator password and logs audit events on success/failure."""
    return SecurityService.verify_admin_password(password, module=module)

def show_admin_dialog(parent=None, action_title: str = "Administrator Authorization Required", action_context: str = "", module: str = "General") -> bool:
    """Displays the AdminAuthDialog modal and returns True if authorized, False otherwise."""
    dialog = AdminAuthDialog(
        parent=parent,
        action_title=action_title,
        action_context=action_context,
        module=module
    )
    return bool(dialog.exec())

def authenticate(parent=None, action_name: str = "Critical Action", module_name: str = "General", record_desc: str = "") -> bool:
    """
    Standard high-level authentication facade for ERP views.
    Prompts AdminAuthDialog and returns True if successfully authorized.
    """
    action_context = f"{action_name}: {record_desc}" if record_desc else action_name
    return show_admin_dialog(
        parent=parent,
        action_title=f"{action_name} Protection",
        action_context=action_context,
        module=module_name
    )
