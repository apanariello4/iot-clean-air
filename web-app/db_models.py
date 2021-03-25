from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils.types.uuid import UUIDType
from datetime import datetime


db = SQLAlchemy()


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
