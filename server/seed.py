import random
from app import app
from models import db, User, DonationRequest, Donation, Category
import bcrypt
from datetime import datetime

with app.app_context():

    def add_categories():
        categories = [
            {"name": "Education", "description": "Support for educational initiatives", "img": "education.jpg"},
            {"name": "Health", "description": "Funds for health services", "img": "health.jpg"},
            {"name": "Environment", "description": "Environmental conservation projects", "img": "environment.jpg"}
        ]
        for category in categories:
            cat = Category(**category)
            db.session.add(cat)
        db.session.commit()

    def add_users():
        users = [
            {"name": "John Doe", "email": "john@example.com", "password": "password123", "role": "admin", "location": "Nairobi", "description": "System administrator", "img": "john.jpg", "contacts": 123456},
            {"name": "Jane Doe", "email": "jane@example.com", "password": "password123", "role": "ngo", "location": "Kisumu", "description": "Runs an NGO focused on education", "category_id": 1, "img": "jane.jpg", "contacts": 654321}
        ]
        for user in users:
        
            hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user['_password_hash'] = hashed_password  
            del user['password']  

            new_user = User(**user)
            db.session.add(new_user)
        db.session.commit()


    def add_donation_requests():
        donation_requests = [
            {"ngo_id": 2, "admin_id": 1, "title": "School Supplies", "reason": "To buy books and uniforms", "amount_requested": 5000, "category_id": 1}
        ]
        for request in donation_requests:
            new_request = DonationRequest(**request)
            db.session.add(new_request)
        db.session.commit()

    def add_donations():
        donations = [
            {
                "donor_id": 1, 
                "donation_request_id": 1, 
                "ngo_id": 2, 
                "category_id": 1, 
                "amount": 2000, 
                "date_donated": datetime.strptime("2022-06-01", "%Y-%m-%d"),  
                "pay_method": "Credit Card"
            }
        ]
        for donation in donations:
            new_donation = Donation(**donation)
            db.session.add(new_donation)
        db.session.commit()

    if __name__ == '__main__':
        with app.app_context():
            db.drop_all()
            db.create_all()

            add_categories()
            add_users()
            add_donation_requests()
            add_donations()

            print("Database seeded successfully!")