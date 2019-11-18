import json
from db import db, User, Trip, Entry
from flask import Flask, request

app = Flask(__name__)
db_filename = 'app.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/api/users/', methods=['GET'])
def user_get_all():
    return json.dumps({
        'success': True,
        'data': [user.serialize() for user in User.query.all()]
    }), 200


@app.route('/api/user/<int:user_id>/', methods=['GET'])
def user_get_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return json.dumps({
            'success': True, 
            'data': user.serialize()
        }), 200

    else:
        return json.dumps({
            'success': False, 
            'error': 'User not found'
        }), 404


@app.route('/api/users/', methods=['POST'])
def user_create():
    try:
        body = json.loads(request.data)
        user = User(name=body.get('name'))
        db.session.add(user)
        db.session.commit()

        return json.dumps({ 
            'success': True,
            'data': user.serialize()
        }), 200

    except Exception as e:
        return json.dumps({
            'success': False, 
            'error': 'Exception: ' + str(e)
        }), 400


@app.route('/api/users/delete_all/', methods=['DELETE'])
def user_delete_all():
    User.query.delete()
    db.session.commit()

    return json.dumps({ 
        'success': True
    }), 200


def trip_update_contents(trip, data):
    trip.name = data.get('name', 'Untitled trip')
    trip.start = data.get('start')
    trip.entries = []
    for entry_data in data.get('entries', []):
        entry = Entry(description=entry_data['description'], 
                    kind=entry_data['kind'],
                    completed=False,
                    day_index=entry_data['day_index'])
        trip.entries.append(entry)
        db.session.add(entry)
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

        return json.dumps({ 
            'success': True,
            'data': trip.serialize()
        }), 200

    except Exception as e:
        return json.dumps({
            'success': False, 
            'error': 'Exception: ' + str(e)
        }), 500


@app.route('/api/trip/<int:trip_id>', methods=['PUT'])
def trip_update(trip_id):
    try:
        body = json.loads(request.data)

        trip = Trip.query.filter_by(trip_id=trip_id).first()
        if not trip:
            return json.dumps({
                'success': False,
                'error': 'Trip not found'
            }), 404
        
        with db.session.no_autoflush:   
            trip_update_contents(trip, body)
            user.trips.append(trip)

        db.session.commit()

        return json.dumps({ 
            'success': True,
            'data': trip.serialize()
        }), 200

    except Exception as e:
        return json.dumps({
            'success': False, 
            'error': 'Exception: ' + str(e)
        }), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
