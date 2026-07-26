# app/forms/__init__.py
from app.forms.user_forms import UserCreateForm, UserEditForm, UserConfirmDeleteForm
from app.forms.role_forms import RoleCreateForm, RoleEditForm, RoleConfirmDeleteForm
from app.forms.permission_forms import (
    PermissionCreateForm,
    PermissionEditForm,
    PermissionConfirmDeleteForm,
)

__all__ = [
    "UserCreateForm",
    "UserEditForm",
    "UserConfirmDeleteForm",
    "RoleCreateForm",
    "RoleEditForm",
    "RoleConfirmDeleteForm",
    "PermissionCreateForm",
    "PermissionEditForm",
    "PermissionConfirmDeleteForm",
]

#  font NU E1, NU S1