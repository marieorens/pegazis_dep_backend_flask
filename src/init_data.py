#!/usr/bin/env python3
"""
Script d'initialisation des données de test pour PEGAZIS DEP
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import User, db
from src.models.gare import Gare
from src.models.ligne import Ligne
from src.models.vehicule import Vehicule
from src.models.planning import PlanningDepart
from src.models.encaissement import Encaissement
from src.models.versement import Versement
from datetime import datetime, timedelta

def init_test_data():
    """Initialise les données de test"""
    
    print("Initialisation des données de test...")
    
    # Création des utilisateurs de test
    
    # Chef de gare
    chef_gare = User(
        username='chef_gare_test',
        email='chef@pegazis.com',
        role='chef_gare',
        nom='KOUAME',
        prenom='Jean',
        telephone='+225 07 12 34 56 78'
    )
    chef_gare.set_password('password123')
    
    # Chauffeurs
    chauffeur1 = User(
        username='chauffeur1_test',
        email='chauffeur1@pegazis.com',
        role='chauffeur',
        nom='TRAORE',
        prenom='Mamadou',
        telephone='+225 05 98 76 54 32'
    )
    chauffeur1.set_password('password123')
    
    chauffeur2 = User(
        username='chauffeur2_test',
        email='chauffeur2@pegazis.com',
        role='chauffeur',
        nom='KONE',
        prenom='Fatou',
        telephone='+225 01 23 45 67 89'
    )
    chauffeur2.set_password('password123')
    
    db.session.add_all([chef_gare, chauffeur1, chauffeur2])
    db.session.commit()
    
    # Création des gares
    gare_adjame = Gare(
        commune='Adjamé',
        quartier='Gare Nord',
        localisation_geo='Près du marché d\'Adjamé',
        latitude=5.3599,
        longitude=-4.0077,
        nom_responsable='DIABATE Moussa'
    )
    
    gare_yopougon = Gare(
        commune='Yopougon',
        quartier='Gesco',
        localisation_geo='Carrefour Gesco',
        latitude=5.3364,
        longitude=-4.0677,
        nom_responsable='OUATTARA Aminata'
    )
    
    gare_cocody = Gare(
        commune='Cocody',
        quartier='Riviera',
        localisation_geo='Carrefour Riviera',
        latitude=5.3717,
        longitude=-3.9926,
        nom_responsable='N\'GUESSAN Paul'
    )
    
    db.session.add_all([gare_adjame, gare_yopougon, gare_cocody])
    db.session.commit()
    
    # Création des lignes
    ligne1 = Ligne(
        nom='Adjamé - Yopougon',
        gare_depart_id=gare_adjame.id,
        gare_arrivee_id=gare_yopougon.id,
        nom_responsable='KOFFI Bernard'
    )
    
    ligne2 = Ligne(
        nom='Adjamé - Cocody',
        gare_depart_id=gare_adjame.id,
        gare_arrivee_id=gare_cocody.id,
        nom_responsable='BAMBA Marie'
    )
    
    db.session.add_all([ligne1, ligne2])
    db.session.commit()
    
    # Création des véhicules
    vehicule1 = Vehicule(
        marque='Toyota',
        modele='Hiace',
        immatriculation='CI-1234-AB',
        chauffeur_id=chauffeur1.id,
        nom_chauffeur='TRAORE Mamadou',
        contact_chauffeur='+225 05 98 76 54 32',
        nom_proprietaire='SANGARE Ibrahim',
        contact_proprietaire='+225 07 11 22 33 44'
    )
    
    vehicule2 = Vehicule(
        marque='Nissan',
        modele='Urvan',
        immatriculation='CI-5678-CD',
        chauffeur_id=chauffeur2.id,
        nom_chauffeur='KONE Fatou',
        contact_chauffeur='+225 01 23 45 67 89',
        nom_proprietaire='DOUMBIA Sekou',
        contact_proprietaire='+225 05 55 66 77 88'
    )
    
    db.session.add_all([vehicule1, vehicule2])
    db.session.commit()
    
    # Création du planning de départ
    planning1 = PlanningDepart(
        vehicule_id=vehicule1.id,
        gare_id=gare_adjame.id,
        rang=1,
        heure_arrivee=datetime.now() - timedelta(minutes=30)
    )
    
    planning2 = PlanningDepart(
        vehicule_id=vehicule2.id,
        gare_id=gare_adjame.id,
        rang=2,
        heure_arrivee=datetime.now() - timedelta(minutes=15)
    )
    
    db.session.add_all([planning1, planning2])
    db.session.commit()
    
    # Création des encaissements de test
    encaissements = [
        Encaissement(
            vehicule_id=vehicule1.id,
            chauffeur_id=chauffeur1.id,
            montant=500,
            type_paiement='mobile_money',
            description='Course Adjamé-Yopougon',
            date_encaissement=datetime.now() - timedelta(hours=2)
        ),
        Encaissement(
            vehicule_id=vehicule1.id,
            chauffeur_id=chauffeur1.id,
            montant=300,
            type_paiement='especes',
            description='Course courte',
            date_encaissement=datetime.now() - timedelta(hours=1)
        ),
        Encaissement(
            vehicule_id=vehicule2.id,
            chauffeur_id=chauffeur2.id,
            montant=750,
            type_paiement='mobile_money',
            description='Course Adjamé-Cocody',
            date_encaissement=datetime.now() - timedelta(minutes=30)
        )
    ]
    
    db.session.add_all(encaissements)
    db.session.commit()
    
    # Création des versements de test
    versements = [
        Versement(
            vehicule_id=vehicule1.id,
            chauffeur_id=chauffeur1.id,
            montant=200,
            destinataire='SANGARE Ibrahim',
            description='Versement propriétaire',
            date_versement=datetime.now() - timedelta(hours=3)
        ),
        Versement(
            vehicule_id=vehicule2.id,
            chauffeur_id=chauffeur2.id,
            montant=300,
            destinataire='DOUMBIA Sekou',
            description='Versement propriétaire',
            date_versement=datetime.now() - timedelta(hours=2)
        )
    ]
    
    db.session.add_all(versements)
    db.session.commit()
    
    print("✅ Données de test initialisées avec succès!")
    print("\n=== COMPTES DE TEST ===")
    print("Chef de gare:")
    print("  Username: chef_gare_test")
    print("  Password: password123")
    print("\nChauffeur 1:")
    print("  Username: chauffeur1_test")
    print("  Password: password123")
    print("  Véhicule: CI-1234-AB")
    print("\nChauffeur 2:")
    print("  Username: chauffeur2_test")
    print("  Password: password123")
    print("  Véhicule: CI-5678-CD")

if __name__ == '__main__':
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        init_test_data()

