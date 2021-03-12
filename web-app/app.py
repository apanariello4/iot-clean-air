from flask import Flask
from config import Config
from flask import render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_restful import Api, Resource
from flask_mqtt import Mqtt


appname = "iot-clean-air"
app = Flask(appname)
api = Api(app)
base_url = "/api/v1"
host_path = "http://151.81.17.207:5000"
mqtt = Mqtt(app)

myconfig = Config
app.config.from_object(myconfig)

# db creation
db = SQLAlchemy(app)


class Sensorfeed(db.Model):
    # id arduino | stato finestra | timestamp

    id = db.Column('id', db.Integer, primary_key=True)
    status = db.Column('status', db.Boolean)
    pollution = db.Column('pollution', db.Integer)
    timestamp = db.Column(db.DateTime(timezone=True),
                          nullable=False,  default=datetime.utcnow)

    def __init__(self, id, pollution=None, status=None):
        self.id = id
        self.status = status
        self.pollution = pollution

    # aggiungi update


class SensorStatus(Resource):
    def get(self):
        id = request.get_json()['id']

        if id is None:
            return "id field is not valid", 400

        sensor = Sensorfeed.query.filter_by(id=id).first()
        if sensor is None:
            return f"No sensor with this id: {id} in db", 400
        status = sensor.status
        return f'Window Status: {status}', 200

    def post(self): # post from arduino when changed window status

        id = request.get_json()['id']
        status = request.get_json()['status']

        if id is None:
            return "id field is not valid", 400

        if status is None or status not in [0, 1]:
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
                mqtt.publish(f'{id}/window', payload=f'{status}')

        return "OK", 200


api.add_resource(SensorStatus, f'{base_url}/sensor/status')


class SensorPollution(Resource):
    # controlli su input
    def get(self):
        id = request.get_json()['id']

        if id is None:
            return "id field is not valid", 400

        sensor = Sensorfeed.query.filter_by(id=id).first()

        if sensor is None:
            return f"No sensor with this id: {id} in db", 400

        pol = sensor.pollution
        return f'Pollution: {pol}', 200

    def post(self):
        print(request.get_json())
        id = request.get_json()['id']
        pol = request.get_json()['pollution']

        sf = Sensorfeed(id, pollution=pol)

        db.session.add(sf)
        db.session.commit()

        return None, 200


api.add_resource(SensorPollution, f'{base_url}/sensor/pollution')


class Client(Resource):
    def post(self): #post from client
        id = request.get_json()['id']
        status = request.get_json()['status']

        if id is None:
            return "id field is not valid", 400

        if status is None or status not in [0, 1]:
            return "status field is not valid", 400

        sensor = Sensorfeed.query.filter_by(id=id).first()

        if sensor is None:
            return "No sensors found", 400
        else:
            if sensor.status != status:
                mqtt.publish(f'{id}/command', payload=f'{status}')

        return None, 200


api.add_resource(Client, f'{base_url}/sensor/command')


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
