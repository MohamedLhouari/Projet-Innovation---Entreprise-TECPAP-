# Script de lancement pour Linux/Mac
#!/bin/bash

echo "============================================================"
echo "Agent IA de Décision pour l'Amélioration de l'OEE - TECPAP"
echo "============================================================"
echo ""

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python 3 n'est pas installé"
    exit 1
fi

echo "[1/3] Vérification de Python... OK"
echo ""

# Installation des dépendances si nécessaire
echo "[2/3] Vérification des dépendances..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installation des dépendances en cours..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERREUR: Échec de l'installation des dépendances"
        exit 1
    fi
else
    echo "Dépendances déjà installées"
fi
echo ""

echo "[3/3] Démarrage de l'application..."
echo ""
echo "============================================================"
echo "L'application sera accessible sur: http://localhost:5000"
echo "============================================================"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

# Lancement de l'application
python3 app.py
