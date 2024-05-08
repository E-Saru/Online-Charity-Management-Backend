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

class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email
        }

    @hybrid_property
    def password(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password.setter
    def password(self, password):
        
        self._password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def authenticate(self, password):
        
        return bcrypt.checkpw(password.encode('utf-8'), self._password_hash.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.email}>'
    

class NGO(db.Model):
    __tablename__ = 'Ngos'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    ph_number = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "ph_number": self.ph_number,
            "description": self.description,
            "category": self.category
        }

    @hybrid_property
    def password(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password.setter
    def password(self, password):
        
        self._password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def authenticate(self, password):
        
        return bcrypt.checkpw(password.encode('utf-8'), self._password_hash.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.email}>'
    

class Donor(db.Model):
    __tablename__ = 'donors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    reason = db.Column(db.Text, nullable=False)
    ph_number = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "reason": self.reason,
            "ph_number": self.ph_number
        }

    @hybrid_property
    def password(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password.setter
    def password(self, password):
        
        self._password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def authenticate(self, password):
        
        return bcrypt.checkpw(password.encode('utf-8'), self._password_hash.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.email}>'
    

class DonationRequest(db.Model):

    __tablename__ = 'donations_requests'

    id = db.Column(db.Integer, primary_key=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('Ngos.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    title = db.Column(db.String, nullable=False)
    reason = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String)


class Donation(db.Model):

    __tablename__ = 'donations'

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    donation_req_id = db.Column(db.Integer, db.ForeignKey('donations_requests.id'))
    ngo_id = db.Column(db.Integer, db.ForeignKey('Ngos.id'))
    amount_id = db.Column(db.Integer)
    date = db.Column(db.Date)

class Category(db.Model):

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String)
    description = db.Column(db.String)

if __name__ == "__main__":
    db.create_all()  