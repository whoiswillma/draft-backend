import json
from db import db, User, Trip, Entry
from flask import Flask, request
import ssl
import os
import sys
import unsplash_api
from flog import fprint

app = Flask(__name__)
db_filename = 'app.db'
debug_enabled = bool(os.getenv('DEBUG'))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = debug_enabled


db.init_app(app)
with app.app_context():
    db.create_all()


def extract_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False, json.dumps({'error': 'Missing authorization header'})

    bearer_token = auth_header.replace('Bearer ', '').strip()
    if not bearer_token: 
        return False, json.dumps({'error': 'Missing authorization token'})

    return True, bearer_token


def json_response(success, data_or_error, code):
    res = { "success": success }
    if data_or_error != None:
        if success:
            res['data'] = data_or_error
        else:
            res['error'] = data_or_error
    return json.dumps(res), code, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/api/users/', methods=['GET'])
def user_get_all():
    if debug_enabled:
        return json_response(True, [user.serialize() for user in User.query.all()], 200)
    else:
        return None


@app.route('/api/user/<int:user_id>/', methods=['GET'])
def user_get_id(user_id):
    user = User.user_with_id(user_id)
    if user:
        return json_response(True, user.serialize(), 200)
    else:
        return json_response(False, 'User not found', 404)


@app.route('/api/users/', methods=['POST'])
def user_create():
    try:
        body = json.loads(request.data)

        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return json_response(False, 'Missing username or password', 400)

        created, user = User.create_user(username, password)

        if not created:
            return json_response(False, 'User already exists', 400)

        return json_response(True, user.serialize_session_info(), 200)

    except Exception as e:
        return json_response(False, 'Exception: ' + str(e), 500)


@app.route('/api/users/delete_all/', methods=['DELETE'])
def user_delete_all():
    if debug_enabled:
        for user in User.query.all():
            db.session.delete(user)

        db.session.commit()

        return json_response(True, None, 200)
    else:
        return None


def trip_update_contents(trip, data):
    trip.name = data.get('name', 'Untitled trip')
    trip.start = data.get('start')
    for entry in trip.entries:
        db.session.delete(entry)

    for entry_data in data.get('entries', []):
        entry = Entry(
            description=entry_data['description'], 
            kind=entry_data['kind'],
            completed=False,
            day_index=entry_data['day_index']
        )
        trip.entries.append(entry)
        db.session.add(entry)

    location = data.get('location')
    if location:
        trip.location = location
        trip.unsplash_data = unsplash_api.unsplash_search(location)

    return trip
        

@app.route('/api/trip/', methods=['POST'])
def trip_create():
    try:
        success, session_token = extract_token(request)
        if not success:
            return json_response(False, 'Unable to extract session token: ' + session_token, 401)

        user = User.user_with_session_token(session_token)
        if not user:
            return json_response(False, 'User not found', 404)
        
        
        body = json.loads(request.data)

        with db.session.no_autoflush:
            trip = Trip()
            trip_update_contents(trip, body)
            user.trips.append(trip)
            db.session.add(trip)

        db.session.commit()

        return json_response(True, trip.serialize(), 200)

    except Exception as e:
        return json_response(False, 'Exception: ' + str(e), 500)


@app.route('/api/trip/<int:trip_id>/', methods=['PUT'])
def trip_update(trip_id):
    try:
        success, session_token = extract_token(request)
        if not success:
            return json_response(False, 'Unable to extract session token', 401)

        user = User.user_with_valid_session_token(session_token)
        if not user:
            return json_response(False, 'User not found', 401)

        body = json.loads(request.data)

        trip = Trip.trip_with_id(trip_id)
        if not trip:
            return json_response(False, 'Trip not found', 400)

        if trip.user_id != user_id:
            return json_response(False, 'Permission denied', 401)
        
        with db.session.no_autoflush: 
            trip_update_contents(trip, body)

        db.session.commit()

        return json_response(True, trip.serialize(), 200)

    except Exception as e:
        return json_response(False, str(e), 500)


@app.route('/auth/login/', methods=['GET'])
def auth_login():
    try:
        body = json.loads(request.data)
        username = body['username']
        password = body['password']

        user = User.user_with_username(username)
        if not user:
            return json_response(False, 'User not found', 400)
        
        if user.is_password_valid(password):
            return json_response(True, user.serialize_session_info(), 200)
        else: 
            return json_response(False, None, 400)

    except Exception as e:
        json_response(False, str(e), 500)


@app.route('/auth/refresh/', methods=['GET'])
def auth_refresh():
    try:
        body = json.loads(request.data)


    except Exception as e:
        json_response(False, str(e), 500)


@app.route("/secret/", methods=["GET"])
def secret():
    success, session_token = extract_token(request)

    if not success:
        return json_response(False, 'Unable to extract session token: ' + session_token, 401)

    user = User.user_with_session_token(session_token)
    if not user or not user.is_session_token_valid(session_token):
        return json_response(False, 'Invalid Session Token', 401)  

    return json_response(True, 'Session token is valid', 200)


if __name__ == '__main__':
    if not debug_enabled:
        fprint('Starting draft-backend in production mode')
    else: 
        fprint('Starting draft-backend in debug mode')

    if os.getenv('UNSPLASH_ACCESS_KEY'):
        fprint('Unsplash API key found')
    else:
        fprint('Unsplash API key NOT found')
    
    if not debug_enabled:
        app.run(host='0.0.0.0', 
                port=5000, 
                debug=False)
    else:
        app.run(host='0.0.0.0', 
                port=5000, 
                debug=True)
