# app/services/seed_service.py
import os
import json
from extensions import db
from app.models.tag import TagTable
from app.models.mood import MoodTable
from app.models.go_with import GoWithTable
from app.models.fact import FactTable
from app.models.rule import RuleTable
from app.models.taxonomy import TaxonomyTable
from app.models.role import RoleTable
from app.models.user import UserTable

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')


def _load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []


def seed_database():
    """Migrates existing JSON file records to MySQL database if tables are empty."""
    # Seed Roles if not exist
    admin_role = RoleTable.query.filter_by(name="Admin").first()
    user_role = RoleTable.query.filter_by(name="User").first()

    if not admin_role:
        admin_role = RoleTable(name="Admin", description="Administrator with full access")
        db.session.add(admin_role)
    if not user_role:
        user_role = RoleTable(name="User", description="Standard user account")
        db.session.add(user_role)

    db.session.flush()

    # Seed default Admin account if no users
    if UserTable.query.count() == 0:
        admin_user = UserTable(
            username="admin",
            email="admin@example.com",
            full_name="System Administrator",
            is_active=True,
        )
        admin_user.set_password("Admin123!")
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)

    # Seed Tags
    if TagTable.query.count() == 0:
        tags = _load_json('tags.json')
        for item in tags:
            tag = TagTable(id=item.get('id'), name=item.get('name'))
            db.session.add(tag)

    # Seed Moods
    if MoodTable.query.count() == 0:
        moods = _load_json('moods.json')
        for item in moods:
            mood = MoodTable(id=item.get('id'), name=item.get('name'))
            db.session.add(mood)

    # Seed GoWith
    if GoWithTable.query.count() == 0:
        go_withs = _load_json('go_with.json')
        for item in go_withs:
            gw = GoWithTable(id=item.get('id'), name=item.get('name'))
            db.session.add(gw)

    # Seed Facts
    if FactTable.query.count() == 0:
        facts = _load_json('facts.json')
        for item in facts:
            fact = FactTable(
                id=item.get('id'),
                location_name=item.get('location_name', ''),
                description=item.get('description', '')
            )
            db.session.add(fact)

    # Seed Rules
    if RuleTable.query.count() == 0:
        rules = _load_json('rules.json')
        for item in rules:
            rule = RuleTable(
                id=item.get('id'),
                name=item.get('name', ''),
                location_name=item.get('location_name', ''),
                province_name=item.get('province_name', ''),
                budget=item.get('budget', ''),
                is_active=item.get('is_active', True),
                image=item.get('image', ''),
                explanation=item.get('explanation', ''),
            )
            rule.tags = item.get('tags', [])
            rule.moods = item.get('moods', [])
            rule.go_with = item.get('go_with', [])
            db.session.add(rule)

    # Seed Taxonomy
    if TaxonomyTable.query.count() == 0:
        taxonomy = _load_json('taxonomy.json')
        for item in taxonomy:
            tax = TaxonomyTable(
                id=item.get('id'),
                name=item.get('name', ''),
                type=item.get('type', ''),
                description=item.get('description', '')
            )
            db.session.add(tax)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Database seed note: {e}")
