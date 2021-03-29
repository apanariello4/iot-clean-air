from flask import Flask, render_template, request, jsonify
from flask.templating import render_template_string
from config import Config
from flask_restful import Api, Resource
from flask_mqtt import Mqtt
from utils import has_payload, is_valid_date, is_valid_uuid
from db_models import db, Sensorfeed, BridgePredictions

appname = "iot-clean-air"
app = Flask(appname)
api = Api(app)
base_url = "/api/v1"
host_path = "http://151.81.17.207:5000"

try:
    mqtt = Mqtt(app)  # Need broker or exception thrown
except Exception:
    print(f"[ERROR] MQTT broker not found at ip {Config.MQTT_BROKER_URL}")
    pass

myconfig = Config
app.config.from_object(myconfig)

# db creation
# db = SQLAlchemy(app)


class SensorStatus(Resource):
    def get(self):
        if has_payload(request) is False:
            return "No valid json payload", 400

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
        if has_payload(request) is False:
            return "No valid json payload", 400

        id = request.get_json()['id']
        status = int(request.get_json()['status'])

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
                mqtt.publish(f'{id}/window', payload=status)

        return "OK", 200


api.add_resource(SensorStatus, f'{base_url}/sensor/status')


class SensorPollution(Resource):
    def get(self):
        if has_payload(request) is False:
            return "No valid json payload", 400

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
        if has_payload(request) is False:
            return "No valid json payload", 400

        id = request.get_json()['id']
        pol = request.get_json()['pollution']

        sf = Sensorfeed(id, pollution=pol)

        db.session.add(sf)
        db.session.commit()

        return None, 200


api.add_resource(SensorPollution, f'{base_url}/sensor/pollution')


class Client(Resource):
    def post(self):  # post from client
        if has_payload(request) is False:
            return "No valid json payload", 400

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
        if has_payload(request) is False:
            return "No valid json payload", 400

        region = request.get_json()['region'].lower()

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
        if has_payload(request) is False:
            return "No valid json payload", 400

        region = request.get_json()['region'].lower()
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


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/manage/<uuid>', methods=['GET', 'POST'])
def manage_arduino(uuid):
    # ac0a2590-85d0-11eb-8c68-3065ecc9cc2c
    if request.method == 'GET':
        if is_valid_uuid(uuid) is False:
            return render_template_string('Access Denied')
        arduino_info = Sensorfeed.query.filter_by(id=uuid).first()

        return render_template('manage_arduino.html', info=arduino_info)
    elif request.method == 'POST':
        status = request.get_json()['status']
        print(status)

        try:
            mqtt.publish(f'{id}/command', payload=f'{status}')
        except NameError:
            return "No broker enabled", 401

        return "OK", 200


@app.route('/list', methods=['GET'])
def printlist():
    sensor_list = Sensorfeed.query.order_by(Sensorfeed.id.desc()).all()
    print(len(sensor_list))

    return render_template('list.html', lista=sensor_list)


@app.route('/addinlista/<val>', methods=['POST'])
def addinlista(val):
    sf = Sensorfeed(val)

    db.session.add(sf)
    db.session.commit()
    return str(sf.id)


if __name__ == '__main__':

    # db.create_all()
    db.app = app
    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    port = 5000
    interface = '0.0.0.0'
    app.run(host=interface, port=port)
