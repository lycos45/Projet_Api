from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import Config
from app.blueprints.admin import admin_bp
from app.blueprints.user import user_bp
from app.blueprints.guest import guest_bp
from app.routes import main_bp

from app.db import close_db_connection

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    

    # Initialiser JWT
    jwt = JWTManager(app)

    # Enregistrer les blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(guest_bp, url_prefix='/guest')
    app.register_blueprint(main_bp, url_prefix='/')
    

    # Enregistrer les fonctions de nettoyage des ressources
    app.teardown_appcontext(close_db_connection)

    return app

# Pour lancer l'application via le fichier __init__.py
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
