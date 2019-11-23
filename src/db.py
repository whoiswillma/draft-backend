from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    trips = db.relationship('Trip', cascade='delete')

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.trips = []

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'trips': [trip.serialize() for trip in self.trips]
        }


class Trip(db.Model):
    __tablename__ = 'trip'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=True)
    start = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unsplash_data = db.Column(db.String, nullable=True)
    entries = db.relationship('Entry', cascade='delete')

    def __init__(self):
        self.name = ''
        self.entries = []

    def serialize(self, group_by_days = False):
        serialized = {
            'id': self.id,
            'location': self.location,
            'name': self.name,
            'start': self.start
        }

        if group_by_days:
            entry_by_day = {}
            for entry in self.entries:
                entry_by_day[entry.day_index] = entry.serialize()
            serialized['days'] = entry_by_day

        else:
            serialized['entries'] = [entry.serialize() for entry in self.entries]

        try:
            unsplash_json = json.loads(self.unsplash_data)
            image_url = unsplash_json['urls']['regular']
            serialized['image_url'] = image_url
        except:
            serialized['image_url'] = None
            
        return serialized
    

class Entry(db.Model):
    __tablename__ = 'entry'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=True)
    kind = db.Column(db.String, nullable=True)
    completed = db.Column(db.Boolean, nullable=False)
    day_index = db.Column(db.Integer, nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)

    def __init__(self, **kwargs):
        self.description = kwargs.get('description')
        self.kind = kwargs.get('kind', None)
        self.completed = kwargs.get('completed', False)
        self.day_index = kwargs.get('day_index', 0)

    def serialize(self):
        return {
            'id': self.id,
            'description': self.description,
            'kind': self.kind,
            'completed': self.completed,
            'day_index': self.day_index
        }
