from flask import Flask, render_template, request, send_from_directory, redirect, flash
from flask.helpers import url_for
from flask.templating import render_template_string
from config import Config
from flask_restful import Api, Resource
from flask_mqtt import Mqtt
from utils import has_payload, is_valid_date, is_valid_uuid
from db_models import db, Sensor, BridgePredictions
import os

appname = "iot-clean-air"
app = Flask(appname)
api = Api(app)
base_url = "/api/v1"
host_path = "http://151.81.28.142:5000"

try:
    mqtt = Mqtt(app)  # Need broker or exception thrown
except Exception:
    print(
        f"\033[91m [ERROR] MQTT broker not found at ip {Config.MQTT_BROKER_URL} \033[00m")
    pass

myconfig = Config
app.config.from_object(myconfig)


class SensorStatus(Resource):
    """Sensor status api.

        -GET request return the status of the window given the uuid.
        -POST request insert the new status of the window in the db and publish on
        {id}/command topic to alert clients.

    """

    def get(self):

        id = request.args.get('uuid', default=None)

        if is_valid_uuid(id) is False:
            return "id field is not valid", 400

        sensor = Sensor.query.filter_by(id=id).first()

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
        region = request.get_json()['region']

        print(request.get_json())

        if is_valid_uuid(id) is False:
            return "id field is not valid", 400

        if status is None or status not in {0, 1}:
            return "status field is not valid", 400

        if region is None:
            return "region field is not valid", 400

        sensor = Sensor.query.filter_by(id=id).first()

        if sensor is None:
            sf = Sensor(id, status=status, region=region)
            db.session.add(sf)
            db.session.commit()
            mqtt.publish(f'{id}/window', payload=status)
            return "OK", 201

        elif sensor.status != status:
            sensor.status = status
            db.session.commit()
            mqtt.publish(f'{id}/window', payload=status)

        return "OK", 204


api.add_resource(SensorStatus, f'{base_url}/sensor/status')


class SensorPollution(Resource):
    """Sensor pollution api.

        -GET request returns the pollution in the area of the arduino given the uuid
        -POST request insert in the db the pollution of the arduino given the uuid
    """

    def get(self):

        id = request.args.get('uuid', default=None)

        if is_valid_uuid(id) is False:
            return "id field is not valid", 400

        sensor = Sensor.query.filter_by(id=id).first()

        if sensor is None:
            return f"No sensor with this id: {id} in db", 400

        r = {
            'id': id,
            'pollution': sensor.pollution
        }

        return r, 200

    def post(self):
        # arriva regione e valore
        if has_payload(request) is False:
            return "No valid json payload", 400

        region = request.get_json()['region'].lower()
        pol = request.get_json()['pollution']

        if region is None or pol is None:
            return "No valid json payload", 400

        try:
            pol = int(pol)
        except Exception:
            return "Pollution is not a valid integer", 400

        if pol not in range(0, 500):
            return "No valid pollution value", 400

        if Sensor.query.filter_by(region=region).first() is None:
            return "No sensors with that region", 403

        db.session.query(Sensor).filter_by(
            region=region).update({'pollution': pol})

        db.session.commit()

        return None, 201


api.add_resource(SensorPollution, f'{base_url}/sensor/pollution')


class RemoveSensor(Resource):
    def get(self):
        id = request.args.get('uuid', default=None)

        if is_valid_uuid(id) is False:
            return "id field is not valid", 400

        sensor = Sensor.query.filter_by(id=id).first()

        if sensor is None:
            return f"No sensor with this id: {id} in db", 400

        Sensor.query.filter_by(id=id).delete()
        db.session.commit()

        return "Removed", 200


api.add_resource(RemoveSensor, f'{base_url}/sensor/remove')


class Client(Resource):
    """Client api

        -POST request from the clients (web or mobile) that publish a mqtt message on
        the {id}/command topic to let the arduino change the status of the window
    """

    def post(self):  # post from client
        if has_payload(request) is False:
            return "No valid json payload", 400

        id = request.get_json()['id']
        status = request.get_json()['status']

        if is_valid_uuid(id) is False:
            return "id field is not valid", 400

        if status is None or status not in {0, 1}:
            return "status field is not valid", 400

        sensor = Sensor.query.filter_by(id=id).first()

        if sensor is None:
            return "No sensors found", 404
        else:
            if sensor.status != status:
                mqtt.publish(f'{id}/command', payload=f'{status}')

        return None, 204


api.add_resource(Client, f'{base_url}/sensor/command')


class Predictions(Resource):
    """Predictions api.

        -GET request returns the predictions of pollution value for the next 3 hours
        given the region.
        -POST request insert the predictions in the db.
    """

    def get(self):

        region: str = request.args.get('region', default=None)

        if region is None:
            return None, 400

        region = region.lower()

        db_region = BridgePredictions.query.filter_by(region=region).first()

        if not db_region:
            return "Region not present in db", 404

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

        return None, 201


api.add_resource(Predictions, f'{base_url}/predictions')


@app.errorhandler(404)
def page_not_found(error):
    return 'Error', 404


@app.route('/login', methods=['GET'])
def login():
    '''Login page missing backend
    '''
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        '''Shows add arduino page
        '''
        return render_template('home.html')

    if request.method == 'POST':
        '''Adds arduino
            form:
              - uuid: <uuid>
              - region: <region>
        '''

        new_arduino: str = request.form.get('uuid')
        region: str = request.form.get('region')

        if not new_arduino or is_valid_uuid(new_arduino.strip()) is False:
            return render_template('home.html', error="UUID is not valid")

        new_arduino = new_arduino.strip()

        if Sensor.query.filter_by(id=new_arduino).first() is not None:
            return render_template('home.html', error="This Arduino is already registered")

        if region is None:
            region = 'modena'

        region = region.strip().lower()

        new_entry = Sensor(id=new_arduino, region=region, status=0)

        db.session.add(new_entry)
        db.session.commit()

        flash('Arduino added succesfully, redirecting to the list of Arduino', 'info')
        return redirect(url_for('printlist'))


@app.route('/manage/<uuid>', methods=['GET', 'POST'])
def manage_arduino(uuid: str):
    """Page to manage the arduino.

    We can read information and send open/close commands.
    """
    if request.method == 'GET':
        if is_valid_uuid(uuid) is False:
            return render_template_string('Arduino not found')
        arduino_info = Sensor.query.filter_by(id=uuid).first()

        if arduino_info is None:
            return render_template_string('Arduino not found')

        return render_template('manage_arduino.html', info=arduino_info)

    elif request.method == 'POST':
        """When open/close button in this page gets pressed we publish a mqtt message
        to open/close the window.

        """
        status = request.get_json()['status']

        command = 'OFF' if status == 0 else 'ON'

        try:
            mqtt.publish(f'{uuid}/command', payload=f'{command}')
        except NameError:
            return "No broker enabled", 401

        return "OK", 200


@app.route('/list', methods=['GET'])
def printlist():
    """List of all the arduinos registered in the db.

    """
    sensor_list = Sensor.query.order_by(Sensor.id.desc()).all()

    return render_template('list.html', lista=sensor_list)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':

    # db.create_all()
    db.app = app
    db.init_app(app)  # initialize the db
    with app.test_request_context():
        db.create_all()

    port = 5000
    interface = '0.0.0.0'
    app.run(host=interface, port=port)  # start the server
