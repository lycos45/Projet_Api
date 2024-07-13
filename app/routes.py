from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db_connection
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import psycopg2

main_bp = Blueprint('main', __name__)

VALID_ROLES = {'admin', 'user', 'guest'}

# Connexion des utilisateurs
@main_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, role FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user[2], password):
        access_token = create_access_token(identity={'id': user[0], 'role': user[3]})
        return jsonify({'message': 'Login successful', 'access_token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

# Test de la connexion à la base de données
"""@main_bp.route('/test_db_connection', methods=['GET'])
def test_db_connection():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            return jsonify({'message': 'Connection successful', 'result': result}), 200
        else:
            return jsonify({'message': 'Connection failed'}), 500
    except Exception as e:
        return jsonify({'message': 'Connection failed', 'error': str(e)}), 500
"""