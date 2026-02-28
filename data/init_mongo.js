// ============================================================
// INITIALISATION BASE UNIVERSITÉ (MongoDB)
// Source 2 : Données non-relationnelles
// Collections : evenements, candidatures, feedbacks_cours
// ============================================================

db = db.getSiblingDB('universite_nosql');

// ── Collection 1 : Événements du campus ──────────────────────
db.evenements.drop();
db.evenements.insertMany([
  {
    titre: "Journée Portes Ouvertes 2025",
    type: "institutionnel",
    date_debut: new Date("2025-03-15T08:00:00"),
    date_fin: new Date("2025-03-15T17:00:00"),
    lieu: "Campus Principal",
    description: "Découvrez nos formations et rencontrez nos enseignants.",
    organisateur: { nom: "Service Communication", email: "comm@univ.sn" },
    participants_attendus: 500,
    tags: ["orientation", "recrutement", "campus"],
    statut: "terminé",
    created_at: new Date()
  },
  {
    titre: "Hackathon IA & Data 2025",
    type: "academique",
    date_debut: new Date("2025-04-10T09:00:00"),
    date_fin: new Date("2025-04-12T18:00:00"),
    lieu: "Bâtiment Informatique",
    description: "48h pour innover autour de l'intelligence artificielle et la data.",
    organisateur: { nom: "Dept. Informatique", email: "info@univ.sn" },
    participants_attendus: 120,
    participants_inscrits: 98,
    tags: ["hackathon", "IA", "data", "competition"],
    prix: ["MacBook Pro", "Stage en entreprise", "Bourse"],
    statut: "terminé",
    created_at: new Date()
  },
  {
    titre: "Conférence Big Data & Cloud",
    type: "conference",
    date_debut: new Date("2025-05-20T10:00:00"),
    date_fin: new Date("2025-05-20T16:00:00"),
    lieu: "Amphi A",
    description: "Conférence sur les tendances Big Data et architectures Cloud.",
    organisateur: { nom: "Dr. Kane Aminata", email: "akane@univ.sn" },
    intervenants: ["Expert AWS", "Data Engineer Orange SN", "CTO Wave"],
    participants_attendus: 250,
    statut: "planifié",
    created_at: new Date()
  },
  {
    titre: "Cérémonie de Remise des Diplômes 2025",
    type: "ceremonie",
    date_debut: new Date("2025-07-05T10:00:00"),
    date_fin: new Date("2025-07-05T14:00:00"),
    lieu: "Grande Salle des Fêtes",
    description: "Remise officielle des diplômes aux étudiants de la promotion 2025.",
    organisateur: { nom: "Présidence", email: "presidence@univ.sn" },
    diplomes_prevus: 180,
    statut: "planifié",
    created_at: new Date()
  },
  {
    titre: "Séminaire Entrepreneuriat",
    type: "formation",
    date_debut: new Date("2025-06-03T09:00:00"),
    date_fin: new Date("2025-06-04T17:00:00"),
    lieu: "Salle de Conférence B",
    description: "2 jours pour développer votre esprit entrepreneurial.",
    organisateur: { nom: "Club Entrepreneur", email: "entrepreneur@univ.sn" },
    tags: ["startup", "business", "innovation"],
    statut: "planifié",
    created_at: new Date()
  }
]);

// ── Collection 2 : Candidatures (admissions) ─────────────────
db.candidatures.drop();
db.candidatures.insertMany([
  {
    numero: "CAND-2025-001",
    candidat: {
      nom: "Diallo", prenom: "Alpha",
      email: "alpha.diallo@gmail.com",
      telephone: "+221 77 123 4567",
      nationalite: "Sénégalaise",
      date_naissance: new Date("2003-04-12")
    },
    formation_souhaitee: "Licence Informatique",
    departement: "INFO",
    annee_entree: 1,
    documents: {
      bac: { serie: "S", mention: "Bien", annee: 2024, etablissement: "Lycée Lamine Guèye" },
      releve_notes: true,
      lettre_motivation: true,
      piece_identite: true
    },
    scores: { note_dossier: 16.5, test_admission: 14.0, entretien: null },
    statut: "en_attente",
    created_at: new Date()
  },
  {
    numero: "CAND-2025-002",
    candidat: {
      nom: "Sané", prenom: "Binta",
      email: "binta.sane@gmail.com",
      telephone: "+221 76 234 5678",
      nationalite: "Sénégalaise",
      date_naissance: new Date("2003-08-25")
    },
    formation_souhaitee: "Licence Mathématiques",
    departement: "MATH",
    annee_entree: 1,
    documents: {
      bac: { serie: "S2", mention: "Très Bien", annee: 2024, etablissement: "Lycée Blaise Diagne" },
      releve_notes: true,
      lettre_motivation: true,
      piece_identite: true
    },
    scores: { note_dossier: 18.0, test_admission: 17.5, entretien: 17.0 },
    statut: "accepté",
    created_at: new Date()
  },
  {
    numero: "CAND-2025-003",
    candidat: {
      nom: "Badiane", prenom: "Serigne",
      email: "serigne.badiane@gmail.com",
      telephone: "+221 70 345 6789",
      nationalite: "Sénégalaise",
      date_naissance: new Date("2002-12-01")
    },
    formation_souhaitee: "Master Data Science",
    departement: "INFO",
    annee_entree: 4,
    documents: {
      licence: { mention: "Bien", annee: 2024, etablissement: "UCAD" },
      cv: true,
      lettre_motivation: true,
      releve_notes: true
    },
    scores: { note_dossier: 15.8, test_admission: 16.0, entretien: 15.5 },
    statut: "accepté",
    created_at: new Date()
  },
  {
    numero: "CAND-2025-004",
    candidat: {
      nom: "Gomis", prenom: "Lucie",
      email: "lucie.gomis@gmail.com",
      telephone: "+221 78 456 7890",
      nationalite: "Sénégalaise",
      date_naissance: new Date("2003-06-18")
    },
    formation_souhaitee: "Licence Gestion",
    departement: "GEST",
    annee_entree: 1,
    documents: {
      bac: { serie: "L", mention: "Assez Bien", annee: 2024, etablissement: "Lycée John F. Kennedy" },
      releve_notes: true,
      lettre_motivation: false,
      piece_identite: true
    },
    scores: { note_dossier: 12.5, test_admission: 11.0, entretien: null },
    statut: "dossier_incomplet",
    created_at: new Date()
  },
  {
    numero: "CAND-2025-005",
    candidat: {
      nom: "Konaté", prenom: "Ibrahim",
      email: "ibrahim.konate@gmail.com",
      telephone: "+221 77 567 8901",
      nationalite: "Malienne",
      date_naissance: new Date("2002-09-30")
    },
    formation_souhaitee: "Master Intelligence Artificielle",
    departement: "INFO",
    annee_entree: 4,
    documents: {
      licence: { mention: "Très Bien", annee: 2024, etablissement: "USTTB Bamako" },
      cv: true,
      lettre_motivation: true,
      releve_notes: true,
      visa_etudiant: true
    },
    scores: { note_dossier: 17.2, test_admission: 18.0, entretien: 17.5 },
    statut: "accepté",
    created_at: new Date()
  }
]);

