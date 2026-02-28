-- ============================================================
-- INITIALISATION BASE UNIVERSITÉ (PostgreSQL)
-- Source 1 : Données relationnelles
-- ============================================================

-- Table des départements
CREATE TABLE IF NOT EXISTS departements (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    responsable VARCHAR(100),
    budget NUMERIC(12,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des étudiants
CREATE TABLE IF NOT EXISTS etudiants (
    id SERIAL PRIMARY KEY,
    matricule VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE,
    email VARCHAR(150) UNIQUE,
    departement_id INTEGER REFERENCES departements(id),
    annee_etude INTEGER CHECK (annee_etude BETWEEN 1 AND 5),
    statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif','suspendu','diplome')),
    moyenne_generale NUMERIC(4,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des enseignants
CREATE TABLE IF NOT EXISTS enseignants (
    id SERIAL PRIMARY KEY,
    matricule VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    grade VARCHAR(50),
    departement_id INTEGER REFERENCES departements(id),
    specialite VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des cours
CREATE TABLE IF NOT EXISTS cours (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    intitule VARCHAR(200) NOT NULL,
    credits INTEGER,
    heures_cm INTEGER,
    heures_td INTEGER,
    heures_tp INTEGER,
    enseignant_id INTEGER REFERENCES enseignants(id),
    departement_id INTEGER REFERENCES departements(id),
    semestre VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des inscriptions
CREATE TABLE IF NOT EXISTS inscriptions (
    id SERIAL PRIMARY KEY,
    etudiant_id INTEGER REFERENCES etudiants(id),
    cours_id INTEGER REFERENCES cours(id),
    annee_academique VARCHAR(10),
    date_inscription TIMESTAMP DEFAULT NOW(),
    UNIQUE(etudiant_id, cours_id, annee_academique)
);

-- Table des notes
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    etudiant_id INTEGER REFERENCES etudiants(id),
    cours_id INTEGER REFERENCES cours(id),
    note_cc NUMERIC(4,2),
    note_exam NUMERIC(4,2),
    note_finale NUMERIC(4,2),
    mention VARCHAR(20),
    annee_academique VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des salles
CREATE TABLE IF NOT EXISTS salles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    capacite INTEGER,
    type VARCHAR(50),
    batiment VARCHAR(50),
    disponible BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- DONNÉES DE TEST
-- ============================================================

INSERT INTO departements (nom, code, responsable, budget) VALUES
('Informatique', 'INFO', 'Dr. Diallo Mamadou', 15000000.00),
('Mathématiques', 'MATH', 'Dr. Sow Aissatou', 10000000.00),
('Physique', 'PHY', 'Dr. Ba Ibrahim', 12000000.00),
('Gestion', 'GEST', 'Dr. Ndiaye Fatou', 11000000.00),
('Langues', 'LANG', 'Dr. Traoré Moussa', 8000000.00);

INSERT INTO enseignants (matricule, nom, prenom, email, grade, departement_id, specialite) VALUES
('ENS001', 'Diallo', 'Mamadou', 'mdiallo@univ.sn', 'Professeur', 1, 'Intelligence Artificielle'),
('ENS002', 'Sow', 'Aissatou', 'asow@univ.sn', 'Maître de Conférences', 2, 'Algèbre'),
('ENS003', 'Ba', 'Ibrahim', 'iba@univ.sn', 'Professeur', 3, 'Mécanique Quantique'),
('ENS004', 'Ndiaye', 'Fatou', 'fndiaye@univ.sn', 'Maître de Conférences', 4, 'Finance'),
('ENS005', 'Traoré', 'Moussa', 'mtraore@univ.sn', 'Assistant', 1, 'Réseaux et Sécurité'),
('ENS006', 'Kane', 'Aminata', 'akane@univ.sn', 'Professeur', 1, 'Data Engineering'),
('ENS007', 'Cissé', 'Omar', 'ocisse@univ.sn', 'Assistant', 2, 'Statistiques');

INSERT INTO etudiants (matricule, nom, prenom, date_naissance, email, departement_id, annee_etude, statut, moyenne_generale) VALUES
('ETU001', 'Fall', 'Oumar', '2001-03-15', 'ofall@etud.univ.sn', 1, 3, 'actif', 14.5),
('ETU002', 'Diop', 'Mariama', '2002-07-22', 'mdiop@etud.univ.sn', 1, 2, 'actif', 16.2),
('ETU003', 'Sarr', 'Ibrahima', '2000-11-10', 'isarr@etud.univ.sn', 2, 4, 'actif', 13.8),
('ETU004', 'Ndiaye', 'Rokhaya', '2001-05-30', 'rndiaye@etud.univ.sn', 1, 3, 'actif', 15.0),
('ETU005', 'Mbaye', 'Cheikh', '2003-01-18', 'cmbaye@etud.univ.sn', 4, 1, 'actif', 11.5),
('ETU006', 'Thiaw', 'Ndéye', '2001-09-25', 'nthiaw@etud.univ.sn', 1, 3, 'actif', 17.1),
('ETU007', 'Faye', 'Moussa', '2000-12-05', 'mfaye@etud.univ.sn', 3, 4, 'actif', 12.9),
('ETU008', 'Gueye', 'Aminata', '2002-04-14', 'agueye@etud.univ.sn', 2, 2, 'actif', 15.7),
('ETU009', 'Seck', 'Aliou', '1999-08-20', 'aseck@etud.univ.sn', 1, 5, 'actif', 13.2),
('ETU010', 'Badji', 'Coumba', '2002-02-28', 'cbadji@etud.univ.sn', 4, 2, 'actif', 14.8),
('ETU011', 'Diouf', 'Seydou', '2001-06-12', 'sdiouf@etud.univ.sn', 1, 3, 'suspendu', 9.5),
('ETU012', 'Mendy', 'Awa', '2000-10-03', 'amendy@etud.univ.sn', 3, 4, 'actif', 16.8),
('ETU013', 'Diatta', 'Lamine', '2003-03-22', 'ldiatta@etud.univ.sn', 1, 1, 'actif', 13.0),
('ETU014', 'Coly', 'Fatimata', '2001-07-16', 'fcoly@etud.univ.sn', 2, 3, 'actif', 14.2),
('ETU015', 'Tendeng', 'Pascal', '2000-05-08', 'ptendeng@etud.univ.sn', 4, 5, 'diplome', 15.9);

INSERT INTO cours (code, intitule, credits, heures_cm, heures_td, heures_tp, enseignant_id, departement_id, semestre) VALUES
('INFO301', 'Bases de Données Avancées', 4, 30, 15, 15, 1, 1, 'S5'),
('INFO302', 'Data Engineering', 4, 30, 10, 20, 6, 1, 'S5'),
('INFO201', 'Algorithmes et Structures de Données', 3, 25, 15, 10, 5, 1, 'S3'),
('INFO101', 'Introduction à la Programmation', 3, 20, 10, 15, 5, 1, 'S1'),
('MATH301', 'Analyse Avancée', 4, 35, 20, 0, 2, 2, 'S5'),
('MATH201', 'Probabilités et Statistiques', 3, 30, 15, 0, 7, 2, 'S3'),
('PHY301', 'Physique Quantique', 4, 35, 15, 10, 3, 3, 'S5'),
('GEST201', 'Finance d''Entreprise', 3, 30, 15, 0, 4, 4, 'S3'),
('INFO401', 'Machine Learning', 5, 40, 15, 20, 1, 1, 'S7'),
('INFO402', 'Sécurité Informatique', 4, 30, 15, 15, 5, 1, 'S7');

INSERT INTO inscriptions (etudiant_id, cours_id, annee_academique) VALUES
(1,1,'2024-2025'),(1,2,'2024-2025'),(1,3,'2024-2025'),
(2,1,'2024-2025'),(2,2,'2024-2025'),(2,4,'2024-2025'),
(3,5,'2024-2025'),(3,6,'2024-2025'),
(4,1,'2024-2025'),(4,2,'2024-2025'),(4,3,'2024-2025'),
(5,8,'2024-2025'),
(6,1,'2024-2025'),(6,2,'2024-2025'),(6,9,'2024-2025'),
(7,7,'2024-2025'),
(8,5,'2024-2025'),(8,6,'2024-2025'),
(9,9,'2024-2025'),(9,10,'2024-2025'),
(10,8,'2024-2025'),
(12,7,'2024-2025'),
(13,4,'2024-2025'),
(14,5,'2024-2025'),(14,6,'2024-2025');

INSERT INTO notes (etudiant_id, cours_id, note_cc, note_exam, note_finale, mention, annee_academique) VALUES
(1,1,14.0,15.0,14.6,'Bien','2024-2025'),
(1,2,16.0,13.0,14.2,'Assez Bien','2024-2025'),
(1,3,13.0,14.0,13.6,'Assez Bien','2024-2025'),
(2,1,17.0,16.0,16.4,'Très Bien','2024-2025'),
(2,2,15.0,17.0,16.2,'Bien','2024-2025'),
(4,1,15.0,15.0,15.0,'Bien','2024-2025'),
(4,2,16.0,14.0,14.8,'Bien','2024-2025'),
(6,1,18.0,17.0,17.4,'Très Bien','2024-2025'),
(6,2,16.0,18.0,17.2,'Très Bien','2024-2025'),
(9,9,13.0,13.0,13.0,'Assez Bien','2024-2025'),
(9,10,14.0,12.0,12.8,'Assez Bien','2024-2025');

INSERT INTO salles (nom, capacite, type, batiment, disponible) VALUES
('Amphi A', 300, 'Amphithéâtre', 'Bâtiment Principal', TRUE),
('Amphi B', 200, 'Amphithéâtre', 'Bâtiment Sciences', TRUE),
('Salle 101', 40, 'TD', 'Bâtiment A', TRUE),
('Salle 102', 40, 'TD', 'Bâtiment A', TRUE),
('Labo Info 1', 30, 'TP Informatique', 'Bâtiment Informatique', TRUE),
('Labo Info 2', 30, 'TP Informatique', 'Bâtiment Informatique', FALSE),
('Salle 201', 50, 'Cours Magistral', 'Bâtiment B', TRUE),
('Labo Physique', 25, 'TP Sciences', 'Bâtiment Sciences', TRUE);
