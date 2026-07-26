# app/services/permission_service.py
from typing import List, Optional
from app.models.permission import PermissionTable
from extensions import db

class PermissionService:
    @staticmethod
    def get_permission_all() -> List[PermissionTable]:
        return PermissionTable.query.order_by(PermissionTable.code.asc()).all()
    
    @staticmethod
    def get_permission_by_id(permission_id: int) -> Optional[PermissionTable]:
        return PermissionTable.query.get(permission_id)
    
    @staticmethod
    def create_permission(data: dict) -> PermissionTable:
        perm = PermissionTable(
            code=data["code"],
            name=data["name"],
            module=data.get("module", "General"),
            description=data.get("description") or "",
        )
        db.session.add(perm)
        db.session.commit()
        return perm
    
    @staticmethod
    def update_permission(
        permission: PermissionTable,
        data: dict,
    ) -> PermissionTable:
        permission.code = data.get("code")
        permission.name = data.get("name")
        permission.module = data.get("module", "General")
        permission.description = data.get("description") or ""
        
        db.session.commit()
        return permission
    
    @staticmethod
    def delete_permission(permission: PermissionTable) -> None:
        db.session.delete(permission)
        db.session.commit()