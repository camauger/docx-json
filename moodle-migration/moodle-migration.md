# Plan de migration de Moodle 3.11 vers Moodle 4.5.3

## Phase 1 : Préparation et planification

### Analyse de l'environnement actuel

* Inventaire des sites Moodle 3.11 (https://jenseigneadistance.teluq.ca/ sera considéré comme une priorité)
* Documentation de la configuration actuelle
* Identification des plugins et vérification de compatibilité

### Planification et communication

* Établissement du calendrier de migration
* Préparation d'un environnement de test

## Phase 2 : Sauvegarde des données

### Sauvegarde complète du système

* Sauvegarde de la base de données
* Archivage du répertoire moodledata
* Sauvegarde des fichiers de configuration
* Documentation des personnalisations

### Sauvegarde des cours

* Connexion en administrateur
* Navigation vers "Administration du cours" > "Sauvegarde"
* Sélection des options complètes (activités, ressources, blocs, filtres, etc.)
* Organisation structurée des fichiers .mbz par catégorie
* Vérification de l'intégrité des sauvegardes

### Extraction des données spécifiques

* Export des utilisateurs et leurs rôles
* Documentation des catégories de cours
* Export des cohortes et groupes
* Captures d'écran des configurations importantes

## Phase 3 : Installation de Moodle 4.5.3

### Préparation de l'environnement

* Vérification des prérequis (PHP 8.0+, MySQL 5.7+/MariaDB 10.4+/PostgreSQL 13+)
* Contrôle des extensions PHP requises

### Installation

* Téléchargement de Moodle 4.5.3
* Décompression dans le répertoire web
* Création/préparation de la base de données
* Adaptation du fichier config.php
* Exécution du script d'installation

### Configuration initiale

* Paramétrage du site (nom, langue, fuseau horaire)
* Installation des plugins compatibles
* Configuration du thème

## Phase 4 : Migration des contenus

### Restauration de la structure

* Recréation des catégories de cours
* Import des utilisateurs
* Reconfiguration des cohortes et groupes

### Restauration des cours

* Navigation vers "Administration du site" > "Cours" > "Restaurer un cours"
* Import des fichiers .mbz
* Sélection de l'option "Restaurer comme nouveau cours"
* Placement dans la catégorie appropriée
* Vérification des paramètres de restauration
* Traitement par lots pour les cours volumineux

### Vérification post-restauration

* Contrôle des activités et ressources
* Vérification des liens internes
* Contrôle des rôles et permissions
* Test des accès utilisateurs

## Phase 5 : Adaptation à Moodle 4.5.3

### Formation et documentation

* Documentation des changements d'interface
* Création de guides d'utilisation
* Organisation de sessions de formation

### Optimisation et personnalisation

* Ajustement des paramètres spécifiques
* Configuration du tableau de bord et navigation
* Optimisation des performances
* Adaptation des thèmes

## Phase 6 : Tests et mise en production

### Tests approfondis

* Vérification des fonctionnalités principales
* Test des scénarios d'utilisation
* Tests de charge
* Vérification de compatibilité multi-navigateurs/appareils

### Mise en production

* Définition de la date de mise en production
* Ouverture progressive de l'accès

## Phase 7 : Suivi et ajustements

### Surveillance et support

* Monitoring des journaux d'erreurs
* Support technique renforcé

### Ajustements finaux

* Correctifs basés sur les retours
* Optimisation des performances
* Complétion de la documentation
