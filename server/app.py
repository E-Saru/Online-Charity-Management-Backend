#!/usr/bin/env python3

import os
from datetime import datetime
from flask import request, jsonify, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
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

# get all categories for the admin
class CategoryListResource(Resource):
    @jwt_required()
    def get(self):
        categories = Category.query.all()

        categories_data = []
        for category in categories:
            category_info = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "img": category.img
            }
            categories_data.append(category_info)
        return jsonify(categories_data)
        
        


    
    # admin should be able to add categories
    @jwt_required()
    def post(self):
        data = request.json
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return {'message': 'User not found'}, 401
        
        if user.role != 'admin':
            return {'message': 'User is not an admin'}, 401
        
        category = Category(name=data.get('name'), 
                            description=data.get('description'), 
                            img=data.get('img', ''))
        
        db.session.add(category)
        db.session.commit()
        return {'message': 'Category created successfully'}, 201
    

class CategoryResource(Resource):
    @jwt_required()
    def get(self, category_id):
        category = Category.query.get(category_id)
        if category:
            category_data = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "img": category.img
            }
            return jsonify(category_data)
        else:
            return ({'error': 'Category not found'}), 404 
   
    @jwt_required()
    def patch(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            return {'message': 'Category not found'}, 404
        
        data = request.json

        if 'name' in data:
            category.name = data.get('name')
        if 'description' in data:
            category.description = data.get('description')
        if 'img' in data:
            category.img = data.get('img')

        db.session.commit()
        return {'message': 'Category updated successfully'}, 200  
    
    @jwt_required()
   # sorted the delete problem, the user id was not gooten from the token 
    def delete(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            return {'message': 'Category not found'}, 404

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {'message': 'User not found'}, 401
        
        if user.role != 'admin':
            return {'message': 'User is not an admin'}, 401

        db.session.delete(category)
        db.session.commit()
        return {'message': 'Category deleted successfully'}, 200

api.add_resource(LoginResource, '/login')
api.add_resource(SignupResource, '/signup')
api.add_resource(CategoryListResource, '/categories')
api.add_resource(CategoryResource, '/categories/<int:category_id>')


# This endpoint gets all the donation requests based on the auth of the user

@app.route('/donation-requests', methods=['GET'])
@jwt_required()
def get_donation_requests():
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user_role = user.role
    
    if user_role not in ['admin', 'donor', 'ngo']:
        return jsonify({'message': 'Unauthorized access'}), 403

    if user_role == 'admin':
        donation_requests = DonationRequest.query.all()
    elif user_role == 'donor':  # donors
        donation_requests = DonationRequest.query.filter_by(donor_id=user.id).all()
    else:
        donation_requests = DonationRequest.query.filter_by(ngo_id=user.id).all()
    
    donation_requests_list = []
    for request in donation_requests:
        category = Category.query.get(request.category_id)
        ngo = User.query.get(request.ngo_id)
        donor = User.query.get(request.donor_id)
        
        donation_requests_list.append({
            'id': request.id,
            'ngo_id': request.ngo_id,
            'ngo_name': ngo.name if ngo else None,
            'category_id': request.category_id,
            'category_name': category.name if category else None,
            'donor_id': request.donor_id,
            'donor_name': donor.name if donor else None,
            'title': request.title,
            'reason': request.reason,
            'amount_requested': request.amount_requested,
            'balance': request.balance,
            'status': request.status
        })
    
    return jsonify(donation_requests_list), 200

@app.route('/donation_requests', methods=['POST'])
@jwt_required()
def create_donation_request():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    data = request.json
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if user.role != 'ngo':
        return jsonify({'message': "Only NGOs can create donation requests"}), 403
    
     # Validate required fields
    if 'title' not in data or 'reason' not in data or 'amount_requested' not in data or 'category_id' not in data:
        return jsonify({"message": "Missing required fields"}), 40

    # Create a new donation request
    new_donation_request = DonationRequest(
        ngo_id=current_user_id,
        title=data.get('title'),
        category_id=data.get('category_id'),
        reason=data.get('reason'),
        amount_requested=data.get('amount_requested'),
        balance = data.get('balance'),
        
    )

    db.session.add(new_donation_request)

    try:
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating donation request"}), 500

    return jsonify({"message": "Donation request created successfully"}), 201

#This endpoint gets all the donations made, shows the admin

@app.route('/admin/donations', methods=['GET'])
@jwt_required()
def get_all_donations():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    
    donations = Donation.query.all()
    donations_list = []

    for donation in donations:
        ngo = User.query.get(donation.ngo_id)
        donor = User.query.get(donation.donor_id)
        category = Category.query.get(donation.category_id)

        donations_list.append({
            'id': donation.id,
            'ngo_id': donation.ngo_id,
            'ngo_name': ngo.name if ngo else None,
            'donor_id': donation.donor_id,
            'donor_name': donor.name if donor else None,
            'category_id': donation.category_id,
            'category_name': category.name if category else None,
            'amount': donation.amount,
            'date_donated': donation.date_donated.strftime('%Y-%m-%d'),
            'pay_method': donation.pay_method
        })
    
    return jsonify(donations_list), 200


# This endpoint gets all donations made by a certain donor, shows the donor

@app.route('/donor/donations', methods=['GET'])
@jwt_required()
def get_donor_donations():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.role != 'donor':
        return jsonify({'message': 'Unauthorized access'}), 403

    
    donations = Donation.query.filter_by(donor_id=user.id).all()
    donations_list = []

    for donation in donations:
        ngo = User.query.get(donation.ngo_id)
        category = Category.query.get(donation.category_id)

        donations_list.append({
            'id': donation.id,
            'ngo_id': donation.ngo_id,
            'ngo_name': ngo.name if ngo else None,
            'category_id': donation.category_id,
            'category_name': category.name if category else None,
            'amount': donation.amount,
            'date_donated': donation.date_donated.strftime('%Y-%m-%d'),
            'pay_method': donation.pay_method
        })
    
    return jsonify(donations_list), 200


# gets the donations received by a single ngo, shows the ngo

@app.route('/ngo/donations', methods=['GET'])
@jwt_required()
def get_ngo_donations():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.role != 'ngo':
        return jsonify({'message': 'Unauthorized access'}), 403

    
    donations = Donation.query.filter_by(ngo_id=user.id).all()
    donations_list = []

    for donation in donations:
        donor = User.query.get(donation.donor_id)
        category = Category.query.get(donation.category_id)

        donations_list.append({
            'id': donation.id,
            'ngo_id': user.id, 
            'ngo_name': user.name,
            'donor_id': donation.donor_id,
            'donor_name': donor.name if donor else None,
            'category_id': donation.category_id,
            'category_name': category.name if category else None,
            'amount': donation.amount,
            'date_donated': donation.date_donated.strftime('%Y-%m-%d'),
            'pay_method': donation.pay_method
        })
    
    return jsonify(donations_list), 200


# This endpoint gets the list of ngos, should be used by admin and probably the donors

@app.route('/ngos', methods=['GET'])
@jwt_required()
def get_ngos():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.role not in ['admin', 'donor']:
        return jsonify({'message': 'Unauthorized access'}), 403

    ngos = User.query.filter(User.role == 'ngo').all()
    ngos_list = []

    for ngo in ngos:

        category_name = Category.query.get(ngo.category_id).name if Category.query.get(ngo.category_id) else 'category not assigned'
        
        ngos_list.append({
            'id': ngo.id,
            'name': ngo.name,
            'email': ngo.email,
            'location': ngo.location,
            'description': ngo.description,
            'category_name': category_name,
            'img': ngo.img,
            'contacts': ngo.contacts
        })
    
    return jsonify(ngos_list), 200


# This endpoint gets a list of all the donors, should only be accessible to the admin

@app.route('/donors', methods=['GET'])
@jwt_required()
def get_donors():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403

    donors = User.query.filter_by(role='donor').all()
    donors_list = []

    for donor in donors:
        donors_list.append({
            'name': donor.name,
            'email': donor.email,
            'location': donor.location,
            'description': donor.description,
            'contacts': donor.contacts
        })
    
    return jsonify(donors_list), 200

# Endpoint gets a single ngo, it should be used by the admin and donor pages

@app.route('/ngos/<int:ngo_id>', methods=['GET'])
@jwt_required()
def get_ngo(ngo_id):
    # Authenticate and authorize
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.role not in ['admin', 'donor']:
        return jsonify({'message': 'Unauthorized access'}), 403

    
    ngo = User.query.filter_by(id=ngo_id, role='ngo').first()
    if not ngo:
        return jsonify({'message': 'NGO not found'}), 404

    
    category_name = Category.query.get(ngo.category_id).name if Category.query.get(ngo.category_id) else 'No category assigned'

    
    ngo_details = {
        'id': ngo.id,
        'name': ngo.name,
        'email': ngo.email,
        'location': ngo.location,
        'description': ngo.description,
        'category_name': category_name,
        'img': ngo.img,
        'contacts': ngo.contacts
    }

    return jsonify(ngo_details), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)
    