from extensions import db


class Location(db.Model):
    __tablename__ = "locations"

    locationID = db.Column(db.Integer, primary_key=True)
    LocationName = db.Column(db.String(100), nullable=False, unique=True)
    ProvinceName = db.Column(db.String(100), nullable=True)
    Tags = db.Column(db.String(255), nullable=True)
    Budget_level = db.Column(db.String(50), nullable=True)
    Moods = db.Column(db.String(255), nullable=True)
    go_with = db.Column(db.String(255), nullable=True)
    Description = db.Column(db.Text, nullable=True)
    images = db.Column(db.String(255), nullable=True)  
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Location {self.locationID} - {self.LocationName}>"
