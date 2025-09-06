from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username et password requis'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Identifiants invalides'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Vérification des champs requis
        required_fields = ['username', 'email', 'password', 'role', 'nom', 'prenom']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Vérification si l'utilisateur existe déjà
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Cet email existe déjà'}), 400
        
        # Création du nouvel utilisateur
        user = User(
            username=data['username'],
            email=data['email'],
            role=data['role'],
            nom=data['nom'],
            prenom=data['prenom'],
            telephone=data.get('telephone')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

