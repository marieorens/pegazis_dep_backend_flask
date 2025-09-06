from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.gare import Gare

gare_bp = Blueprint('gare', __name__)

@gare_bp.route('', methods=['POST'])
@jwt_required()
def create_gare():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chef_gare':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Vérification des champs requis
        required_fields = ['commune', 'quartier', 'nom_responsable']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Création de la nouvelle gare
        gare = Gare(
            commune=data['commune'],
            quartier=data['quartier'],
            localisation_geo=data.get('localisation_geo'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            nom_responsable=data['nom_responsable']
        )
        
        db.session.add(gare)
        db.session.commit()
        
        return jsonify({
            'message': 'Gare créée avec succès',
            'gare': gare.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@gare_bp.route('', methods=['GET'])
@jwt_required()
def get_gares():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        gares = Gare.query.all()
        return jsonify({
            'gares': [gare.to_dict() for gare in gares]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gare_bp.route('/<int:gare_id>', methods=['GET'])
@jwt_required()
def get_gare(gare_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        gare = Gare.query.get(gare_id)
        if not gare:
            return jsonify({'error': 'Gare non trouvée'}), 404
        
        return jsonify({'gare': gare.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gare_bp.route('/<int:gare_id>', methods=['PUT'])
@jwt_required()
def update_gare(gare_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chef_gare':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        gare = Gare.query.get(gare_id)
        if not gare:
            return jsonify({'error': 'Gare non trouvée'}), 404
        
        data = request.get_json()
        
        # Mise à jour des champs
        if 'commune' in data:
            gare.commune = data['commune']
        if 'quartier' in data:
            gare.quartier = data['quartier']
        if 'localisation_geo' in data:
            gare.localisation_geo = data['localisation_geo']
        if 'latitude' in data:
            gare.latitude = data['latitude']
        if 'longitude' in data:
            gare.longitude = data['longitude']
        if 'nom_responsable' in data:
            gare.nom_responsable = data['nom_responsable']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Gare mise à jour avec succès',
            'gare': gare.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

