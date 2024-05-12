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
        

class SignupResource(Resource):
    def post(self):
        data = request.json
         # Validate required fields
        if 'name' not in data or 'email' not in data or 'role' not in data or 'password' not in data:
             return {"message": "Missing required fields"}, 400   
         
        user = User.query.filter_by(email=data['email']).first() 
        
        if user:
            return {"message": "User already exists"}, 400
        
        # Create a new user instance
        new_user = User(
            name=data.get('name'),
            email=data.get('email'),
            role=data.get('role'),
            location=data.get('location'),
            description=data.get('description'),
            category_id=data.get('category_id'),
            img=data.get('img'),
            contacts=data.get('contacts')
        )
        # Set password
        new_user.set_password(data['password'])
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"message": "Error creating user"}, 500
        
        access_token = create_access_token(identity=new_user.id)
        return {"user_id": new_user.id, "user_role": new_user.role, "access_token": access_token}, 201

# get all categories
class CategoryListResource(Resource):
    @jwt_required()
    def get(self):
        categories = Category.query.all()
        categories_response = [category for category in categories]
        return make_response(categories_response, 200)
     
    @jwt_required()
    def post(self):
        data = request.json
        user = User.query.get(data.get('user_id'))
        
        if not user:
            return {'message': 'User not found'}, 401
        
        if user.role != 'admin':
            return {'message': 'User is not an admin'}, 401
        
        category = Category(name=data.get('name'), 
                            description=data('description'), 
                            img=data.get('img', ''))
        
        db.session.add(category)
        db.session.commit()
        return {'message': 'Category created successfully'}, 201

api.add_resource(LoginResource, '/login')
api.add_resource(SignupResource, '/signup')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
    