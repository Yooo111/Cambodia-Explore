# app/models/fact.py
from extensions import db


class FactTable(db.Model):
    __tablename__ = "tbl_facts"

    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "location_name": self.location_name,
            "description": self.description,
        }

    def __repr__(self):
        return f"<Fact {self.id} - {self.location_name}>"
