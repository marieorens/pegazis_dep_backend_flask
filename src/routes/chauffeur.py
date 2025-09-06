from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.vehicule import Vehicule
from src.models.encaissement import Encaissement
from src.models.versement import Versement
from src.models.planning import PlanningDepart
from datetime import datetime, timedelta
import io

chauffeur_bp = Blueprint('chauffeur', __name__)

@chauffeur_bp.route('/rang', methods=['GET'])
@jwt_required()
def get_rang_vehicule():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chauffeur':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Récupérer le véhicule du chauffeur
        vehicule = Vehicule.query.filter_by(chauffeur_id=current_user_id).first()
        if not vehicule:
            return jsonify({'error': 'Aucun véhicule assigné'}), 404
        
        # Récupérer le planning actuel du véhicule
        planning = PlanningDepart.query.filter_by(
            vehicule_id=vehicule.id,
            statut='en_attente'
        ).first()
        
        if not planning:
            return jsonify({
                'vehicule': vehicule.to_dict(),
                'rang': None,
                'message': 'Véhicule non enregistré dans une gare'
            }), 200
        
        return jsonify({
            'vehicule': vehicule.to_dict(),
            'rang': planning.rang,
            'gare_id': planning.gare_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chauffeur_bp.route('/encaisser', methods=['POST'])
@jwt_required()
def encaisser_client():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chauffeur':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Vérification des champs requis
        required_fields = ['montant', 'type_paiement']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Récupérer le véhicule du chauffeur
        vehicule = Vehicule.query.filter_by(chauffeur_id=current_user_id).first()
        if not vehicule:
            return jsonify({'error': 'Aucun véhicule assigné'}), 404
        
        # Création de l'encaissement
        encaissement = Encaissement(
            vehicule_id=vehicule.id,
            chauffeur_id=current_user_id,
            montant=float(data['montant']),
            type_paiement=data['type_paiement'],
            description=data.get('description', '')
        )
        
        db.session.add(encaissement)
        db.session.commit()
        
        return jsonify({
            'message': 'Encaissement enregistré avec succès',
            'encaissement': encaissement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@chauffeur_bp.route('/recettes/jour', methods=['GET'])
@jwt_required()
def get_recettes_jour():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chauffeur':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Récupérer le véhicule du chauffeur
        vehicule = Vehicule.query.filter_by(chauffeur_id=current_user_id).first()
        if not vehicule:
            return jsonify({'error': 'Aucun véhicule assigné'}), 404
        
        # Date du jour
        aujourd_hui = datetime.now().date()
        
        # Récupérer les encaissements du jour
        encaissements = Encaissement.query.filter(
            Encaissement.vehicule_id == vehicule.id,
            Encaissement.date_encaissement >= aujourd_hui,
            Encaissement.date_encaissement < aujourd_hui + timedelta(days=1)
        ).all()
        
        total_jour = sum(enc.montant for enc in encaissements)
        
        return jsonify({
            'date': aujourd_hui.isoformat(),
            'total_recettes': total_jour,
            'nombre_encaissements': len(encaissements),
            'encaissements': [enc.to_dict() for enc in encaissements]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chauffeur_bp.route('/verser', methods=['POST'])
@jwt_required()
def effectuer_versement():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chauffeur':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Vérification des champs requis
        required_fields = ['montant', 'destinataire']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Récupérer le véhicule du chauffeur
        vehicule = Vehicule.query.filter_by(chauffeur_id=current_user_id).first()
        if not vehicule:
            return jsonify({'error': 'Aucun véhicule assigné'}), 404
        
        # Création du versement
        versement = Versement(
            vehicule_id=vehicule.id,
            chauffeur_id=current_user_id,
            montant=float(data['montant']),
            destinataire=data['destinataire'],
            description=data.get('description', '')
        )
        
        db.session.add(versement)
        db.session.commit()
        
        return jsonify({
            'message': 'Versement enregistré avec succès',
            'versement': versement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@chauffeur_bp.route('/historique/encaissements', methods=['GET'])
@jwt_required()
def get_historique_encaissements():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chauffeur':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Récupérer le véhicule du chauffeur
        vehicule = Vehicule.query.filter_by(chauffeur_id=current_user_id).first()
        if not vehicule:
            return jsonify({'error': 'Aucun véhicule assigné'}), 404
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Récupérer les encaissements avec pagination
        encaissements = Encaissement.query.filter_by(vehicule_id=vehicule.id)\
            .order_by(Encaissement.date_encaissement.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'encaissements': [enc.to_dict() for enc in encaissements.items],
            'total': encaissements.total,
            'pages': encaissements.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chauffeur_bp.route('/historique/versements', methods=['GET'])
@jwt_required()
def get_historique_versements():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chauffeur':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Récupérer le véhicule du chauffeur
        vehicule = Vehicule.query.filter_by(chauffeur_id=current_user_id).first()
        if not vehicule:
            return jsonify({'error': 'Aucun véhicule assigné'}), 404
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Récupérer les versements avec pagination
        versements = Versement.query.filter_by(vehicule_id=vehicule.id)\
            .order_by(Versement.date_versement.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'versements': [vers.to_dict() for vers in versements.items],
            'total': versements.total,
            'pages': versements.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chauffeur_bp.route('/recettes/solde', methods=['GET'])
@jwt_required()
def get_solde_recettes():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chauffeur':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Récupérer le véhicule du chauffeur
        vehicule = Vehicule.query.filter_by(chauffeur_id=current_user_id).first()
        if not vehicule:
            return jsonify({'error': 'Aucun véhicule assigné'}), 404
        
        # Paramètres de date
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        # Requête de base
        query_encaissements = Encaissement.query.filter_by(vehicule_id=vehicule.id)
        query_versements = Versement.query.filter_by(vehicule_id=vehicule.id)
        
        # Filtrage par date si spécifié
        if date_debut:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            query_encaissements = query_encaissements.filter(Encaissement.date_encaissement >= date_debut_obj)
            query_versements = query_versements.filter(Versement.date_versement >= date_debut_obj)
        
        if date_fin:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date() + timedelta(days=1)
            query_encaissements = query_encaissements.filter(Encaissement.date_encaissement < date_fin_obj)
            query_versements = query_versements.filter(Versement.date_versement < date_fin_obj)
        
        # Calcul des totaux
        total_encaissements = sum(enc.montant for enc in query_encaissements.all())
        total_versements = sum(vers.montant for vers in query_versements.all())
        solde = total_encaissements - total_versements
        
        return jsonify({
            'periode': {
                'date_debut': date_debut,
                'date_fin': date_fin
            },
            'total_encaissements': total_encaissements,
            'total_versements': total_versements,
            'solde': solde
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chauffeur_bp.route('/recettes/pdf', methods=['GET'])
@jwt_required()
def generer_etat_recettes_pdf():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'chauffeur':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Récupérer le véhicule du chauffeur
        vehicule = Vehicule.query.filter_by(chauffeur_id=current_user_id).first()
        if not vehicule:
            return jsonify({'error': 'Aucun véhicule assigné'}), 404
        
        # Paramètres de date
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        # Requête des encaissements
        query_encaissements = Encaissement.query.filter_by(vehicule_id=vehicule.id)
        
        if date_debut:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            query_encaissements = query_encaissements.filter(Encaissement.date_encaissement >= date_debut_obj)
        
        if date_fin:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date() + timedelta(days=1)
            query_encaissements = query_encaissements.filter(Encaissement.date_encaissement < date_fin_obj)
        
        encaissements = query_encaissements.order_by(Encaissement.date_encaissement.desc()).all()
        
        # Génération d'un rapport simple en texte
        rapport_text = f"PEGAZIS DEP - État des Recettes\n"
        rapport_text += f"Chauffeur: {user.nom} {user.prenom}\n"
        rapport_text += f"Véhicule: {vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})\n\n"
        
        if date_debut and date_fin:
            rapport_text += f"Période: du {date_debut} au {date_fin}\n\n"
        
        rapport_text += "Date\t\tMontant\t\tType\t\tDescription\n"
        rapport_text += "-" * 60 + "\n"
        
        total = 0
        for enc in encaissements:
            rapport_text += f"{enc.date_encaissement.strftime('%d/%m/%Y')}\t{enc.montant} FCFA\t{enc.type_paiement}\t{enc.description or ''}\n"
            total += enc.montant
        
        rapport_text += "-" * 60 + "\n"
        rapport_text += f"Total: {total} FCFA\n"
        
        response = make_response(rapport_text)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=recettes_{vehicule.immatriculation}_{datetime.now().strftime("%Y%m%d")}.txt'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

