from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.vehicule import Vehicule

vehicule_bp = Blueprint('vehicule', __name__)

@vehicule_bp.route('', methods=['POST'])
@jwt_required()
def create_vehicule():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chef_gare':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Vérification des champs requis
        required_fields = ['marque', 'modele', 'immatriculation', 'chauffeur_id', 
                          'nom_chauffeur', 'contact_chauffeur', 'nom_proprietaire', 'contact_proprietaire']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Vérification que l'immatriculation n'existe pas déjà
        if Vehicule.query.filter_by(immatriculation=data['immatriculation']).first():
            return jsonify({'error': 'Cette immatriculation existe déjà'}), 400
        
        # Vérification que le chauffeur existe
        chauffeur = User.query.get(data['chauffeur_id'])
        if not chauffeur or chauffeur.role != 'chauffeur':
            return jsonify({'error': 'Chauffeur non trouvé ou invalide'}), 404
        
        # Création du nouveau véhicule
        vehicule = Vehicule(
            marque=data['marque'],
            modele=data['modele'],
            immatriculation=data['immatriculation'],
            chauffeur_id=data['chauffeur_id'],
            nom_chauffeur=data['nom_chauffeur'],
            contact_chauffeur=data['contact_chauffeur'],
            nom_proprietaire=data['nom_proprietaire'],
            contact_proprietaire=data['contact_proprietaire']
        )
        
        db.session.add(vehicule)
        db.session.commit()
        
        return jsonify({
            'message': 'Véhicule créé avec succès',
            'vehicule': vehicule.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vehicule_bp.route('', methods=['GET'])
@jwt_required()
def get_vehicules():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if user.role == 'chef_gare':
            # Chef de gare peut voir tous les véhicules
            vehicules = Vehicule.query.all()
        else:
            # Chauffeur ne peut voir que ses véhicules
            vehicules = Vehicule.query.filter_by(chauffeur_id=current_user_id).all()
        
        vehicules_data = []
        for vehicule in vehicules:
            vehicule_dict = vehicule.to_dict()
            # Ajouter les informations du chauffeur
            chauffeur = User.query.get(vehicule.chauffeur_id)
            vehicule_dict['chauffeur'] = chauffeur.to_dict() if chauffeur else None
            vehicules_data.append(vehicule_dict)
        
        return jsonify({'vehicules': vehicules_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehicule_bp.route('/search/<immatriculation>', methods=['GET'])
@jwt_required()
def search_vehicule_by_immatriculation(immatriculation):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        vehicule = Vehicule.query.filter_by(immatriculation=immatriculation).first()
        if not vehicule:
            return jsonify({'error': 'Véhicule non trouvé'}), 404
        
        vehicule_dict = vehicule.to_dict()
        # Ajouter les informations du chauffeur
        chauffeur = User.query.get(vehicule.chauffeur_id)
        vehicule_dict['chauffeur'] = chauffeur.to_dict() if chauffeur else None
        
        return jsonify({'vehicule': vehicule_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehicule_bp.route('/<int:vehicule_id>', methods=['GET'])
@jwt_required()
def get_vehicule(vehicule_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        vehicule = Vehicule.query.get(vehicule_id)
        if not vehicule:
            return jsonify({'error': 'Véhicule non trouvé'}), 404
        
        # Vérification des permissions
        if user.role == 'chauffeur' and vehicule.chauffeur_id != current_user_id:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        vehicule_dict = vehicule.to_dict()
        # Ajouter les informations du chauffeur
        chauffeur = User.query.get(vehicule.chauffeur_id)
        vehicule_dict['chauffeur'] = chauffeur.to_dict() if chauffeur else None
        
        return jsonify({'vehicule': vehicule_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

