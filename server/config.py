# Remote library imports
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
import os
import json
from dotenv import load_dotenv
load_dotenv()
# import bcrypt

# Instantiate the Flask app with configuration
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['DEBUG'] = True  # Enable debug mode
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://online_charity_manager_user:edQrCNVH1c5p73bZZtRaZWEFBpKqe8kW@dpg-cp4tac0cmk4c73eouffg-a.oregon-postgres.render.com/online_charity_manager"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
# app.config['PORT'] = 5555  # Default port
app.config['JWT_SECRET_KEY'] ='63734b761f2cdcbb8d81471b'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=120)
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
