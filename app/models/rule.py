# app/models/rule.py
import json
from extensions import db


class RuleTable(db.Model):
    __tablename__ = "tbl_rules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    location_name = db.Column(db.String(120), nullable=False)
    province_name = db.Column(db.String(120), nullable=False)
    budget = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    image = db.Column(db.String(255), nullable=True, default="")
    explanation = db.Column(db.Text, nullable=True)
    tags_json = db.Column(db.Text, nullable=True, default="[]")
    moods_json = db.Column(db.Text, nullable=True, default="[]")
    go_with_json = db.Column(db.Text, nullable=True, default="[]")

    @property
    def images_list(self):
        if not self.image:
            return []
        try:
            if self.image.startswith("[") and self.image.endswith("]"):
                return json.loads(self.image)
        except Exception:
            pass
        return [img.strip() for img in self.image.split(",") if img.strip()]

    @property
    def tags(self):
        try:
            return json.loads(self.tags_json or "[]")
        except Exception:
            return []

    @tags.setter
    def tags(self, value):
        self.tags_json = json.dumps(value or [], ensure_ascii=False)

    @property
    def moods(self):
        try:
            return json.loads(self.moods_json or "[]")
        except Exception:
            return []

    @moods.setter
    def moods(self, value):
        self.moods_json = json.dumps(value or [], ensure_ascii=False)

    @property
    def go_with(self):
        try:
            return json.loads(self.go_with_json or "[]")
        except Exception:
            return []

    @go_with.setter
    def go_with(self, value):
        self.go_with_json = json.dumps(value or [], ensure_ascii=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name or "",
            "location_name": self.location_name,
            "province_name": self.province_name,
            "budget": self.budget,
            "is_active": self.is_active,
            "image": self.image or "",
            "images_list": self.images_list,
            "explanation": self.explanation or "",
            "tags": self.tags,
            "moods": self.moods,
            "go_with": self.go_with,
        }

    def __repr__(self):
        return f"<Rule {self.id} - {self.location_name}>"
