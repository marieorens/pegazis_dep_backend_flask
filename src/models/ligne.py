from src.models.user import db
from datetime import datetime

class Ligne(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    gare_depart_id = db.Column(db.Integer, db.ForeignKey('gare.id'), nullable=False)
    gare_arrivee_id = db.Column(db.Integer, db.ForeignKey('gare.id'), nullable=False)
    nom_responsable = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Ligne {self.nom}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'gare_depart_id': self.gare_depart_id,
            'gare_arrivee_id': self.gare_arrivee_id,
            'nom_responsable': self.nom_responsable,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

