from app.models.location import Location
from extensions import db

class LocationService:
    @staticmethod
    def get_all():
        return Location.query.all()

    @staticmethod
    def get_by_id(locationID):
        return Location.query.get_or_404(locationID)

    @staticmethod
    def create(data, filename=None):
        location = Location(
            LocationName=data['LocationName'],
            ProvinceName=data.get('ProvinceName'),
            Tags=data.get('Tags'),
            Budget_level=data.get('Budget_level'),
            Moods=data.get('Moods'),
            go_with=data.get('go_with'),
            Description=data.get('Description'),
            images=filename,
            is_active=data.get('is_active', True)
        )
        db.session.add(location)
        db.session.commit()
        return location

    @staticmethod
    def update(location, data, filename=None):
        location.LocationName = data['LocationName']
        location.ProvinceName = data.get('ProvinceName')
        location.Tags = data.get('Tags')
        location.Budget_level = data.get('Budget_level')
        location.Moods = data.get('Moods')
        location.go_with = data.get('go_with')
        location.Description = data.get('Description')
        if filename:
            location.images = filename
        location.is_active = data.get('is_active', True)
        db.session.commit()
        return location

    @staticmethod
    def delete(location):
        db.session.delete(location)
        db.session.commit()
