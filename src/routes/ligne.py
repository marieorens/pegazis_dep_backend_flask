from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.ligne import Ligne
from src.models.gare import Gare

ligne_bp = Blueprint('ligne', __name__)

@ligne_bp.route('', methods=['POST'])
@jwt_required()
def create_ligne():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chef_gare':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Vérification des champs requis
        required_fields = ['nom', 'gare_depart_id', 'gare_arrivee_id', 'nom_responsable']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Vérification que les gares existent
        gare_depart = Gare.query.get(data['gare_depart_id'])
        gare_arrivee = Gare.query.get(data['gare_arrivee_id'])
        
        if not gare_depart:
            return jsonify({'error': 'Gare de départ non trouvée'}), 404
        if not gare_arrivee:
            return jsonify({'error': 'Gare d\'arrivée non trouvée'}), 404
        
        # Création de la nouvelle ligne
        ligne = Ligne(
            nom=data['nom'],
            gare_depart_id=data['gare_depart_id'],
            gare_arrivee_id=data['gare_arrivee_id'],
            nom_responsable=data['nom_responsable']
        )
        
        db.session.add(ligne)
        db.session.commit()
        
        return jsonify({
            'message': 'Ligne créée avec succès',
            'ligne': ligne.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ligne_bp.route('', methods=['GET'])
@jwt_required()
def get_lignes():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        lignes = Ligne.query.all()
        lignes_data = []
        
        for ligne in lignes:
            ligne_dict = ligne.to_dict()
            # Ajouter les informations des gares
            gare_depart = Gare.query.get(ligne.gare_depart_id)
            gare_arrivee = Gare.query.get(ligne.gare_arrivee_id)
            
            ligne_dict['gare_depart'] = gare_depart.to_dict() if gare_depart else None
            ligne_dict['gare_arrivee'] = gare_arrivee.to_dict() if gare_arrivee else None
            
            lignes_data.append(ligne_dict)
        
        return jsonify({'lignes': lignes_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ligne_bp.route('/<int:ligne_id>', methods=['GET'])
@jwt_required()
def get_ligne(ligne_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        ligne = Ligne.query.get(ligne_id)
        if not ligne:
            return jsonify({'error': 'Ligne non trouvée'}), 404
        
        ligne_dict = ligne.to_dict()
        # Ajouter les informations des gares
        gare_depart = Gare.query.get(ligne.gare_depart_id)
        gare_arrivee = Gare.query.get(ligne.gare_arrivee_id)
        
        ligne_dict['gare_depart'] = gare_depart.to_dict() if gare_depart else None
        ligne_dict['gare_arrivee'] = gare_arrivee.to_dict() if gare_arrivee else None
        
        return jsonify({'ligne': ligne_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

