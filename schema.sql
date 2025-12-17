-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Gestion des Capteurs Intelligents
-- Sensors table
CREATE TABLE IF NOT EXISTS capteurs (
    id_capteur UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_capteur VARCHAR(50) NOT NULL CHECK (type_capteur IN ('qualité_air', 'trafic', 'énergie', 'déchets', 'éclairage')),
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    statut VARCHAR(20) NOT NULL CHECK (statut IN ('actif', 'en_maintenance', 'hors_service')),
    proprietaire_type VARCHAR(20) NOT NULL CHECK (proprietaire_type IN ('municipalité', 'privé')),
    nom_proprietaire VARCHAR(100),
    adresse_proprietaire TEXT,
    telephone_proprietaire VARCHAR(20),
    email_proprietaire VARCHAR(100),
    date_installation DATE NOT NULL
);

-- 2. Maintenance et Interventions
-- Technicians table (needed for interventions)
CREATE TABLE IF NOT EXISTS techniciens (
    id_technicien UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(100) NOT NULL,
    specialite VARCHAR(100),
    certifie BOOLEAN DEFAULT TRUE
);

-- Interventions table
CREATE TABLE IF NOT EXISTS interventions (
    id_intervention UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_capteur UUID REFERENCES capteurs(id_capteur),
    date_heure TIMESTAMP NOT NULL,
    type_intervention VARCHAR(20) NOT NULL CHECK (type_intervention IN ('prédictive', 'corrective', 'curative')),
    duree_minutes INTEGER,
    cout DECIMAL(10, 2),
    impact_environnemental_co2 DECIMAL(10, 2), -- CO2 reduction in kg
    id_technicien_intervenant UUID REFERENCES techniciens(id_technicien),
    id_technicien_validateur UUID REFERENCES techniciens(id_technicien),
    CONSTRAINT different_technicians CHECK (id_technicien_intervenant != id_technicien_validateur)
);

-- 3. Données des Citoyens Engagés
-- Citizens table
CREATE TABLE IF NOT EXISTS citoyens (
    id_citoyen UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(100) NOT NULL,
    adresse TEXT,
    email VARCHAR(100) UNIQUE,
    telephone VARCHAR(20),
    score_ecologique INTEGER DEFAULT 0,
    preferences_mobilite TEXT, -- JSON or text description
    historique_consultations TEXT -- JSON or text description
);

-- 4. Gestion des Véhicules Autonomes Municipaux
-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicules (
    immatriculation VARCHAR(20) PRIMARY KEY,
    type_vehicule VARCHAR(50),
    energie_utilisee VARCHAR(50)
);

-- Routes/Trips table
CREATE TABLE IF NOT EXISTS trajets (
    id_trajet UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    immatriculation VARCHAR(20) REFERENCES vehicules(immatriculation),
    origine VARCHAR(100),
    destination VARCHAR(100),
    date_depart TIMESTAMP,
    date_arrivee TIMESTAMP,
    duree_minutes INTEGER GENERATED ALWAYS AS (EXTRACT(EPOCH FROM (date_arrivee - date_depart))/60) STORED,
    economie_co2 DECIMAL(10, 2)
);
