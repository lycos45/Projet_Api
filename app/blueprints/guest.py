from flask import Blueprint, request, jsonify
from app.db import get_db_connection

# Création du blueprint pour les routes accessibles aux invités
guest_bp = Blueprint('guest', __name__)

# Route pour consulter les prompts (accessible à tous)
@guest_bp.route('/view_prompts', methods=['GET'])
def view_prompts():
    """
    Route pour consulter les prompts.
    Accessible à tous, sans authentification requise.
    """
    # Obtenir une connexion à la base de données
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Exécuter la requête pour récupérer les prompts
    cur.execute("SELECT id, content, price FROM prompts")
    prompts = cur.fetchall()
    
    # Fermer le curseur et la connexion à la base de données
    cur.close()
    conn.close()
    
    # Retourner les prompts en format JSON
    return jsonify(prompts), 200

# Route pour rechercher des prompts par contenu ou mots clés (accessible à tous)
@guest_bp.route('/search_prompts', methods=['GET'])
def search_prompts():
    """
    Route pour rechercher des prompts par contenu ou mots clés.
    Accessible à tous, sans authentification requise.
    """
    # Récupérer la requête de recherche depuis les paramètres de la requête
    query = request.args.get('query', '')

    # Obtenir une connexion à la base de données
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Exécuter la requête pour rechercher les prompts correspondant à la requête
    cur.execute(
        "SELECT id, content, price FROM prompts WHERE content ILIKE %s",
        (f'%{query}%',)
    )
    prompts = cur.fetchall()
    
    # Fermer le curseur et la connexion à la base de données
    cur.close()
    conn.close()
    
    # Retourner les résultats de la recherche en format JSON
    return jsonify(prompts), 200

# Route pour acheter un prompt (accessible à tous)
@guest_bp.route('/buy_prompt', methods=['POST'])
def buy_prompt():
    """
    Route pour acheter un prompt.
    Accessible à tous, sans authentification requise.
    """
    # Récupérer les données JSON envoyées dans la requête
    data = request.get_json()
    prompt_id = data.get('prompt_id')
    
    # Processus d'achat à implémenter
    # Remarque: L'implémentation réelle nécessiterait des étapes supplémentaires
    # comme la vérification de l'utilisateur, le traitement du paiement, etc.
    
    return jsonify({'message': 'Purchase successful'}), 200
