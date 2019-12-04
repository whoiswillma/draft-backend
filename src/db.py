from flask_sqlalchemy import SQLAlchemy
import bcrypt
import datetime
import hashlib
import json
import os

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    trips = db.relationship('Trip', cascade='delete')
        
    username = db.Column(db.String, nullable=True)
    password_digest = db.Column(db.String, nullable=False)

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
        self.trips = []
        self.renew_session()

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'trips': [trip.serialize() for trip in self.trips]
        }

    def serialize_session_info(self):
        return {
            'session_token': self.session_token,
            'seesion_expiration': str(self.session_expiration),
            'update_token': self.update_token
        }

    # Used to randomly generate session/update tokens
    def _urlsafe_base_64(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    # Generates new tokens, and resets expiration time
    def renew_session(self):
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def is_password_valid(self, password):
        return bcrypt.checkpw(password.encode("utf8"), self.password_digest)

    # Checks if session token is valid and hasn't expired
    def is_session_token_valid(self, session_token):
        return (
            session_token == self.session_token
            and datetime.datetime.now() < self.session_expiration
        )

    def is_update_token_valid(self, update_token):
        return update_token == self.update_token

    @staticmethod
    def user_with_id(user_id):
        return User.query.filter(User.id == user_id).first()

    @staticmethod
    def user_with_username(username):
        return User.query.filter(User.username == username).first()
        
    @staticmethod
    def user_with_valid_session_token(session_token):
        user = User.query.filter(User.session_token == session_token).first()
        if user and user.is_session_token_valid(session_token):
            return user
        else:
            return None

    @staticmethod
    def user_with_update_token(update_token):
        return User.query.filter(User.update_token == update_token).first()

    @staticmethod
    def create_user(username, password):
        optional_user = User.user_with_username(username)

        if optional_user:
            return False, optional_user

        user = User(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        return True, user


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
            serialized['image_url'] = unsplash_json['urls']['regular']
            serialized['image_credit'] = unsplash_json['user']['name']
        except:
            serialized['image_url'] = None
            serialized['image_credit'] = None
            
        return serialized

    @staticmethod
    def trip_with_id(trip_id):
        return Trip.query.filter_by(id=trip_id).first()


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
