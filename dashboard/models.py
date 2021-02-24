import datetime
from dashboard import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Dam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="NORMAL")
    location = db.Column(db.String(60), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.String(10), nullable=False)
    longitude = db.Column(db.String(10), nullable=False)
    frl = db.Column(db.Integer, nullable=False)
    devices = db.relationship('Device', backref='installed_at', lazy=True)
    users = db.relationship('User', backref='works_at', lazy=True)

    def __repr__(self):
        return f"Dam({self.name}, {self.state}, {self.frl})"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    password = db.Column(db.String(60), nullable=False)
    dam_id = db.Column(db.Integer, db.ForeignKey('dam.id'), nullable=False)

    def __repr__(self):
        return f"User({self.username}, {self.dam_id})"


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    mac = db.Column(db.String(17), nullable=False)
    data_measured = db.Column(db.String(30), nullable=False)
    api_key = db.Column(db.String(32), unique=True, nullable=False)
    dam_id = db.Column(db.Integer, db.ForeignKey('dam.id'),nullable=False)
    data = db.relationship('Data', backref='collected_by', lazy=True)

    def __repr__(self):
        return f"Device({self.name}, {self.mac}, {self.data_measured})"

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)

    def __repr__(self):
        return f"Data({self.data}, {self.timestamp})"
