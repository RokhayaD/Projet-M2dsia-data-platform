"""
SOURCE 3 : API REST simulée
Endpoints disponibles :
  GET /health              - Health check
  GET /emplois-du-temps    - Emplois du temps par département/semaine
  GET /absences            - Données d'absences des étudiants
  GET /bourses             - Données sur les bourses attribuées
  GET /statistiques        - Statistiques globales université
"""

from fastapi import FastAPI, Query
from datetime import datetime, date
import random

app = FastAPI(
    title="API Université",
    description="Source de données REST pour la data-plateforme universitaire",
    version="1.0.0"
)

# ── Données statiques simulées ────────────────────────────────

EMPLOIS_DU_TEMPS = [
    {"id": 1, "cours_code": "INFO302", "intitule": "Data Engineering",
     "enseignant": "Dr. Kane Aminata", "salle": "Labo Info 1",
     "jour": "Lundi", "heure_debut": "08:00", "heure_fin": "10:00",
     "type": "TP", "departement": "INFO", "semaine": 1},
    {"id": 2, "cours_code": "INFO301", "intitule": "Bases de Données Avancées",
     "enseignant": "Dr. Diallo Mamadou", "salle": "Amphi A",
     "jour": "Lundi", "heure_debut": "10:00", "heure_fin": "12:00",
     "type": "CM", "departement": "INFO", "semaine": 1},
    {"id": 3, "cours_code": "INFO201", "intitule": "Algorithmes",
     "enseignant": "Dr. Traoré Moussa", "salle": "Salle 101",
     "jour": "Mardi", "heure_debut": "08:00", "heure_fin": "10:00",
     "type": "TD", "departement": "INFO", "semaine": 1},
    {"id": 4, "cours_code": "MATH301", "intitule": "Analyse Avancée",
     "enseignant": "Dr. Sow Aissatou", "salle": "Amphi B",
     "jour": "Mardi", "heure_debut": "14:00", "heure_fin": "16:00",
     "type": "CM", "departement": "MATH", "semaine": 1},
    {"id": 5, "cours_code": "INFO401", "intitule": "Machine Learning",
     "enseignant": "Dr. Diallo Mamadou", "salle": "Labo Info 2",
     "jour": "Mercredi", "heure_debut": "09:00", "heure_fin": "12:00",
     "type": "TP", "departement": "INFO", "semaine": 1},
    {"id": 6, "cours_code": "GEST201", "intitule": "Finance d'Entreprise",
     "enseignant": "Dr. Ndiaye Fatou", "salle": "Salle 201",
     "jour": "Jeudi", "heure_debut": "10:00", "heure_fin": "12:00",
     "type": "CM", "departement": "GEST", "semaine": 1},
    {"id": 7, "cours_code": "INFO302", "intitule": "Data Engineering",
     "enseignant": "Dr. Kane Aminata", "salle": "Salle 102",
     "jour": "Jeudi", "heure_debut": "14:00", "heure_fin": "16:00",
     "type": "TD", "departement": "INFO", "semaine": 1},
    {"id": 8, "cours_code": "PHY301", "intitule": "Physique Quantique",
     "enseignant": "Dr. Ba Ibrahim", "salle": "Labo Physique",
     "jour": "Vendredi", "heure_debut": "08:00", "heure_fin": "11:00",
     "type": "TP", "departement": "PHY", "semaine": 1},
]

ABSENCES = [
    {"id": 1, "etudiant_matricule": "ETU001", "cours_code": "INFO302",
     "date": "2025-02-10", "heure": "08:00", "justifiee": False, "motif": None},
    {"id": 2, "etudiant_matricule": "ETU003", "cours_code": "MATH301",
     "date": "2025-02-11", "heure": "14:00", "justifiee": True, "motif": "Maladie"},
    {"id": 3, "etudiant_matricule": "ETU011", "cours_code": "INFO301",
     "date": "2025-02-10", "heure": "10:00", "justifiee": False, "motif": None},
    {"id": 4, "etudiant_matricule": "ETU011", "cours_code": "INFO201",
     "date": "2025-02-11", "heure": "08:00", "justifiee": False, "motif": None},
    {"id": 5, "etudiant_matricule": "ETU005", "cours_code": "GEST201",
     "date": "2025-02-13", "heure": "10:00", "justifiee": True, "motif": "Raisons familiales"},
    {"id": 6, "etudiant_matricule": "ETU007", "cours_code": "PHY301",
     "date": "2025-02-14", "heure": "08:00", "justifiee": False, "motif": None},
    {"id": 7, "etudiant_matricule": "ETU002", "cours_code": "INFO301",
     "date": "2025-02-17", "heure": "10:00", "justifiee": True, "motif": "Compétition sportive"},
    {"id": 8, "etudiant_matricule": "ETU009", "cours_code": "INFO401",
     "date": "2025-02-12", "heure": "09:00", "justifiee": False, "motif": None},
]

