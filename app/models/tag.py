# app/models/tag.py
from extensions import db


class TagTable(db.Model):
    __tablename__ = "tbl_tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

    def __repr__(self):
        return f"<Tag {self.name}>"
