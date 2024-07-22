from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import get_db_connection
from app.utils import update_prompt_price,count_votes_and_update_status
import psycopg2

user_bp = Blueprint('user', __name__)

# Route pour créer un prompt
@user_bp.route('/create_prompt', methods=['POST'])
@jwt_required()
def create_prompt():
    current_user = get_jwt_identity()
    current_user_id = current_user['id']
    data = request.get_json()

    # Extraire les données du JSON
    content = data.get('content')

    if not content:
        return jsonify({"error": "Content is required"}), 400

    # Définir le statut par défaut à 'En attente' et le prix par défaut à 1000
    status = 'En attente'
    price = 1000.0

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO prompts (content, author_id, status, price) VALUES (%s, %s, %s, %s)",
            (content, current_user_id, status, price)
        )
        conn.commit()
        return jsonify({"message": "Prompt created successfully"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Failed to create prompt: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()


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
            "INSERT INTO votes (user_id, prompt_id, vote_value) VALUES (%s, %s, %s)",
            (current_user['id'], prompt_id, vote)
        )
        conn.commit()

        count_votes_and_update_status(prompt_id, cur)
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
    rating = data.get('score')

    if rating < -10 or rating > 10:
        return jsonify({'error': 'Invalid score, it must be between -10 and 10'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Vérifier que le prompt a le statut "Activé"
        cur.execute("SELECT status, author_id FROM prompts WHERE id = %s", (prompt_id,))
        prompt = cur.fetchone()
        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404

        status, author_id = prompt
        if status != 'Activé':
            return jsonify({'error': 'Prompt is not active'}), 400
        
        # Vérifier que l'utilisateur ne note pas son propre prompt
        if author_id == current_user['id']:
            return jsonify({'error': 'You cannot rate your own prompt'}), 400

        # Insérer la note dans la base de données
        cur.execute(
            "INSERT INTO notes (user_id, prompt_id, score) VALUES (%s, %s, %s)",
            (current_user['id'], prompt_id, rating)
        )
        conn.commit()

        # Recalculer le prix après avoir noté le prompt
        update_prompt_price(prompt_id, cur)
        conn.commit()

        return jsonify({'message': 'Rating recorded successfully'}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Error recording rating'}), 400
    finally:
        cur.close()
        conn.close()

# Route pour demander la suppression d'un prompt (accessible aux utilisateurs authentifiés)
@user_bp.route('/request_delete_prompt', methods=['PATCH'])
@jwt_required()
def request_delete_prompt():
    current_user = get_jwt_identity()

    data = request.get_json()
    prompt_id = data.get('prompt_id')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Vérification que le prompt existe et appartient à l'utilisateur actuel
        cur.execute("SELECT author_id, status FROM prompts WHERE id = %s", (prompt_id,))
        prompt = cur.fetchone()

        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404

        if prompt[0] != current_user['id']:
            return jsonify({'error': 'You can only request deletion of your own prompts'}), 403
        
        if prompt[1] == 'À supprimer':
            return jsonify({'error': 'Prompt is already marked for deletion'}), 400

        # Mise à jour du statut du prompt à 'À supprimer'
        cur.execute(
            "UPDATE prompts SET status = %s WHERE id = %s",
            ('À supprimer', prompt_id)
        )
        conn.commit()
        return jsonify({'message': 'Prompt marked for deletion successfully'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': f'Failed to mark prompt for deletion: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

# Route pour modifier un prompt (accessible aux utilisateurs authentifiés)
@user_bp.route('/modify_prompt', methods=['PATCH'])
@jwt_required()
def modify_prompt():
    current_user = get_jwt_identity()
    current_user_id = current_user['id']
    data = request.get_json()

    prompt_id = data.get('prompt_id')
    new_content = data.get('new_content')
    new_price = data.get('new_price')

    if not prompt_id:
        return jsonify({"error": "Prompt ID is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, content, author_id, status, price FROM prompts WHERE id = %s", (prompt_id,))
        prompt = cur.fetchone()

        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404

        if prompt[2] != current_user_id:
            return jsonify({'error': 'You are not authorized to modify this prompt'}), 403

        if prompt[3] != 'À revoir':
            return jsonify({'error': 'Prompt cannot be modified at this time'}), 400

        if new_content:
            cur.execute("UPDATE prompts SET content = %s, last_updated = CURRENT_TIMESTAMP WHERE id = %s", (new_content, prompt_id))
        if new_price is not None:
            cur.execute("UPDATE prompts SET price = %s, last_updated = CURRENT_TIMESTAMP WHERE id = %s", (new_price, prompt_id))

        conn.commit()

        return jsonify({"message": "Prompt updated successfully"}), 200
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": f"Failed to update prompt: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()
