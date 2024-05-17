# Remote library imports
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
# import bcrypt

# Instantiate the Flask app with configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True  # Enable debug mode
app.config['PORT'] = 5555  # Default port
app.config['JWT_SECRET_KEY'] ='63734b761f2cdcbb8d81471b'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)
# Metadata for database schema conventions
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

# Setup Flask-RESTful API
api = Api(app)
# initialize a JWTManager
jwt = JWTManager(app)
# Setup CORS
CORS(app)
