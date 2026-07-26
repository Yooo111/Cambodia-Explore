# app/models/taxonomy.py
from extensions import db


class TaxonomyTable(db.Model):
    __tablename__ = "tbl_taxonomy"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description or "",
        }

    def __repr__(self):
        return f"<Taxonomy {self.id} - {self.name}>"
