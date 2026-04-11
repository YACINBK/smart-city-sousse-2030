# ANALYSE THÉORIQUE ET CORRECTIONS : SMART CITY PLATFORM

## 1. Audit du Diagramme Entité-Association (E/A)
Après analyse de l'image du diagramme E/A et comparaison avec le cahier des charges (`bdd-theorie.pdf`), plusieurs corrections sont nécessaires pour garantir l'intégrité des données.

### 1.1. Correction des Cardinalités
*   **Relation Trajet - Véhicule** :
    *   *Erreur dans le diagramme* : Affiché en `0:n` -- `0:n` (plusieurs-à-plusieurs).
    *   *Correction* : Un trajet est effectué par **un et un seul** véhicule. Un véhicule peut effectuer plusieurs trajets.
    *   **Cardinalités Correctes** : `Trajet (1,1)` --- effectue --- `Véhicule (1,n)`.
*   **Relation Capteur - Propriétaire** :
    *   *Audit* : Le diagramme affiche `1:1` et `1:n`. C'est correct sur le fond (1 propriétaire possède N capteurs), mais la notation standard est `Propriétaire (1,n)` --- possède --- `Capteur (1,1)`.
*   **Relation Intervention - Technicien** :
    *   *Audit* : Le diagramme utilise deux liens (`intervient` et `valide`). C'est une excellente modélisation de la contrainte métier "2 techniciens par intervention". Dans le modèle relationnel, cela se traduit par une table associative avec un attribut de lien `role`.

---

## 2. Modèle Logique de Données (MLD) Optimisé
Le passage du diagramme E/A au relationnel doit suivre ces règles de dérivation :

*   **Propriétaire**(__id_proprietaire__, nom, type, adresse, telephone, email)
*   **Capteur**(__id_capteur__, type, latitude, longitude, statut, date_installation, *id_proprietaire*)
*   **Technicien**(__id_technicien__, nom, certification)
*   **Intervention**(__id_intervention__, date_heure, type_intervention, duree, cout, impact_co2, *id_capteur*)
*   **Intervention_Technicien**(__#id_intervention, #id_technicien__, role)
*   **Citoyen**(__id_citoyen__, nom, adresse, telephone, email, score_ecologique, preferences_mobilite)
*   **Consultation**(__id_consultation__, titre, date_debut, date_fin, statut)
*   **Participation**(__#id_citoyen, #id_consultation__, date_participation)
*   **Vehicule_Autonome**(__id_vehicule__, plaque_immatriculation, type_vehicule, energie_utilisee)
*   **Trajet**(__id_trajet__, origine, destination, duree, economie_co2, *id_vehicule*)

---

## 3. Analyse de la Normalisation

### 3.1. Dépendances Fonctionnelles (DF)
Les clés primaires déterminent de manière unique tous les autres attributs de leur relation :
*   `id_capteur` $\rightarrow$ `type, latitude, longitude, statut, date_installation, id_proprietaire`
*   `id_trajet` $\rightarrow$ `origine, destination, duree, economie_co2, id_vehicule`
*   `id_intervention` $\rightarrow$ `date_heure, type, cout, id_capteur`

### 3.2. Passage en Forme Normale de Boyce-Codd (BCNF)
Le schéma est en **BCNF** car :
1.  **1FN** : Tous les attributs sont atomiques.
2.  **2FN** : Tout attribut n'appartenant pas à une clé ne dépend d'aucune partie d'une clé candidate (pas de dépendances partielles).
3.  **3FN** : Tout attribut n'appartenant pas à une clé ne dépend pas d'un autre attribut non-clé (pas de dépendances transitives).
4.  **BCNF** : Pour toute dépendance fonctionnelle non triviale $X \rightarrow Y$, $X$ est une clé candidate.
    *   *Exemple* : Dans `Capteur`, seule la clé `id_capteur` permet de déterminer les autres champs. Il n'y a pas de déterminant qui ne soit pas une clé.

---

## 4. Réponses aux Questions Théoriques du Rapport
*   **Pourquoi une table associative pour les techniciens ?** Pour respecter la contrainte de cardinalité N-N et permettre l'attribution de rôles distincts (intervenant vs validateur) sans dupliquer les données de l'intervention.
*   **Comment assurer l'intégrité référentielle ?** Par l'utilisation de clés étrangères (FK) avec contrainte `ON DELETE CASCADE` ou `RESTRICT` selon la sensibilité des données.
*   **Impact de la modélisation sur les performances ?** L'indexation des UUID et des colonnes de recherche fréquente (ex: `quartier` dans Capteur) permet des jointures rapides malgré la normalisation poussée.
