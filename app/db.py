import psycopg2
from flask import current_app, g

def get_db_connection():
    """
    Obtient une connexion à la base de données depuis le contexte global.
    Si une connexion n'existe pas encore, elle est créée.
    """
    if 'db' not in g:
        g.db = psycopg2.connect(current_app.config['DATABASE_URL'])
    return g.db

def close_db_connection(e=None):
    """
    Ferme la connexion à la base de données si elle existe.
    Cette fonction est appelée automatiquement à la fin de chaque requête.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()
