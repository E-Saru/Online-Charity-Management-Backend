#!/usr/bin/env python3

import os
from datetime import datetime
from flask import request, jsonify, make_response, session
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api  
from models import User, DonationRequest, Donation, Category 


@app.route('/')
def index():
    return '<h1>Project Server</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)