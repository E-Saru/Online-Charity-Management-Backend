#!/usr/bin/env python3

import os
from datetime import datetime
from flask import request, jsonify, make_response, Response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from config import app, db, api  
import cloudinary
from models import User, DonationRequest, Donation, Category 
from cloudinary.uploader import upload
from werkzeug.utils import secure_filename



          
cloudinary.config( 
  cloud_name = "dr2jfs28z", 
  api_key = "439529234124963", 
  api_secret = "0AU2lcNuml4oCF9K6VFmrBnmtxQ" 
)

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
    # implemented cloudinary here
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 401
                    
        if user.role != 'admin':
            return jsonify({'message': 'User is not an admin'}), 401

        name = request.form.get('name')
        description = request.form.get('description')
        image_files = request.files.getlist('images')

        if not name or not description:
            return jsonify({'message': 'Missing required fields'}), 400

        image_urls = []
        for image in image_files[:3]:  # select the first 3 images
            if image:  # Check if the image exists
                try:
                    response = upload(image)
                    image_urls.append(response.get('url'))
                except Exception as e:
                    db.session.rollback()  # Roll back in case of an error
                    return jsonify({'message': f'Failed to upload image: {str(e)}'}), 500

        image_urls_string = ','.join(image_urls)

        try:
            category = Category(name=name, description=description, img=image_urls_string)
            db.session.add(category)
            db.session.commit()
            # Instead of returning a Response object, return a JSON response
            return ({'message': 'Category created successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error creating category: {str(e)}'}), 500
        
        # don't know what this does, but let it be
        data = {'message': 'Category created successfully', 'data': some_data}
        json_data = json.dumps(data)
        return Response(json_data, mimetype='application/json'), 201


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
   # implemented cloudinary
    @jwt_required()
    def patch(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        
        # Using request.form and request.files for data and file handling
        name = request.form.get('name')
        description = request.form.get('description')
        image_files = request.files.getlist('images')  #uploaded images

        # change the names
        if name:
            category.name = name
        if description:
            category.description = description
        
        # upload the images
        if image_files:
            image_urls = []
            for image in image_files[:3]:  # select only 3 images
                try:
                    response = upload(image)
                    image_urls.append(response.get('url'))
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': f'Failed to upload image: {str(e)}'}), 500
            category.img = ','.join(image_urls)
        
        try:
            db.session.commit()
            return jsonify({'message': 'Category updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error updating category: {str(e)}'}), 500
    
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

#Create donation request
@app.route('/donation/request', methods=['POST'])
@jwt_required()
def create_donation_request():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    data = request.json
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if user.role != 'ngo':
        return jsonify({'message': "Only NGOs can create donation requests"}), 403
    
    
    if 'title' not in data or 'reason' not in data or 'amount_requested' not in data or 'category_name' not in data:
        return jsonify({"message": "Missing required fields"}), 40
    
    # get the category input from the db
    category = Category.query.filter_by(name=data.get('category_name')).first()
    if not category:
        return jsonify({'message': 'Category not found'}), 404

    # a new donation request
    new_donation_request = DonationRequest(
        ngo_id=current_user_id,
        title=data.get('title'),
        category_id=category.id, 
        reason=data.get('reason'),
        amount_requested=data.get('amount_requested'),
        balance=data.get('amount_requested')  # Balance should be initialized with the amount
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
            # removed the image bit since it is a list
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

    if user.role not in ['admin', 'ngo']:
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
# updated this so as to fetch the images correctly
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

    #fetch the image links by looping through
    images = ngo.img.split(',') if ngo.img else []


    ngo_details = {
        'id': ngo.id,
        'name': ngo.name,
        'email': ngo.email,
        'location': ngo.location,
        'description': ngo.description,
        'category_name': category_name,
        'images': images,
        'contacts': ngo.contacts
    }

    return jsonify(ngo_details), 200

# this endpoint enables an ngo to update their details once they are logged in
# implemented cloudinary here
@app.route('/update/profile', methods=['PUT'])
@jwt_required()
def update_ngo_profile():
    current_user_id = get_jwt_identity()
    ngo = User.query.get(current_user_id)

    if not ngo:
        return jsonify({'message': 'NGO not found'}), 404
    if ngo.role != 'ngo':
        return jsonify({'message': 'Unauthorized access. Only NGOs can update their profile.'}), 403

    description = request.form.get('description')
    if description:
        ngo.description = description

    image_files = request.files.getlist('images')  #uploaded files
    if image_files:
        image_urls = []
        for image in image_files[:3]:  # take only the first three images
            response = upload(image)
            image_urls.append(response.get('url'))
        ngo.img = ','.join(image_urls)

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating profile: " + str(e)}), 500

# This endpoint enables the admin to chnage the status of the donation request   
@app.route('/donation/requests_status/<int:id>', methods=['PUT'])
@jwt_required()
def update_donation_request_status(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403

    data = request.json
    new_status = data.get('status')

    if new_status not in ['approved', 'declined']:
        return jsonify({'message': 'Invalid status value'}), 400

    donation_request = DonationRequest.query.get(id)
    if not donation_request:
        return jsonify({'message': 'Donation request not found'}), 404

    donation_request.status = new_status
    db.session.commit()
    return jsonify({'message': 'Donation request status updated successfully'}), 200

# this endpoint gives a specific donor the related donation requests

@app.route('/donation/requests/approved', methods=['GET'])
@jwt_required()
def get_approved_donation_requests():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'donor' and user.role != 'Donor':
        return jsonify({'message': 'Unauthorized access'}), 403

    approved_requests = DonationRequest.query.filter_by(status='approved').all()
    requests_data = [{
        'id': req.id,
        'title': req.title,
        'reason': req.reason,
        'amount_requested': req.amount_requested,
        'ngo_id': req.ngo_id
    } for req in approved_requests]

    return jsonify(requests_data), 200

# this endpoint enables the donors make donations
@app.route('/make/donation', methods=['POST'])
@jwt_required()
def make_donation():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'donor':
        return jsonify({'message': 'Unauthorized access'}), 403

    data = request.json
    donation_request_id = data.get('donation_request_id')
    amount = data.get('amount')

    donation_request = DonationRequest.query.get(donation_request_id)
    if donation_request.status != 'approved':
        return jsonify({'message': 'This donation request is not approved'}), 400

    
    donation_request.balance -= amount
    new_donation = Donation(donor_id=user_id, donation_request_id=donation_request_id, amount=amount)
    db.session.add(new_donation)
    db.session.commit()

    return jsonify({'message': 'Donation made successfully'}), 200

# This endpoint filters the donation requests by category name
# should be used by the donor
@app.route('/donation-requests/<string:category_name>', methods=['GET'])
@jwt_required()
def get_donation_requests_by_category_name(category_name):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user or current_user.role != 'donor':
        return jsonify({'message': 'Access denied'}), 403

    
    category = Category.query.filter(Category.name.ilike(f"%{category_name}%")).first()
    if not category:
        return jsonify({'message': 'Category not found'}), 404

    
    donation_requests = DonationRequest.query.filter_by(category_id=category.id).join(User, User.id == DonationRequest.ngo_id).all()


    donation_requests_data = [{
        'id': req.id,
        'ngo_name': req.ngo.name,
        'category_name': category.name,
        'title': req.title,
        'reason': req.reason,
        'amount_requested': req.amount_requested,
        'balance': req.balance,
        'status': req.status
    } for req in donation_requests]

    return jsonify(donation_requests_data), 200

# This endpoint just gets a list of categories for the dropdown
@app.route('/list/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()  
    category_names = [category.name for category in categories] 

    return jsonify(category_names), 200