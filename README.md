# Agent IA de Décision pour l'Amélioration de l'OEE - TECPAP

## Description du Projet

Solution innovante d'intelligence artificielle pour optimiser l'Overall Equipment Effectiveness (OEE) dans un environnement industriel. Ce système transforme les données descriptives en recommandations prescriptives pour améliorer les performances de production de +1% à +5%.

## Fonctionnalités Principales

### 1. Prédiction OEE
- Prédiction des performances futures sur 7 jours
- Analyse des tendances par ligne de production
- Identification précoce des dérives de performance
- Confiance élevée grâce aux algorithmes Random Forest et Gradient Boosting

### 2. Recommandation Intelligente
- Sélection automatique de la meilleure ligne pour chaque production
- Simulation de scénarios (L1 vs L2 vs L3)
- Analyse coût/bénéfice en temps réel
- Optimisation multi-critères (OEE, coût, temps, qualité)

### 3. Système Expert d'Anomalies
- Base de connaissances de 2 ans d'historique
- Recherche de similarité pour trouver des solutions éprouvées
- Recommandations de résolution basées sur l'expérience
- Temps de résolution estimés et impact sur l'OEE

### 4. Analytics Avancés
- Visualisations interactives des performances
- Calcul d'impact des améliorations
- Analyse comparative des lignes
- Tableaux de bord en temps réel

## Architecture Technique

```
Agent IA OEE TECPAP/
│
├── app.py                      # Application Flask principale
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
│
├── data/
│   ├── data_loader.py         # Gestionnaire de données
│   └── generated/             # Données synthétiques générées
│       ├── oee_data.csv       # ~35,000 enregistrements OEE
│       ├── stops_data.csv     # ~17,000 arrêts
│       ├── quality_data.csv   # ~6,500 contrôles qualité
│       └── anomalies_data.csv # ~100 anomalies documentées
│
├── models/
│   ├── predictor.py           # Modèle de prédiction ML
│   ├── recommender.py         # Système de recommandation
│   ├── anomaly_expert.py      # Expert en anomalies
│   └── saved_models/          # Modèles entraînés
│
├── static/
│   ├── css/
│   │   └── style.css         # Styles professionnels
│   └── js/
│       └── main.js           # Logique frontend
│
└── templates/
    └── index.html            # Interface utilisateur
```

## Installation et Démarrage

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'Installation

1. **Installer les dépendances**
```powershell
pip install -r requirements.txt
```

2. **Lancer l'application**
```powershell
python app.py
```

3. **Accéder à l'interface**
- Ouvrir votre navigateur
- Naviguer vers: `http://localhost:5000`

L'application va automatiquement:
- Générer les données synthétiques (première exécution)
- Entraîner les modèles de prédiction
- Initialiser le système de recommandation
- Charger la base de connaissances des anomalies

## Données Synthétiques

Le système génère automatiquement des données volumineuses et réalistes simulant 2 ans d'historique Evocon:

### Volume de Données
- **35,000+** enregistrements OEE horaires
- **17,000+** arrêts documentés
- **6,500+** contrôles qualité
- **100+** anomalies avec solutions

### Caractéristiques
- 3 lignes de production (L1, L2, L3)
- 9 machines au total
- 10 types d'arrêts différents
- 6 types de défauts qualité
- Variations saisonnières et horaires réalistes
- Anomalies aléatoires (5% de probabilité)

## Modèles de Machine Learning

### 1. Prédiction OEE
- **Algorithmes**: Random Forest + Gradient Boosting
- **Features**: 15+ variables (temporelles, historiques, machines)
- **Performance**: MAE < 3%, R² > 0.75
- **Horizon**: 7 jours

### 2. Détection d'Anomalies
- **Méthode**: Analyse statistique multi-critères
- **Seuils adaptatifs** par ligne
- **Alertes en temps réel**

### 3. Système de Similarité
- **Technique**: TF-IDF + Cosine Similarity
- **Base**: Historique complet des anomalies
- **Précision**: Top 5 cas similaires avec score de confiance

## API Endpoints

### Dashboard
```
GET /api/dashboard
```
Retourne les métriques actuelles, prédictions, recommandations et alertes

### Prédictions
```
POST /api/predict
Body: {"line_id": "L1", "horizon": 7}
```
Prédit l'OEE pour une ligne spécifique

### Recommandations
```
GET /api/recommend?product_type=standard&quantity=1000
```
Recommande la meilleure ligne et simule les scénarios

### Anomalies
```
GET /api/anomalies?period=30
```
Récupère les anomalies récentes

```
POST /api/anomaly/similar
Body: {"description": "symptôme", "machine_id": "M1-1"}
```
Trouve des cas similaires et solutions

### Données Historiques
```
GET /api/historical?line_id=L1&days=90
```
Retourne les données historiques pour analyse

### Impact
```
GET /api/impact?improvement=3
```
Calcule l'impact d'une amélioration OEE

## Interface Utilisateur

### Onglets Disponibles

1. **Dashboard**
   - KPIs en temps réel des 3 lignes
   - Recommandation IA
   - Alertes actives
   - Graphique d'évolution

2. **Prédictions**
   - Prédictions 7 jours par ligne
   - Graphique de tendance
   - Tableau détaillé avec confiance

3. **Recommandations**
   - Simulateur de scénarios
   - Comparaison des lignes
   - Analyse coût/bénéfice

4. **Anomalies**
   - Recherche de solutions similaires
   - Historique des anomalies
   - Base de connaissances

5. **Analytics**
   - Calculateur d'impact
   - Graphiques historiques
   - Analyse comparative

## Impact Attendu

### Objectif Principal
**Amélioration de l'OEE de +1% à +5%**

### Bénéfices Attendus
- Meilleure allocation des ordres de production
- Réduction des arrêts non planifiés
- Décisions standardisées et data-driven
- Suppression des pertes évitables
- Pilotage proactif au lieu de réactif

### Exemple d'Impact (3% d'amélioration)
- OEE actuel: 74%
- OEE cible: 77%
- Gain annuel: ~250 heures de production
- Gain de productivité: ~4%

## Technologies Utilisées

### Backend
- **Flask 3.0**: Framework web Python
- **scikit-learn**: Machine Learning
- **pandas/numpy**: Manipulation de données
- **XGBoost/LightGBM**: Algorithmes avancés

### Frontend
- **HTML5/CSS3**: Interface responsive
- **JavaScript ES6**: Logique interactive
- **Chart.js**: Visualisations
- **Design moderne**: Sans framework lourd

### Data Science
- **Random Forest**: Prédiction robuste
- **Gradient Boosting**: Haute précision
- **TF-IDF**: Similarité textuelle
- **Feature Engineering**: 15+ variables calculées

## Évolutions Futures

1. **Intégration temps réel** avec Evocon via API
2. **Maintenance prédictive** avec ML avancé
3. **Optimisation automatique** des paramètres machines
4. **Rapports automatiques** PDF/Excel
5. **Application mobile** pour suivi terrain
6. **Alertes SMS/Email** configurables

## Support et Contact

Pour toute question concernant ce projet d'innovation:
- **Projet**: Agent IA de Décision OEE
- **Client**: TECPAP
- **Objectif**: Amélioration +1% à +5% OEE

## Licence

Projet d'innovation développé pour TECPAP - 2025

---

**Note**: Ce système utilise des données synthétiques pour la démonstration. En production, il sera connecté aux données réelles d'Evocon pour des résultats optimaux.
