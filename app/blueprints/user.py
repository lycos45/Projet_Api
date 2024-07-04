from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import get_db_connection
import psycopg2


user_bp = Blueprint('user', __name__)

@user_bp.route('/create_prompt', methods=['POST'])
@jwt_required()
def create_prompt():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    content = data.get('content')
    status = data.get('status', 'active')  # Par défaut à 'active' si non fourni
    price = data.get('price', 1000.0)  # Par défaut à 1000.0 si non fourni

    if not content:
        return jsonify({"error": "Content is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO prompts (content, author_id, status, price) VALUES (%s, %s, %s, %s)",
            (content, current_user_id, status, price)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Prompt created successfully"}), 201
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": f"Failed to create prompt: {str(e)}"}), 500

# Route pour voter pour un prompt (seulement pour les utilisateurs connectés)
@user_bp.route('/vote_prompt', methods=['POST'])
@jwt_required()
def vote_prompt():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['user', 'admin']:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    prompt_id = data.get('prompt_id')
    vote = data.get('vote')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO votes (user_id, prompt_id, vote) VALUES (%s, %s, %s)",
            (current_user['id'], prompt_id, vote)
        )
        conn.commit()
        return jsonify({'message': 'Vote recorded successfully'}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Error recording vote'}), 400
    finally:
        cur.close()
        conn.close()

# Route pour noter un prompt (seulement pour les utilisateurs connectés)
@user_bp.route('/rate_prompt', methods=['POST'])
@jwt_required()
def rate_prompt():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['user', 'admin']:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    prompt_id = data.get('prompt_id')
    rating = data.get('rating')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO notes (user_id, prompt_id, note) VALUES (%s, %s, %s)",
            (current_user['id'], prompt_id, rating)
        )
        conn.commit()
        return jsonify({'message': 'Rating recorded successfully'}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Error recording rating'}), 400
    finally:
        cur.close()
        conn.close()
