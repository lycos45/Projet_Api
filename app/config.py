import os
from datetime import timedelta
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or \
          'postgresql://postgres:papasy45@localhost/myprojectdb'
    JWT_ACCES_TOKEN_EXPIRES =timedelta(days=1)
