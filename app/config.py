import os
from datetime import timedelta

class Config:
    # Clé secrète pour la sécurité de Flask (utilisée pour les sessions)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    
    # Clé secrète pour JWT (utilisée pour signer les tokens JWT)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'
    
    # URL de connexion à la base de données PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL') or \
                   'postgresql://postgres:papasy45@localhost/myprojectdb'
    
    # Durée de validité du token JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
