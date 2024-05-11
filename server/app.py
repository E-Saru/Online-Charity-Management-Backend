#!/usr/bin/env python3

# Standard library imports
from models import db, User, DonationRequest, Donation, Category
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify, session
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError
from datetime import datetime

#from config import db
import os

# Remote library imports
from flask import request, jsonify
from flask_restful import Resource
from datetime import datetime
from flask_cors import CORS

# Local imports
from config import app, db, api
# Add your model imports

from models import db, Room, Booking
# Views go here!
CORS(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5555"}})

@app.route('/')
def index():
    return '<h1>Project Server</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)