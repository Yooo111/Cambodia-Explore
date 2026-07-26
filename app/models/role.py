# app/models/role.py
from datetime import datetime
from extensions import db
from app.models.associations import tbl_user_roles, tbl_role_permissions

class RoleTable(db.Model):
    __tablename__ = "tbl_roles"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # NOTE: matches UsesTable.roles
    users = db.relationship("UserTable", secondary=tbl_user_roles, back_populates="roles")
    
    # NOTE: matchea PermissionTable.roles
    permissions = db.relationship("PermissionTable", secondary=tbl_role_permissions, back_populates="roles")
    
    
    def has_permission(self, permission_code: str) -> bool:
        return any(p.code == permission_code for p in self.permissions)
    
    def __repr__(self) -> str:
        return f"<Role {self.name}>"