from src.models.user import db
from datetime import datetime

class Vehicule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(50), nullable=False)
    modele = db.Column(db.String(50), nullable=False)
    immatriculation = db.Column(db.String(20), unique=True, nullable=False)
    chauffeur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nom_chauffeur = db.Column(db.String(100), nullable=False)
    contact_chauffeur = db.Column(db.String(20), nullable=False)
    nom_proprietaire = db.Column(db.String(100), nullable=False)
    contact_proprietaire = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    planning_departs = db.relationship('PlanningDepart', backref='vehicule', lazy=True)
    encaissements = db.relationship('Encaissement', backref='vehicule', lazy=True)
    versements = db.relationship('Versement', backref='vehicule', lazy=True)

    def __repr__(self):
        return f'<Vehicule {self.immatriculation}>'

    def to_dict(self):
        return {
            'id': self.id,
            'marque': self.marque,
            'modele': self.modele,
            'immatriculation': self.immatriculation,
            'chauffeur_id': self.chauffeur_id,
            'nom_chauffeur': self.nom_chauffeur,
            'contact_chauffeur': self.contact_chauffeur,
            'nom_proprietaire': self.nom_proprietaire,
            'contact_proprietaire': self.contact_proprietaire,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

