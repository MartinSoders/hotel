from datetime import date, timedelta
from flask import jsonify
from app import db, ma
from app.models import User

from . import main

class UserSchema(ma.Schema):
    class Meta:
        fields = ('forename', 'surname', 'birthday', ...)


@main.route('/', methods=('GET',))
def get_users():

    start_range = date.today() + timedelta(years=-30)
    end_range = date.today() + timedelta(years=-18)

    users = db.session.query(User).filter(User.birthday.between(start_range, end_range)).all()

    users_schema = UserSchema(many=True)

    return jsonify(users_schema.dump(users))     