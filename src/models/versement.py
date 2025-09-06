from src.models.user import db
from datetime import datetime

class Versement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicule_id = db.Column(db.Integer, db.ForeignKey('vehicule.id'), nullable=False)
    chauffeur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    destinataire = db.Column(db.String(100), nullable=False)  # nom du gérant/propriétaire
    description = db.Column(db.String(255), nullable=True)
    date_versement = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Versement {self.montant} FCFA à {self.destinataire}>'

    def to_dict(self):
        return {
            'id': self.id,
            'vehicule_id': self.vehicule_id,
            'chauffeur_id': self.chauffeur_id,
            'montant': self.montant,
            'destinataire': self.destinataire,
            'description': self.description,
            'date_versement': self.date_versement.isoformat() if self.date_versement else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

