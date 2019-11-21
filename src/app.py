import json
from db import db, User, Trip, Entry
from flask import Flask, request
import unsplash_api

app = Flask(__name__)
db_filename = 'app.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()

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
    return json_response(True, [user.serialize() for user in User.query.all()], 200)


@app.route('/api/user/<int:user_id>/', methods=['GET'])
def user_get_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return json_response(True, user.serialize(), 200)

    else:
        return json_response(False, 'User not found', 404)


@app.route('/api/users/', methods=['POST'])
def user_create():
    try:
        body = json.loads(request.data)
        user = User(name=body.get('name'))
        db.session.add(user)
        db.session.commit()

        return json_response(True, user.serialize(), 200)

    except Exception as e:
        return json.dumps({
            'success': False, 
            'error': 'Exception: ' + str(e)
        }), 400


@app.route('/api/users/delete_all/', methods=['DELETE'])
def user_delete_all():
    for user in User.query.all():
        db.session.delete(user)
    db.session.commit()

    return json_response(True, None, 200)


def trip_update_contents(trip, data):
    trip.name = data.get('name', 'Untitled trip')
    trip.start = data.get('start')
    for entry in trip.entries:
        db.session.delete(entry)
        
    for entry_data in data.get('entries', []):
        entry = Entry(description=entry_data['description'], 
                    kind=entry_data['kind'],
                    completed=False,
                    day_index=entry_data['day_index'])
        trip.entries.append(entry)
        db.session.add(entry)

    location = data.get('location')
    if location:
        trip.location = location
        trip.unsplash_data = unsplash_api.unsplash_search(location)

    return trip
        

@app.route('/api/user/<int:user_id>/trip/', methods=['POST'])
def trip_create(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return json.dumps({
                'success': False,
                'error': 'User not found'
            }), 404
        
        body = json.loads(request.data)

        with db.session.no_autoflush:   
            trip = Trip()
            trip_update_contents(trip, body)
            user.trips.append(trip)
            db.session.add(trip)

        db.session.commit()

        return json_response(True, trip.serialize(), 200)

    except Exception as e:
        return json_resopnse(False, 'Exception: ' + str(e), 500)


@app.route('/api/trip/<int:trip_id>/', methods=['PUT'])
def trip_update(trip_id):
    try:
        body = json.loads(request.data)

        trip = Trip.query.filter_by(id=trip_id).first()
        if not trip:
            return json.dumps({
                'success': False,
                'error': 'Trip not found'
            }), 404
        
        with db.session.no_autoflush: 
            trip_update_contents(trip, body)

        db.session.commit()

        return json_response(True, trip.serialize(), 200)

    except Exception as e:
        return json.dumps({
            'success': False, 
            'error': 'Exception: ' + str(e)
        }), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
