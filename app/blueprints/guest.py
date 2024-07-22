from flask import Blueprint, request, jsonify
from app.db import get_db_connection

# Création du blueprint pour les routes accessibles aux invités
guest_bp = Blueprint('guest', __name__)

# Route pour rechercher des prompts par contenu ou mots clés (accessible à tous)
@guest_bp.route('/search_prompts', methods=['GET'])
def search_prompts():
    """
    Route pour rechercher des prompts par contenu ou mots clés.
    Accessible à tous, sans authentification requise.
    """
    query = request.args.get('query', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, price FROM prompts WHERE content ILIKE %s", (f'%{query}%',))
    prompts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(prompts), 200



@guest_bp.route('/purchase_prompt', methods=['POST'])
def purchase_prompt():
    data = request.get_json()
    prompt_id = data.get('prompt_id')
    purchaser_email = data.get('purchaser_email')
    if not prompt_id or not purchaser_email:
        return jsonify({'error': 'Prompt ID and purchaser email are required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, price FROM prompts WHERE id = %s", (prompt_id,))
    prompt = cur.fetchone()
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404

    cur.execute("INSERT INTO purchases (prompt_id, purchaser_email) VALUES (%s, %s)", (prompt_id, purchaser_email))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Prompt purchased successfully'}), 201
