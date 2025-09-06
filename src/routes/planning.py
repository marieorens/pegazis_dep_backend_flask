from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.planning import PlanningDepart
from src.models.vehicule import Vehicule
from src.models.gare import Gare
from datetime import datetime

planning_bp = Blueprint('planning', __name__)

@planning_bp.route('/arrivee', methods=['POST'])
@jwt_required()
def enregistrer_arrivee():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chef_gare':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Vérification des champs requis
        required_fields = ['immatriculation', 'gare_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Recherche du véhicule par immatriculation
        vehicule = Vehicule.query.filter_by(immatriculation=data['immatriculation']).first()
        if not vehicule:
            return jsonify({'error': 'Véhicule non trouvé'}), 404
        
        # Vérification que la gare existe
        gare = Gare.query.get(data['gare_id'])
        if not gare:
            return jsonify({'error': 'Gare non trouvée'}), 404
        
        # Vérifier si le véhicule n'est pas déjà en attente dans cette gare
        planning_existant = PlanningDepart.query.filter_by(
            vehicule_id=vehicule.id,
            gare_id=data['gare_id'],
            statut='en_attente'
        ).first()
        
        if planning_existant:
            return jsonify({'error': 'Ce véhicule est déjà en attente dans cette gare'}), 400
        
        # Calculer le rang (nombre de véhicules en attente + 1)
        rang = PlanningDepart.query.filter_by(
            gare_id=data['gare_id'],
            statut='en_attente'
        ).count() + 1
        
        # Création de l'enregistrement de planning
        planning = PlanningDepart(
            vehicule_id=vehicule.id,
            gare_id=data['gare_id'],
            rang=rang,
            heure_arrivee=datetime.utcnow()
        )
        
        db.session.add(planning)
        db.session.commit()
        
        planning_dict = planning.to_dict()
        planning_dict['vehicule'] = vehicule.to_dict()
        planning_dict['gare'] = gare.to_dict()
        
        return jsonify({
            'message': 'Arrivée enregistrée avec succès',
            'planning': planning_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@planning_bp.route('/current/<int:gare_id>', methods=['GET'])
@jwt_required()
def get_planning_current(gare_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Vérification que la gare existe
        gare = Gare.query.get(gare_id)
        if not gare:
            return jsonify({'error': 'Gare non trouvée'}), 404
        
        # Récupération du planning actuel (véhicules en attente)
        plannings = PlanningDepart.query.filter_by(
            gare_id=gare_id,
            statut='en_attente'
        ).order_by(PlanningDepart.rang).all()
        
        plannings_data = []
        for planning in plannings:
            planning_dict = planning.to_dict()
            vehicule = Vehicule.query.get(planning.vehicule_id)
            planning_dict['vehicule'] = vehicule.to_dict() if vehicule else None
            plannings_data.append(planning_dict)
        
        return jsonify({
            'gare': gare.to_dict(),
            'planning': plannings_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@planning_bp.route('/depart/<int:planning_id>', methods=['PUT'])
@jwt_required()
def marquer_depart(planning_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chef_gare':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        planning = PlanningDepart.query.get(planning_id)
        if not planning:
            return jsonify({'error': 'Planning non trouvé'}), 404
        
        # Marquer le véhicule comme parti
        planning.statut = 'parti'
        
        # Réorganiser les rangs des véhicules restants
        plannings_restants = PlanningDepart.query.filter_by(
            gare_id=planning.gare_id,
            statut='en_attente'
        ).filter(PlanningDepart.rang > planning.rang).all()
        
        for p in plannings_restants:
            p.rang -= 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Départ enregistré avec succès',
            'planning': planning.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

