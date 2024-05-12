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

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return {"message": "Invalid email or password. Please check your credentials."}, 401
        
        access_token = create_access_token(identity=user.id)
        return {
            "message": "User login success",
            "user_id": user.id, 
            "user_role": user.role, 
            "access_token": access_token}, 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
    