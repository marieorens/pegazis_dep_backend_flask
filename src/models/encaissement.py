from src.models.user import db
from datetime import datetime

class Encaissement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicule_id = db.Column(db.Integer, db.ForeignKey('vehicule.id'), nullable=False)
    chauffeur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    type_paiement = db.Column(db.String(20), nullable=False)  # 'mobile_money', 'especes'
    description = db.Column(db.String(255), nullable=True)
    date_encaissement = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Encaissement {self.montant} FCFA>'

    def to_dict(self):
        return {
            'id': self.id,
            'vehicule_id': self.vehicule_id,
            'chauffeur_id': self.chauffeur_id,
            'montant': self.montant,
            'type_paiement': self.type_paiement,
            'description': self.description,
            'date_encaissement': self.date_encaissement.isoformat() if self.date_encaissement else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

