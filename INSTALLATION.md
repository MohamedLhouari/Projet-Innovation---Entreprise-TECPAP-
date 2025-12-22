# Guide d'Installation Rapide

## Prérequis
- **Python 3.8 ou supérieur** (testé avec Python 3.12)
- **pip** (gestionnaire de paquets Python)
- **Navigateur web moderne** (Chrome, Firefox, Edge)

## Installation en 3 Étapes

### Étape 1: Vérifier Python
Ouvrir un terminal (PowerShell sur Windows) et vérifier:
```powershell
python --version
```
Vous devriez voir: `Python 3.x.x`

### Étape 2: Installer les dépendances
Dans le dossier du projet:
```powershell
pip install -r requirements.txt
```

Cette commande installe:
- Flask (framework web)
- pandas & numpy (manipulation de données)
- scikit-learn (machine learning)
- joblib (sauvegarde des modèles)

**Durée**: 1-2 minutes

### Étape 3: Lancer l'application
```powershell
python app.py
```

OU utiliser le script fourni:
```powershell
.\start.bat
```

## Première Utilisation

### Démarrage Automatique
Au premier lancement, l'application va automatiquement:

1. **Créer les dossiers nécessaires** (2 secondes)
2. **Générer les données synthétiques** (15-30 secondes)
   - 35,000+ enregistrements OEE
   - 17,000+ arrêts
   - 6,500+ contrôles qualité
   - 100+ anomalies documentées
3. **Entraîner les modèles ML** (30-60 secondes)
4. **Initialiser le système** (5 secondes)

**Durée totale du premier lancement**: ~1-2 minutes

### Démarrages Suivants
Les données et modèles sont sauvegardés:
- **Durée**: ~5 secondes seulement

### Accès à l'Interface
Une fois démarré, vous verrez:
```
============================================================
Agent IA de Décision pour l'Amélioration de l'OEE - TECPAP
============================================================

Initialisation des composants...
✓ Données chargées
✓ Modèle de prédiction entraîné
✓ Système de recommandation initialisé
✓ Base de connaissances des anomalies chargée

Démarrage du serveur Flask...
Accédez à l'application sur: http://localhost:5000
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

**Ouvrir votre navigateur** et aller à: `http://localhost:5000`

## Structure des Fichiers Générés

Après le premier lancement:
```
Projet Innovation TECPAP/
│
├── data/
│   └── generated/              # Données créées automatiquement
│       ├── oee_data.csv
│       ├── stops_data.csv
│       ├── quality_data.csv
│       └── anomalies_data.csv
│
└── models/
    └── saved_models/           # Modèles ML entraînés
        ├── oee_model.pkl
        ├── scaler.pkl
        └── features.pkl
```

## Résolution de Problèmes

### Erreur: "Python n'est pas reconnu"
**Solution**: Ajouter Python au PATH système
1. Réinstaller Python en cochant "Add Python to PATH"
2. OU ajouter manuellement le chemin Python au PATH

### Erreur lors de l'installation de packages
**Solution**:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Port 5000 déjà utilisé
**Solution**: Modifier dans app.py la dernière ligne:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changer 5000 en 5001
```

### L'application se ferme immédiatement
**Solution**: Vérifier les erreurs dans le terminal
- Souvent dû à des dépendances manquantes
- Réinstaller: `pip install -r requirements.txt --force-reinstall`

### Données ne se chargent pas
**Solution**: 
1. Supprimer le dossier `data/generated/`
2. Relancer l'application
3. Les données seront régénérées

## Arrêt de l'Application

Dans le terminal où l'application tourne:
- **Windows**: `Ctrl + C`
- **Linux/Mac**: `Ctrl + C`

## Mise à Jour

Pour mettre à jour les dépendances:
```powershell
pip install -r requirements.txt --upgrade
```

Pour réentraîner les modèles:
1. Supprimer `models/saved_models/`
2. Relancer l'application

## Performance Attendue

### Ressources Système
- **RAM**: 500 MB - 1 GB
- **CPU**: Minimal (< 5% en fonctionnement normal)
- **Disque**: ~50 MB (données + modèles)

### Temps de Réponse
- **Dashboard**: < 500 ms
- **Prédictions**: < 1 seconde
- **Recherche d'anomalies**: < 2 secondes
- **Simulation de scénarios**: < 1 seconde

## Utilisation en Production

### Pour une démonstration
Le mode actuel (debug=True) est parfait pour:
- Démonstrations
- Tests
- Développement

### Pour un déploiement réel
Modifier `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

Et utiliser un serveur WSGI comme Gunicorn:
```powershell
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Support

Pour toute question:
1. Consulter le [README.md](README.md) pour la documentation complète
2. Consulter [PRESENTATION_TECPAP.md](PRESENTATION_TECPAP.md) pour le guide de présentation
3. Vérifier que toutes les dépendances sont installées

## Checklist de Vérification

Avant une démonstration, vérifier:
- [ ] Python installé et accessible
- [ ] Dépendances installées (`pip list` doit montrer Flask, pandas, etc.)
- [ ] Port 5000 disponible
- [ ] Données générées dans `data/generated/`
- [ ] Modèles entraînés dans `models/saved_models/`
- [ ] Application démarre sans erreur
- [ ] Interface accessible sur http://localhost:5000
- [ ] Dashboard affiche les données
- [ ] Tous les onglets fonctionnent

## Commandes Utiles

### Vérifier les packages installés
```powershell
pip list
```

### Vérifier la version Python
```powershell
python --version
```

### Tester l'importation des modules
```powershell
python -c "import flask, pandas, sklearn; print('OK')"
```

### Voir les logs en temps réel
L'application affiche automatiquement les logs dans le terminal

---

**Vous êtes prêt!** L'application devrait maintenant fonctionner parfaitement.
