from src.models.user import db
from datetime import datetime

class PlanningDepart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicule_id = db.Column(db.Integer, db.ForeignKey('vehicule.id'), nullable=False)
    gare_id = db.Column(db.Integer, db.ForeignKey('gare.id'), nullable=False)
    heure_arrivee = db.Column(db.DateTime, default=datetime.utcnow)
    rang = db.Column(db.Integer, nullable=False)
    statut = db.Column(db.String(20), default='en_attente')  # 'en_attente', 'parti', 'annule'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PlanningDepart Vehicule:{self.vehicule_id} Rang:{self.rang}>'

    def to_dict(self):
        return {
            'id': self.id,
            'vehicule_id': self.vehicule_id,
            'gare_id': self.gare_id,
            'heure_arrivee': self.heure_arrivee.isoformat() if self.heure_arrivee else None,
            'rang': self.rang,
            'statut': self.statut,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

