# app/forms/user_forms.py
import re
from flask_wtf import FlaskForm
from wtforms import (BooleanField, StringField, SelectField, SubmitField, PasswordField)
from wtforms.validators import (DataRequired, Email, Length, EqualTo, ValidationError, Optional)
from app.models.user import UserTable
from app.models.role import RoleTable
from extensions import db

# ----------helpers validators ----------
def strong_password(form, field):
    """Requires min 8 chars, Upper, lower, digit, special."""
    password = field.data or ""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|+=<>-]", password):
        raise ValidationError("Password must contain at least one special character.")
    
def _role_choices():
    """Return list of (id, name) tuples for all rolse, ordered by name."""
    return [
        (role.id, role.name)
        for role in db.session.scalars(
            db.select(RoleTable).order_by(RoleTable.name)
        )
    ]
    
# -------- create form -------------------------------
class UserCreateForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={"placeholder": "Enter username"}
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={"placeholder": "Enter email"},
    )
    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=3, max=120)],
        render_kw={"placeholder": "Enter full name"}
    )
    is_active = BooleanField("Active", default=True)
    
    role_id = SelectField(
        "Role",
        coerce=int,
        validators=[DataRequired()],
        render_kw={"placeholder": "Select role"},
    )
    
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            strong_password,
        ],
        render_kw={"placeholder": "Strong password"}
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "Confirm password"},
    )
    
    submit = SubmitField("Save")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_id.choices = _role_choices()
    
    def validate_username(self, field):
        exists = db.session.scalar(
            db.select(UserTable).filter(UserTable.username == field.data)
        )
        if exists:
            raise ValidationError("This username is already taken.")
    
    def validate_email(self, field):
        exists = db.session.scalar(
            db.select(UserTable).filter(UserTable.email == field.data)
        )
        if exists:
            raise ValidationError("This email is already registered.")
        
# -------- edit form (password optional) ----------
class UserEditForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=3, max=120)],
    )
    # gender = StringField(
    #     "Gender",
    #     validators=[DataRequired(), Length(min=3, max=120)],
    # )
    is_active = BooleanField("Active")
    
    role_id = SelectField(
        "Role",
        coerce=int,
        validators=[DataRequired()],
    )
    
    # optional password - only change if filled
    password = PasswordField(
        "New password (leave blank to keep current)",
        validators=[Optional(),strong_password],
        render_kw={"placeholder": "New strong password (optional)"},
    ) 
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[EqualTo("password", message="Passwords must match.")],
    )
    
    submit = SubmitField("Update")
    
    def __init__(self, original_user: UserTable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_user = original_user
        self.role_id.choices = _role_choices()
        
        if not self.is_submitted():
            if original_user.roles:
                self.role_id.data = original_user.roles[0].id
            else:
                self.role_id.data = None
        
    def validate_username(self, field):
        q = db.select(UserTable).filter(
            UserTable.username == field.data, 
            UserTable.id != self.original_user.id,
        )
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This username is already taken.")
        
    def validate_email(self, field):
        q = db.select(UserTable).filter(
            UserTable.email == field.data, 
            UserTable.id != self.original_user.id,
        )
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This email is already registered.")
        
class UserConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")