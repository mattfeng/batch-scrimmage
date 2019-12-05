# -*- coding: utf-8 -*-

import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

secrets = json.load(open('./secrets.json'))

app = Flask(__name__)
app.secret_key = secrets['secret_key']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{}:{}@{}/{}'.format(
    secrets['username'],
    secrets['password'],
    secrets['endpoint'],
    secrets['db']
    )

db = SQLAlchemy(app)

# --- MODELS ---

class PlayerBot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = True, nullable = False)
    official_name = db.Column(db.String(120), unique = True, nullable = False)
    desc = db.Column(db.Text, nullable = False)

db.create_all()

# --- ROUTES ---

@app.route('/add', methods = ['POST'])
def add_player():
    return str(request.form)

@app.route('/')
def index():
    return 'index'


