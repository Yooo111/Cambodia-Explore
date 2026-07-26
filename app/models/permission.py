# app/models/permission.py
from datetime import datetime
from extensions import db
from app.models.associations import tbl_role_permissions


class PermissionTable(db.Model):
    __tablename__ = "tbl_permissions"
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    module = db.Column(db.String(80), nullable=False, default="General")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # NOTE: matches RoleTable.permissions
    roles = db.relationship("RoleTable", secondary=tbl_role_permissions, back_populates="permissions")
    
    def __repr__(self) -> str:
        return f"<Permission {self.code}>"