import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.gare import gare_bp
from src.routes.ligne import ligne_bp
from src.routes.vehicule import vehicule_bp
from src.routes.planning import planning_bp
from src.routes.chauffeur import chauffeur_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'pegazis_dep_secret_key_2025'
app.config['JWT_SECRET_KEY'] = 'pegazis_dep_jwt_secret_key_2025'

# Configuration CORS pour permettre les requêtes cross-origin
CORS(app)

# Configuration JWT
jwt = JWTManager(app)

# Enregistrement des blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(gare_bp, url_prefix='/api/gares')
app.register_blueprint(ligne_bp, url_prefix='/api/lignes')
app.register_blueprint(vehicule_bp, url_prefix='/api/vehicules')
app.register_blueprint(planning_bp, url_prefix='/api/planning')
app.register_blueprint(chauffeur_bp, url_prefix='/api/chauffeur')

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
