# app/models/mood.py
from extensions import db


class MoodTable(db.Model):
    __tablename__ = "tbl_moods"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

    def __repr__(self):
        return f"<Mood {self.name}>"
