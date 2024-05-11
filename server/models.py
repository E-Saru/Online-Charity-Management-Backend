from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy

from config import db

# Models go here!

# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
# from sqlalchemy.orm import validates
# from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
import bcrypt


# from app import app

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)  
    location = db.Column(db.String)
    description = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    img = db.Column(db.String)
    contacts = db.Column(db.Integer, nullable=False)

    category = db.relationship("Category", back_populates="users")

    def set_password(self, password):
        self._password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self._password_hash.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.role} {self.email}>'
    
class DonationRequest(db.Model, SerializerMixin): 
    __tablename__ = 'donationrequest'

    id = db.Column(db.Integer, primary_key=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    title = db.Column(db.String, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    amount_requested = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Integer, default=amount_requested)  
    status = db.Column(db.String, nullable=False, default='pending')

    ngo = db.relationship("User", foreign_keys=[ngo_id])
    admin = db.relationship("User", foreign_keys=[admin_id])
    donor = db.relationship("User", foreign_keys=[donor_id])
    category = db.relationship("Category", back_populates="donation_requests")

class Donation(db.Model, SerializerMixin): 
    __tablename__ = 'donations'

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    donation_request_id = db.Column(db.Integer, db.ForeignKey('donationrequest.id'))
    ngo_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    amount = db.Column(db.Integer)
    date_donated = db.Column(db.DateTime)
    pay_method = db.Column(db.String)

    donor = db.relationship("User", foreign_keys=[donor_id])
    ngo = db.relationship("User", foreign_keys=[ngo_id])
    donation_request = db.relationship("DonationRequest", back_populates="donations")
    category = db.relationship("Category", back_populates="donations")

class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    img = db.Column(db.String)

    users = db.relationship("User", back_populates="category")
    donation_requests = db.relationship("DonationRequest", back_populates="category")
    donations = db.relationship("Donation", back_populates="category")

if __name__ == "__main__":
    db.create_all() 