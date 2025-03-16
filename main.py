from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, event
from werkzeug.routing import BaseConverter


import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

with db.session as session:
    session.add(User(name=config.USER_NAME))

