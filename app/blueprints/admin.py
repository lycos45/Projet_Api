from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

from app.db import get_db_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'user')  # Rôle par défaut si non spécifié

    # Hashage du mot de passe avec Werkzeug
    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
                    (username, password_hash, email, role))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        cur.close()
        conn.close()
        return jsonify({'error': f'Failed to register user: {str(e)}'}), 500

# Route pour créer un utilisateur (seulement pour l'admin)
@admin_bp.route('/create_user', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role')

    # Hasher le mot de passe
    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
            (username, password_hash, email, role)
        )
        conn.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Username or email already exists'}), 400
    finally:
        cur.close()
        conn.close()




# Route pour créer un groupe (seulement pour l'admin)
@admin_bp.route('/create_group', methods=['POST'])
@jwt_required()
def create_group():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    name = data.get('name')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO groups (name) VALUES (%s)",
            (name,)
        )
        conn.commit()
        return jsonify({'message': 'Group created successfully'}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Group name already exists'}), 400
    finally:
        cur.close()
        conn.close()

# Route pour associer un utilisateur à un groupe (seulement pour l'admin)
@admin_bp.route('/add_user_to_group', methods=['POST'])
@jwt_required()
def add_user_to_group():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    user_id = data.get('user_id')
    group_id = data.get('group_id')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO group_members (user_id, group_id) VALUES (%s, %s)",
            (user_id, group_id)
        )
        conn.commit()
        return jsonify({'message': 'User added to group successfully'}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'User or group does not exist'}), 400
    finally:
        cur.close()
        conn.close()

@admin_bp.route('/prompts', methods=['GET'])
@jwt_required()
def admin_view_prompts():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Access forbidden'}), 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, price, status FROM prompts")
    prompts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(prompts), 200
