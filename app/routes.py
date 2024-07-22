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


#voir tous les prompts
@main_bp.route('/view_prompts', methods=['GET'])
def view_prompts():
    """
    Route pour consulter les prompts.
    Accessible à tous, sans authentification requise.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, price FROM prompts")
    prompts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(prompts), 200
# voir un prompt specifique
@main_bp.route('/prompts/<int:prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, author_id, status, price FROM prompts WHERE id = %s", (prompt_id,))
    prompt = cur.fetchone()
    if prompt:
        prompt_data = {'id': prompt[0], 'content': prompt[1], 'author_id': prompt[2], 'status': prompt[3], 'price': prompt[4]}
        return jsonify(prompt_data), 200
    return jsonify({'error': 'Prompt not found'}), 404