BOURSES = [
    {"id": 1, "etudiant_matricule": "ETU002", "type_bourse": "Excellence",
     "montant_mensuel": 75000, "duree_mois": 10, "annee_academique": "2024-2025",
     "source_financement": "État", "statut": "active"},
    {"id": 2, "etudiant_matricule": "ETU006", "type_bourse": "Excellence",
     "montant_mensuel": 75000, "duree_mois": 10, "annee_academique": "2024-2025",
     "source_financement": "État", "statut": "active"},
    {"id": 3, "etudiant_matricule": "ETU001", "type_bourse": "Sociale",
     "montant_mensuel": 40000, "duree_mois": 10, "annee_academique": "2024-2025",
     "source_financement": "État", "statut": "active"},
    {"id": 4, "etudiant_matricule": "ETU012", "type_bourse": "Excellence",
     "montant_mensuel": 75000, "duree_mois": 10, "annee_academique": "2024-2025",
     "source_financement": "État", "statut": "active"},
    {"id": 5, "etudiant_matricule": "ETU009", "type_bourse": "Mérite",
     "montant_mensuel": 55000, "duree_mois": 10, "annee_academique": "2024-2025",
     "source_financement": "Partenaire Privé", "statut": "active"},
    {"id": 6, "etudiant_matricule": "ETU015", "type_bourse": "Excellence",
     "montant_mensuel": 75000, "duree_mois": 10, "annee_academique": "2023-2024",
     "source_financement": "État", "statut": "terminée"},
]


# ── Endpoints ────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "API Université", "timestamp": datetime.now().isoformat()}


@app.get("/emplois-du-temps")
def get_emplois_du_temps(
    departement: str = Query(None, description="Filtrer par département (ex: INFO)"),
    semaine: int = Query(1, description="Numéro de semaine")
):
    data = [e for e in EMPLOIS_DU_TEMPS if e["semaine"] == semaine]
    if departement:
        data = [e for e in data if e["departement"] == departement.upper()]
    return {
        "total": len(data),
        "semaine": semaine,
        "emplois_du_temps": data,
        "extracted_at": datetime.now().isoformat()
    }


@app.get("/absences")
def get_absences(
    etudiant: str = Query(None, description="Matricule étudiant"),
    justifiee: bool = Query(None, description="Filtrer par justification")
):
    data = ABSENCES.copy()
    if etudiant:
        data = [a for a in data if a["etudiant_matricule"] == etudiant.upper()]
    if justifiee is not None:
        data = [a for a in data if a["justifiee"] == justifiee]
    return {
        "total": len(data),
        "absences": data,
        "extracted_at": datetime.now().isoformat()
    }


@app.get("/bourses")
def get_bourses(
    annee_academique: str = Query(None, description="Filtrer par année (ex: 2024-2025)"),
    statut: str = Query(None, description="active | terminée")
):
    data = BOURSES.copy()
    if annee_academique:
        data = [b for b in data if b["annee_academique"] == annee_academique]
    if statut:
        data = [b for b in data if b["statut"] == statut]
    return {
        "total": len(data),
        "bourses": data,
        "extracted_at": datetime.now().isoformat()
    }


@app.get("/statistiques")
def get_statistiques():
    return {
        "annee_academique": "2024-2025",
        "etudiants": {
            "total": 1250,
            "actifs": 1180,
            "suspendus": 45,
            "diplomes": 25,
            "par_departement": {
                "INFO": 380, "MATH": 210, "PHY": 195, "GEST": 290, "LANG": 175
            }
        },
        "enseignants": {
            "total": 87,
            "permanents": 62,
            "vacataires": 25
        },
        "cours": {
            "total": 145,
            "par_semestre": {"S1": 28, "S2": 27, "S3": 26, "S4": 26, "S5": 24, "S6": 14}
        },
        "taux_reussite_global": 78.5,
        "taux_abandon": 3.2,
        "extracted_at": datetime.now().isoformat()
    }
