from src.models.user import db
from datetime import datetime

class Gare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commune = db.Column(db.String(100), nullable=False)
    quartier = db.Column(db.String(100), nullable=False)
    localisation_geo = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    nom_responsable = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    lignes_depart = db.relationship('Ligne', backref='gare_depart', lazy=True, foreign_keys='Ligne.gare_depart_id')
    lignes_arrivee = db.relationship('Ligne', backref='gare_arrivee', lazy=True, foreign_keys='Ligne.gare_arrivee_id')
    planning_departs = db.relationship('PlanningDepart', backref='gare', lazy=True)

    def __repr__(self):
        return f'<Gare {self.commune} - {self.quartier}>'

    def to_dict(self):
        return {
            'id': self.id,
            'commune': self.commune,
            'quartier': self.quartier,
            'localisation_geo': self.localisation_geo,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'nom_responsable': self.nom_responsable,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

