# app/models/__init__.py
from app.models.user import UserTable
from app.models.role import RoleTable
from app.models.permission import PermissionTable
from app.models.location import Location
from app.models.rule import RuleTable
from app.models.fact import FactTable
from app.models.tag import TagTable
from app.models.mood import MoodTable
from app.models.go_with import GoWithTable
from app.models.taxonomy import TaxonomyTable

__all__ = [
    "UserTable",
    "RoleTable",
    "PermissionTable",
    "Location",
    "RuleTable",
    "FactTable",
    "TagTable",
    "MoodTable",
    "GoWithTable",
    "TaxonomyTable",
]
