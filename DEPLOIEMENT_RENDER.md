# Guide de Déploiement sur Render.com

## 🚀 Étapes de Déploiement

### 1. Préparer le Repository GitHub

```powershell
# Si pas encore fait, initialiser Git
git init
git add .
git commit -m "Application prête pour déploiement Render"

# Créer un repo sur GitHub et le connecter
git remote add origin https://github.com/VOTRE_USERNAME/tecpap-ia-oee.git
git branch -M main
git push -u origin main
```

### 2. Créer un Compte Render

1. Aller sur https://render.com
2. S'inscrire avec GitHub (recommandé)
3. Vérifier votre email

### 3. Déployer l'Application

1. **Dans le Dashboard Render**, cliquer sur **"New +"** → **"Web Service"**

2. **Connecter votre Repository GitHub** :
   - Autoriser Render à accéder à vos repos
   - Sélectionner `tecpap-ia-oee`

3. **Configuration du Service** :

   | Paramètre | Valeur |
   |-----------|--------|
   | **Name** | `tecpap-ia-oee` |
   | **Region** | Frankfurt (plus proche de France) |
   | **Branch** | `main` |
   | **Root Directory** | (laisser vide) |
   | **Runtime** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
   | **Instance Type** | **Free** |

4. **Variables d'Environnement (optionnel)** :
   - `FLASK_ENV` = `production`
   - `PYTHONUNBUFFERED` = `1`

5. **Cliquer sur "Create Web Service"**

### 4. Attendre le Déploiement

- **Durée** : 5-8 minutes (première fois)
  - 2-3 min : Installation des dépendances
  - 2-3 min : Génération des données
  - 1-2 min : Entraînement des modèles

- **Suivre les logs** en temps réel dans l'interface Render

### 5. Accéder à l'Application

Votre URL sera générée automatiquement :
```
https://tecpap-ia-oee.onrender.com
```

ou

```
https://tecpap-ia-oee-xxxx.onrender.com
```

## ⚙️ Fichiers de Configuration Créés

- ✅ **Procfile** : Commande de démarrage pour Render
- ✅ **runtime.txt** : Version Python (3.11.7)
- ✅ **.env.example** : Exemple de variables d'environnement
- ✅ **requirements.txt** : Avec gunicorn ajouté
- ✅ **app.py** : Modifié pour port dynamique
- ✅ **.gitignore** : Mis à jour

## 🔄 Redéploiement Automatique

Chaque fois que vous faites un `git push`, Render redéploie automatiquement :

```powershell
git add .
git commit -m "Mise à jour"
git push origin main
```

## ⚠️ Limitations du Plan Gratuit

- **750 heures/mois** : Largement suffisant
- **Inactivité** : L'app s'endort après 15 min sans trafic
- **Cold Start** : 30-60 secondes au réveil
- **RAM** : 512 MB (suffisant pour ce projet)

## 💡 Optimisations

### Pour accélérer le Cold Start :

1. **Maintenir l'app éveillée** avec UptimeRobot (gratuit) :
   - Ping toutes les 14 minutes
   - URL : https://uptimerobot.com

2. **Réduire le temps de génération** :
   - Les données sont régénérées à chaque déploiement
   - En production, connecter à Evocon réel

## 🐛 Troubleshooting

### Erreur "Build Failed"
```bash
# Vérifier que requirements.txt est correct
pip install -r requirements.txt
```

### Erreur "Application Error"
```bash
# Vérifier les logs dans Render Dashboard
# Souvent dû à :
# - Timeout (augmenter à 120s)
# - Mémoire insuffisante (réduire workers)
```

### L'application est lente au démarrage
- **Normal** : Génération de 59K données + entraînement ML
- **Solution** : Patienter 2-3 minutes au premier accès

## 📊 Monitoring

Dans le Dashboard Render, vous pouvez voir :
- **Logs en temps réel**
- **Métriques** (CPU, RAM, Requests)
- **Événements de déploiement**
- **URL de l'application**

## 🎯 Prochaines Étapes

1. ✅ Déployer sur Render
2. Tester toutes les fonctionnalités
3. Partager l'URL avec TECPAP
4. Préparer la présentation

## 🔗 Liens Utiles

- **Render Docs** : https://render.com/docs
- **Dashboard** : https://dashboard.render.com
- **Status** : https://status.render.com

---

**Votre application est maintenant prête pour Render ! 🚀**

Pour déployer :
```powershell
git add .
git commit -m "Configuration Render complète"
git push origin main
```

Puis créez le Web Service sur Render.com
