from flask import Flask, render_template, request, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from flask_restful import Api, Resource
from flask_mqtt import Mqtt
from sqlalchemy_utils import UUIDType
from uuid import UUID


appname = "iot-clean-air"
app = Flask(appname)
api = Api(app)
base_url = "/api/v1"
host_path = "http://151.81.17.207:5000"
# mqtt = Mqtt(app)  # Need broker or exception thrown

myconfig = Config
app.config.from_object(myconfig)

# db creation
db = SQLAlchemy(app)


def is_valid_uuid(uuid_to_test: str, version=4) -> bool:
    """Check to see if a string is a valid uuid

    Args:
        uuid_to_test (str): uuid to test
        version (int, optional): uuid version to use. Defaults to 4.

    Returns:
        bool: is a valid uuid or not
    """
    uuid_to_test = uuid_to_test.replace('-', '')
    try:
        val = UUID(uuid_to_test, version=version)
    except ValueError:
        return False


def is_valid_date(date: str, date_format='%Y-%m-%d %H:%M:%S') -> bool:
    """Check if string is valid date given a date_format

    Args:
        date (str): date string
        date_format (str, optional): format to validate against. Defaults to '%Y-%m-%dT%H%M%S'.

    Returns:
        bool: true if valid date, false otherwise
    """
    try:
        date_obj = datetime.strptime(date, date_format)
        return date_obj
    except ValueError:
        return False


class Sensorfeed(db.Model):
    # id arduino | window status | pollution value | timestamp

    id = db.Column('id', UUIDType(binary=False), primary_key=True)
    status = db.Column('status', db.Boolean)
    pollution = db.Column('pollution', db.Integer)
    timestamp = db.Column(db.DateTime(timezone=True),
                          nullable=False,  default=datetime.utcnow)

    def __init__(self, id, pollution=None, status=None):
        self.id = id
        self.status = status
        self.pollution = pollution

    # aggiungi update


class BridgePredictions(db.Model):

    # region | pm_10_1h | pm_25_1h | pm_10_2h | pm_25_2h | pm_10_3h | pm_25_3h | timestamp

    region = db.Column('region', db.String, primary_key=True)
    pm_10_1h = db.Column('pm_10_1h', db.Integer)
    pm_25_1h = db.Column('pm_25_1h', db.Integer)
    pm_10_2h = db.Column('pm_10_2h', db.Integer)
    pm_25_2h = db.Column('pm_25_2h', db.Integer)
    pm_10_3h = db.Column('pm_10_3h', db.Integer)
    pm_25_3h = db.Column('pm_25_3h', db.Integer)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(self, region, pm_10_1h, pm_25_1h, pm_10_2h, pm_25_2h, pm_10_3h, pm_25_3h, timestamp) -> None:
        self.region = region
        self.pm_10_1h = pm_10_1h
        self.pm_25_1h = pm_25_1h
        self.pm_10_2h = pm_10_2h
        self.pm_25_2h = pm_25_2h
        self.pm_10_3h = pm_10_3h
        self.pm_25_3h = pm_25_3h
        self.timestamp = timestamp


class SensorStatus(Resource):
    def get(self):
        id = request.get_json()['id']

        if is_valid_uuid(id) is False:
            return "id field is not valid", 400

        sensor = Sensorfeed.query.filter_by(id=id).first()

        if sensor is None:
            return f"No sensor with this id: {id} in db", 400

        r = {
            'id': id,
            'status': sensor.status
        }
        return r, 200

    def post(self):  # post from arduino when changed window status

        id = request.get_json()['id']
        status = request.get_json()['status']

        if is_valid_uuid(id) is False:
            return "id field is not valid", 400

        if status is None or status not in {0, 1}:
            return "status field is not valid", 400

        sensor = Sensorfeed.query.filter_by(id=id).first()

        if sensor is None:
            sf = Sensorfeed(id, status=status)
            db.session.add(sf)
            db.session.commit()
        else:
            if sensor.status != status:
                sensor.status = status
                db.session.commit()
                #mqtt.publish(f'{id}/window', payload=status)

        return "OK", 200


api.add_resource(SensorStatus, f'{base_url}/sensor/status')


class SensorPollution(Resource):
    # controlli su input
    def get(self):
        id = request.get_json()['id']

        if is_valid_uuid(id) is False:
            return "id field is not valid", 400

        sensor = Sensorfeed.query.filter_by(id=id).first()

        if sensor is None:
            return f"No sensor with this id: {id} in db", 400

        r = {
            'id': id,
            'pollution': sensor.pollution
        }

        return r, 200

    def post(self):
        id = request.get_json()['id']
        pol = request.get_json()['pollution']

        sf = Sensorfeed(id, pollution=pol)

        db.session.add(sf)
        db.session.commit()

        return None, 200


api.add_resource(SensorPollution, f'{base_url}/sensor/pollution')


class Client(Resource):
    def post(self):  # post from client
        id = request.get_json()['id']
        status = request.get_json()['status']

        if is_valid_uuid(id) is False:
            return "id field is not valid", 400

        if status is None or status not in {0, 1}:
            return "status field is not valid", 400

        sensor = Sensorfeed.query.filter_by(id=id).first()

        if sensor is None:
            return "No sensors found", 400
        else:
            if sensor.status != status:
                mqtt.publish(f'{id}/command', payload=f'{status}')

        return None, 200


api.add_resource(Client, f'{base_url}/sensor/command')


class Predictions(Resource):
    def get(self):
        region = request.get_json()['region']

        if region is None:
            return None, 400

        db_region = BridgePredictions.query.filter_by(region=region).first()

        if not db_region:
            return None, 400

        r = {
            'region': db_region.region,
            'pm_10_1h': db_region.pm_10_1h,
            'pm_25_1h': db_region.pm_25_1h,
            'pm_10_2h': db_region.pm_10_2h,
            'pm_25_2h': db_region.pm_25_2h,
            'pm_10_3h': db_region.pm_10_3h,
            'pm_25_3h': db_region.pm_25_3h,
            'timestamp': str(db_region.timestamp)
        }

        return r, 200

    def post(self):
        region = request.get_json()['region']
        pm = request.get_json()['pm']
        timestamp = request.get_json()['timestamp']

        if region is None:
            return None, 400

        if pm is None or len(pm) != 6:
            return None, 400

        timestamp = is_valid_date(timestamp)
        if timestamp is False:
            return None, 400

        db_region = BridgePredictions.query.filter_by(region=region).first()

        if db_region:
            BridgePredictions.query.filter_by(region=region).delete()

        db_region = BridgePredictions(region, *pm, timestamp)
        db.session.add(db_region)
        db.session.commit()

        return None, 200


api.add_resource(Predictions, f'{base_url}/predictions')


@app.errorhandler(404)
def page_not_found(error):
    return 'Errore', 404


@app.route('/')
def testoHTML():
    if request.accept_mimetypes['application/json']:
        return jsonify({'text': 'I Love IoT'}), '200 OK'
    else:
        return '<h1>I love IoT</h1>'


@app.route('/lista', methods=['GET'])
def stampalsita():
    elenco = Sensorfeed.query.order_by(Sensorfeed.id.desc()).limit(10).all()
    #elenco = db.q

    return render_template('lista.html', lista=elenco)


@app.route('/addinlista/<val>', methods=['POST'])
def addinlista(val):
    sf = Sensorfeed(val)

    db.session.add(sf)
    db.session.commit()
    return str(sf.id)


if __name__ == '__main__':

    db.create_all()

    port = 5000
    interface = '0.0.0.0'
    app.run(host=interface, port=port)
