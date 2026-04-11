# RA PPORT DE PROJET : SMART CITY ANALYTICS PLATFORM (Neo-Sousse 2030)

## 1. Contexte et Objectifs

### 1.1. Introduction
Dans le cadre de la modernisation des infrastructures urbaines de la métropole "Neo-Sousse 2030", ce projet vise à concevoir et déployer une plateforme digitale de gestion des données urbaines. L'objectif est de centraliser, analyser et visualiser les flux de données provenant de capteurs IoT, de véhicules autonomes et des interactions citoyennes.

### 1.2. Enjeux
*   **Optimisation des coûts** : Réduire les dépenses de maintenance via des interventions ciblées.
*   **Écologie** : Suivre et réduire l'empreinte carbone (trafic, qualité de l'air).
*   **Qualité de vie** : Améliorer les services aux citoyens (mobilité, participation publique).

---

## 2. Modélisation Théorique

### 2.1. Modèle Conceptuel de Données (MCD)
Le système s'articule autour de plusieurs entités clés identifiées lors de l'analyse métier :

*   **CAPTEUR** : Point central de la collecte (Air, Trafic, Énergie...). Il est géolocalisé et possède un statut.
*   **INTERVENTION** : Action de maintenance reliée à un capteur, impliquant des techniciens.
*   **CITOYEN** : Acteur participant à la vie de la cité (Consultations) et dont l'empreinte écologique est calculée.
*   **VEHICULE_AUTONOME & TRAJET** : Gestion de la flotte intelligente et calcul des économies de CO2 par trajet.

### 2.2. Schéma Relationnel & Normalisation
La base de données a été conçue pour respecter les formes normales jusqu'à la **BCNF (Boyce-Codd Normal Form)** afin d'éviter redondances et anomalies de mise à jour. 

#### Corrections du Modèle Conceptuel (E/A) :
*   **Relation Trajet - Véhicule** : Le diagramme initial présentait une relation N:M. Elle a été corrigée en **1:N** : un trajet appartient à un seul véhicule, tandis qu'un véhicule effectue plusieurs trajets (**Trajet(1,1) --- Véhicule(1,n)**).
*   **Gestion des Techniciens** : Utilisation d'une table associative pour gérer la relation N:N entre `Intervention` et `Technicien` avec un attribut de lien `role` (Intervenant vs Validateur).

#### Dépendances Fonctionnelles (DF) :
*   `id_capteur → type, latitude, longitude, statut, date_installation, id_proprietaire`
*   `id_trajet → origine, destination, duree, economie_co2, id_vehicule`

#### Justification BCNF :
Le schéma est en **BCNF** car pour chaque dépendance fonctionnelle non triviale $X \rightarrow Y$, le déterminant $X$ est une clé candidate.
1.  **1FN** : Tous les attributs sont atomiques.
2.  **2FN** : Pas de dépendances partielles (attributs non-clés dépendant d'une partie de la clé).
3.  **3FN** : Pas de dépendances transitives (ex: l'adresse du propriétaire n'est stockée que dans `Proprietaire`).
4.  **BCNF** : Pas de déterminant qui ne soit pas une clé candidate.

---

## 3. Architecture Technique

### 3.1. Stack Technologique
Le projet repose sur une architecture moderne séparant le Backend (Gestion de données) du Frontend (Visualisation), garantissant scalabilité et maintenance aisée.

*   **Backend** : **Django (Python)** + **Django REST Framework**.
    *   Rôle : ORM (Object-Relational Mapping), Gestion de la BDD, API RESTful.
    *   Base de Formées : **PostgreSQL** (Robuste pour les données relationnelles).
*   **Frontend** : **Streamlit**.
    *   Rôle : Dashboard interactif pour la Data Science et la visualisation temps réel.
*   **Visualisation** : **Folium** (Cartographie) + **Plotly** (Graphiques interactifs).

### 3.2. Pipeline ETL (Extract, Transform, Load) Embedded
Contrairement à une approche Batch traditionnelle, ce projet implémente un **ETL Temps Réel** intégré au Dashboard :

1.  **Extract (Extraction)** : Le Dashboard interroge l'API Django (`GET /api/capteurs/`, `/api/trajets/`) à chaque actualisation.
2.  **Transform (Transformation)** :
    *   Nettoyage des données (Gestion des valeurs nulles).
    *   Enrichissement (Calcul des taux de panne par quartier, Simulation AQI).
    *   Agrégation (Somme des économies CO2, Coûts totaux).
3.  **Load (Chargement)** : Injection des données traitées dans les composants visuels (Cartes Folium, Graphiques Plotly).

---

## 4. Implémentation Fonctionnelle

### 4.1. Simulation "Smart City" Intelligente
Pour démontrer capacités temps réel, un moteur de simulation (`simulate_step`) a été intégré au Backend :
*   **Volatilité** : À chaque "Pas de temps", 20% des capteurs changent d'état (Actif <-> Hors Service).
*   **Logique Métier** : Le centre-ville (Sousse Ville) est soumis à un stress plus élevé (pannes plus fréquentes).
*   **Auto-Guérison** : Le système déclenche automatiquement des interventions correctives sur les capteurs défaillants.
*   **Mobilité** : Les positions des véhicules autonomes sont recalculées dynamiquement.

### 4.2. Réponses aux Questions Métiers (KPIs)
Le Dashboard répond directement aux problématiques posées dans le cahier des charges :

1.  **"Quelles sont les zones les plus polluées ?"**
    *   *Réponse* : Onglet "Pollution". Histogramme des indices AQI (Air Quality Index) par quartier, calculé sur les dernières 24h.
2.  **"Quel est le taux de disponibilité des capteurs ?"**
    *   *Réponse* : Onglet "Disponibilité" & Sidebar. Graphique global + Tableau d'alerte classant les zones par taux de panne décroissant (ex: "Sousse Ville: 45% de pannes").
3.  **"Quels sont les citoyens les plus engagés ?"**
    *   *Réponse* : Onglet "Citoyens". Classement (Top 10) basé sur le `score_ecologique` calculé selon leurs modes de transport et participation.
4.  **"Combien d'interventions prédictives ?"**
    *   *Réponse* : Onglet "Interventions". Indicateur métrique dédié et courbe des coûts.
5.  **"Quels trajets ont réduit le plus de CO2 ?"**
    *   *Réponse* : Onglet "Trajets". Carte interactive traçant les lignes de parcours (Vert=Départ, Rouge=Arrivée) et Top 5 des économies réalisées.

---

## 5. Conclusion
Le projet "Smart City Analytics Platform" fournit une solution complète, allant de la modélisation rigoureuse des données (BCNF) à une interface utilisateur réactive. L'architecture découplée (API + Dashboard) permet une évolution future facile (ex: ajout d'une app mobile citoyenne se connectant à la même API).
La simulation intégrée démontre la robustesse du système face à des flux de données dynamiques et imprévisibles, validant ainsi sa pertinence pour le pilotage urbain de Neo-Sousse 2030.
