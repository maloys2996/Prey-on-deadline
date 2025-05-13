from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    about = db.Column(db.Text, default="")
    avatar = db.Column(db.String(140), default="uploads/default.jpg")

    rooms_owned = db.relationship('Room', backref='owner', lazy='dynamic')
    rooms = db.relationship('RoomUser', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    users = db.relationship('RoomUser', back_populates='room', cascade="all, delete-orphan")
    deadlines = db.relationship('Deadline', backref='room', lazy='dynamic')
    messages = db.relationship('Message', backref='room', lazy='dynamic')


class RoomUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    can_set_deadlines = db.Column(db.Boolean, default=False)

    room = db.relationship('Room', back_populates='users')
    user = db.relationship('User', back_populates='rooms')


class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    for_team = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(10), default='active')
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    sender = db.relationship('User', backref='messages_sent')
