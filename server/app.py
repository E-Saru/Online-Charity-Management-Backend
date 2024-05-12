#!/usr/bin/env python3

import os
from datetime import datetime
from flask import request, jsonify, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, create_access_token
from sqlalchemy.exc import IntegrityError
from config import app, db, api  
from models import User, DonationRequest, Donation, Category 


@app.route('/')
def index():
    return '<h1>Project Server</h1>'
#aunthenticate a user

class LoginResource(Resource):
    def post(self):
        email = request.json.get('email', None)
        password = request.json.get('password', None)



if __name__ == '__main__':
    app.run(port=5555, debug=True)
    