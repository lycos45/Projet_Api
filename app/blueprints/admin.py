from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

from app.db import get_db_connection

# Création du blueprint pour les routes administratives
admin_bp = Blueprint('admin', __name__)

# Route pour enregistrer un nouvel utilisateur
@admin_bp.route('/register', methods=['POST'])
def register():
    # Récupération des données JSON envoyées dans la requête
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'user')  # Rôle par défaut 'user' si non spécifié

    # Hashage du mot de passe avec Werkzeug
    password_hash = generate_password_hash(password)

    # Obtention de la connexion à la base de données
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Insertion de l'utilisateur dans la base de données
        cur.execute("INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
                    (username, password_hash, email, role))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Failed to register user: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

# Route pour créer un utilisateur (accessible seulement aux administrateurs)
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

    # Hashage du mot de passe
    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Insertion de l'utilisateur dans la base de données
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

# Route pour créer un groupe (accessible seulement aux administrateurs)
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
        # Insertion du groupe dans la base de données
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

# Route pour associer un utilisateur à un groupe (accessible seulement aux administrateurs)
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
        # Ajout de l'utilisateur au groupe dans la base de données
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

# Route pour afficher tous les prompts (accessible seulement aux administrateurs)
@admin_bp.route('/prompts', methods=['GET'])
@jwt_required()
def admin_view_prompts():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Access forbidden'}), 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, price, status FROM prompts")
    prompts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(prompts), 200
@admin_bp.route('/update_prompt_status', methods=['PATCH'])
@jwt_required()
def update_prompt_status():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    prompt_id = data.get('prompt_id')
    new_status = data.get('status')

    valid_statuses = [ 'Activé', 'À revoir']
    if new_status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE prompts SET status = %s WHERE id = %s",
            (new_status, prompt_id)
        )
        conn.commit()
        return jsonify({'message': 'Prompt status updated successfully'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': f'Failed to update prompt status: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()
# Route pour supprimer un prompt (accessible seulement aux administrateurs)
# Route pour supprimer un prompt (accessible seulement aux administrateurs)
@admin_bp.route('/delete_prompt', methods=['DELETE'])
@jwt_required()
def delete_prompt():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    prompt_id = data.get('prompt_id')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Vérification que le prompt a le statut 'À supprimer'
        cur.execute("SELECT status FROM prompts WHERE id = %s", (prompt_id,))
        prompt = cur.fetchone()
        
        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404

        if prompt[0] != 'À supprimer':
            return jsonify({'error': "Prompt status must be 'À supprimer' to be deleted"}), 400
        
        # Suppression du prompt de la base de données
        cur.execute("DELETE FROM prompts WHERE id = %s", (prompt_id,))
        conn.commit()
        return jsonify({'message': 'Prompt deleted successfully'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': f'Failed to delete prompt: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()
