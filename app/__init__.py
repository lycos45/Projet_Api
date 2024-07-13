from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import Config
from app.blueprints.admin import admin_bp
from app.blueprints.user import user_bp
from app.blueprints.guest import guest_bp
from app.routes import main_bp

from app.db import close_db_connection

def create_app():
    # Crée une instance de l'application Flask
    app = Flask(__name__)

    # Charge la configuration de l'application à partir de l'objet Config
    app.config.from_object(Config)
    
    # Initialise JWT (JSON Web Token) pour la gestion des tokens d'authentification
    jwt = JWTManager(app)

    # Enregistre les blueprints pour structurer les routes de l'application
    # Les blueprints permettent de diviser l'application en plusieurs modules
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(guest_bp, url_prefix='/guest')
    app.register_blueprint(main_bp, url_prefix='/')

    # Enregistre une fonction pour nettoyer les ressources à la fin de chaque requête
    app.teardown_appcontext(close_db_connection)

    return app

# Ce bloc permet de lancer l'application directement via ce fichier
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