// ── Collection 3 : Feedbacks sur les cours ───────────────────
db.feedbacks_cours.drop();
db.feedbacks_cours.insertMany([
  {
    cours_code: "INFO302",
    cours_intitule: "Data Engineering",
    annee_academique: "2024-2025",
    etudiant_matricule: "ETU001",
    notes: {
      qualite_contenu: 5,
      clarte_explications: 4,
      disponibilite_enseignant: 5,
      pertinence_tp: 5,
      difficulte: 4
    },
    note_globale: 4.6,
    commentaire: "Cours très pertinent et bien structuré. Les TPs sur Spark et MinIO sont excellents. Je recommande fortement ce cours.",
    points_positifs: ["Contenu à jour", "TPs pratiques", "Enseignant disponible"],
    points_amelioration: ["Ajouter plus d'exercices sur Kafka"],
    recommande: true,
    created_at: new Date()
  },
  {
    cours_code: "INFO302",
    cours_intitule: "Data Engineering",
    annee_academique: "2024-2025",
    etudiant_matricule: "ETU004",
    notes: {
      qualite_contenu: 5,
      clarte_explications: 5,
      disponibilite_enseignant: 4,
      pertinence_tp: 5,
      difficulte: 3
    },
    note_globale: 4.4,
    commentaire: "Excellent cours. Le projet final est très formateur.",
    points_positifs: ["Projet final réaliste", "Bonne progression pédagogique"],
    points_amelioration: ["Accélérer sur les bases au début"],
    recommande: true,
    created_at: new Date()
  },
  {
    cours_code: "INFO301",
    cours_intitule: "Bases de Données Avancées",
    annee_academique: "2024-2025",
    etudiant_matricule: "ETU002",
    notes: {
      qualite_contenu: 4,
      clarte_explications: 4,
      disponibilite_enseignant: 3,
      pertinence_tp: 4,
      difficulte: 4
    },
    note_globale: 3.8,
    commentaire: "Cours solide mais parfois difficile à suivre. Les TPs sont bien.",
    points_positifs: ["Contenu exhaustif"],
    points_amelioration: ["Plus de temps pour les questions", "Support de cours à améliorer"],
    recommande: true,
    created_at: new Date()
  },
  {
    cours_code: "MATH301",
    cours_intitule: "Analyse Avancée",
    annee_academique: "2024-2025",
    etudiant_matricule: "ETU003",
    notes: {
      qualite_contenu: 5,
      clarte_explications: 3,
      disponibilite_enseignant: 4,
      pertinence_tp: 4,
      difficulte: 5
    },
    note_globale: 4.2,
    commentaire: "Cours difficile mais l'enseignante est très compétente. Nécessite beaucoup de travail personnel.",
    points_positifs: ["Niveau académique élevé", "Enseignante passionnée"],
    points_amelioration: ["Plus d'exemples concrets", "Ralentir le rythme"],
    recommande: false,
    created_at: new Date()
  },
  {
    cours_code: "INFO401",
    cours_intitule: "Machine Learning",
    annee_academique: "2024-2025",
    etudiant_matricule: "ETU009",
    notes: {
      qualite_contenu: 5,
      clarte_explications: 5,
      disponibilite_enseignant: 5,
      pertinence_tp: 5,
      difficulte: 4
    },
    note_globale: 4.8,
    commentaire: "Le meilleur cours de la formation ! Très pratique avec des cas réels.",
    points_positifs: ["Kaggle competitions", "Projets réels", "Super ambiance"],
    points_amelioration: ["Rien à signaler"],
    recommande: true,
    created_at: new Date()
  }
]);

// Création des index
db.evenements.createIndex({ "date_debut": 1 });
db.evenements.createIndex({ "type": 1 });
db.candidatures.createIndex({ "numero": 1 }, { unique: true });
db.candidatures.createIndex({ "statut": 1 });
db.feedbacks_cours.createIndex({ "cours_code": 1 });
db.feedbacks_cours.createIndex({ "annee_academique": 1 });

print("✅ MongoDB initialisé avec succès : evenements, candidatures, feedbacks_cours");
