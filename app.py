"""
Agent IA de Décision pour l'Amélioration de l'OEE - TECPAP
Application principale Flask
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import os
from models.predictor import OEEPredictor
from models.recommender import LineRecommender
from models.anomaly_expert import AnomalyExpert
from data.data_loader import DataLoader
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tecpap-innovation-oee-2025'

# Initialisation des composants IA
data_loader = DataLoader()
oee_predictor = OEEPredictor()
line_recommender = LineRecommender()
anomaly_expert = AnomalyExpert()

# Variable pour suivre l'état d'initialisation
_system_initialized = False

def initialize_system():
    """Initialisation du système au démarrage (compatible Gunicorn)"""
    global _system_initialized
    
    if _system_initialized:
        return True
    
    print("=" * 60)
    print("Agent IA de Décision OEE - TECPAP - Initialisation")
    print("=" * 60)
    
    try:
        # 1. Chargement des données
        print("\n[1/4] Chargement des données...")
        if not data_loader.load_data():
            print("Erreur lors du chargement des données")
            return False
        print("✓ Données chargées avec succès")
        
        # 2. Entraînement du modèle de prédiction
        print("\n[2/4] Entraînement du modèle de prédiction OEE...")
        oee_predictor.train()
        print("✓ Modèle entraîné")
        
        # 3. Initialisation du système de recommandation
        print("\n[3/4] Initialisation du système de recommandation...")
        line_recommender.initialize()
        print("✓ Recommandation initialisée")
        
        # 4. Chargement de la base de connaissances
        print("\n[4/4] Chargement de la base de connaissances...")
        anomaly_expert.load_knowledge_base()
        print("✓ Expert en anomalies prêt")
        
        print("\n" + "=" * 60)
        print("✅ Système opérationnel!")
        print("=" * 60 + "\n")
        
        _system_initialized = True
        return True
        
    except Exception as e:
        print(f"\nErreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False

# Initialisation automatique au chargement du module (fonctionne avec Gunicorn)
initialize_system()

@app.route('/')
def index():
    """Dashboard principal"""
    return render_template('index.html')

@app.route('/api/dashboard')
def get_dashboard_data():
    """Récupération des données du dashboard"""
    try:
        # Données actuelles
        current_data = data_loader.get_current_metrics()
        
        # Prédictions OEE pour les 7 prochains jours
        predictions = oee_predictor.predict_next_days(days=7)
        
        # Recommandation de ligne
        recommendation = line_recommender.get_best_line()
        
        # Alertes critiques
        alerts = anomaly_expert.get_active_alerts()
        
        return jsonify({
            'success': True,
            'current': current_data,
            'predictions': predictions,
            'recommendation': recommendation,
            'alerts': alerts,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_oee():
    """Prédiction OEE pour une ligne spécifique"""
    try:
        data = request.json
        line_id = data.get('line_id', 'L1')
        horizon = data.get('horizon', 7)
        
        prediction = oee_predictor.predict_line(line_id, horizon)
        
        return jsonify({
            'success': True,
            'line_id': line_id,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommend')
def recommend_line():
    """Recommandation de la meilleure ligne pour production"""
    try:
        product_type = request.args.get('product_type', 'standard')
        quantity = int(request.args.get('quantity', 1000))
        
        recommendation = line_recommender.recommend(product_type, quantity)
        scenarios = line_recommender.simulate_scenarios(product_type, quantity)
        
        return jsonify({
            'success': True,
            'recommendation': recommendation,
            'scenarios': scenarios
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/anomalies')
def get_anomalies():
    """Récupération des anomalies et solutions"""
    try:
        period = request.args.get('period', '30')
        anomalies = anomaly_expert.get_recent_anomalies(int(period))
        
        return jsonify({
            'success': True,
            'anomalies': anomalies
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/anomaly/similar', methods=['POST'])
def find_similar_anomalies():
    """Recherche d'anomalies similaires et solutions"""
    try:
        data = request.json
        description = data.get('description', '')
        machine_id = data.get('machine_id', '')
        
        similar = anomaly_expert.find_similar(description, machine_id)
        
        return jsonify({
            'success': True,
            'similar_cases': similar
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/historical')
def get_historical_data():
    """Données historiques pour analyse"""
    try:
        line_id = request.args.get('line_id', 'all')
        days = int(request.args.get('days', 90))
        
        historical = data_loader.get_historical_data(line_id, days)
        
        return jsonify({
            'success': True,
            'data': historical
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/impact')
def calculate_impact():
    """Calcul de l'impact potentiel d'amélioration"""
    try:
        current_oee = data_loader.get_average_oee()
        improvement = float(request.args.get('improvement', 1.0))
        
        impact = {
            'current_oee': current_oee,
            'target_oee': current_oee + improvement,
            'improvement_percent': improvement,
            'estimated_gain': calculate_production_gain(current_oee, improvement)
        }
        
        return jsonify({
            'success': True,
            'impact': impact
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_production_gain(current_oee, improvement):
    """Calcul du gain de production estimé"""
    # Simulation basée sur une production annuelle estimée
    annual_hours = 8760  # heures par an
    utilization_rate = 0.85
    effective_hours = annual_hours * utilization_rate
    
    current_production = effective_hours * (current_oee / 100)
    improved_production = effective_hours * ((current_oee + improvement) / 100)
    
    gain_hours = improved_production - current_production
    gain_percent = (improvement / current_oee) * 100
    
    return {
        'gain_hours': round(gain_hours, 2),
        'gain_percent': round(gain_percent, 2),
        'annual_current': round(current_production, 2),
        'annual_improved': round(improved_production, 2)
    }

if __name__ == '__main__':
    import os
    
    print("=" * 60)
    print("Agent IA de Décision pour l'Amélioration de l'OEE - TECPAP")
    print("=" * 60)
    print("\nInitialisation des composants...")
    
    # Chargement des données
    data_loader.load_data()
    print("✓ Données chargées")
    
    # Entraînement des modèles
    oee_predictor.train()
    print("✓ Modèle de prédiction entraîné")
    
    line_recommender.initialize()
    print("✓ Système de recommandation initialisé")
    
    anomaly_expert.load_knowledge_base()
    print("✓ Base de connaissances des anomalies chargée")
    
    print("\nDémarrage du serveur Flask...")
    
    # Configuration pour déploiement (Render, Heroku, etc.)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') != 'production'
    
    if debug_mode:
        print("Accédez à l'application sur: http://localhost:5000")
    else:
        print(f"Application en production sur le port {port}")
    
    print("=" * 60)
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
