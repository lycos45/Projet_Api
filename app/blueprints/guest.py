from flask import Blueprint, request, jsonify
from app.db import get_db_connection

guest_bp = Blueprint('guest', __name__)

# Route pour consulter les prompts (accessible à tous)
@guest_bp.route('/view_prompts', methods=['GET'])
def view_prompts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, price FROM prompts ")
    prompts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(prompts), 200


# Route pour rechercher des prompts par contenu ou mots clés (accessible à tous)
@guest_bp.route('/search_prompts', methods=['GET'])
def search_prompts():
    query = request.args.get('query')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, price FROM prompts")
    prompts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(prompts), 200


# Route pour acheter un prompt (accessible à tous)
@guest_bp.route('/buy_prompt', methods=['POST'])
def buy_prompt():
    data = request.get_json()
    prompt_id = data.get('prompt_id')
    
    # Processus d'achat à implémenter
    return jsonify({'message': 'Purchase successful'}), 200
