"""
Agent IA de Décision pour l'Amélioration de l'OEE - TECPAP
Application principale Flask
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from datetime import datetime, timedelta
import os
import pandas as pd
from models.predictor import OEEPredictor
from models.recommender import LineRecommender
from models.anomaly_expert import AnomalyExpert
from models.speed_optimizer import SpeedOptimizer
from data.data_loader import DataLoader
from data.products_catalog import get_all_products, get_product_by_code
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tecpap-innovation-oee-2025'

# Initialisation des composants IA
data_loader = DataLoader()
oee_predictor = OEEPredictor()
line_recommender = LineRecommender()
anomaly_expert = AnomalyExpert()
speed_optimizer = SpeedOptimizer()

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
        
        # 2. Chargement/Entraînement du modèle de prédiction
        print("\n[2/4] Chargement du modèle de prédiction OEE...")
        if oee_predictor._load_model():
            print("✓ Modèle chargé depuis fichier")
        else:
            print("Entraînement du modèle...")
            oee_predictor.train()
            print("✓ Modèle entraîné")
        
        # 3. Initialisation du système de recommandation
        print("\n[3/4] Initialisation du système de recommandation...")
        line_recommender.initialize()
        print("✓ Recommandation initialisée")
        
        # 4. Chargement de la base de connaissances
        print("\n[4/5] Chargement de la base de connaissances...")
        anomaly_expert.load_knowledge_base()
        print("✓ Expert en anomalies prêt")
        
        # 5. Entraînement de l'optimiseur de vitesse
        print("\n[5/5] Entraînement de l'optimiseur de vitesse...")
        training_data = data_loader.get_data_for_training()
        speed_optimizer.train(training_data)
        print("✓ Optimiseur de vitesse prêt")
        
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
def home():
    """Page d'accueil - Sélection Dashboard ou Admin"""
    return render_template('home.html')

@app.route('/dashboard')
def index():
    """Dashboard principal"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Page d'administration"""
    return render_template('admin.html')

@app.route('/images/produits/<path:filename>')
def serve_product_image(filename):
    """Servir les images des produits depuis le dossier images/produits"""
    images_path = os.path.join(os.path.dirname(__file__), 'images', 'produits')
    return send_from_directory(images_path, filename)

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
        scenarios_data = line_recommender.simulate_scenarios(product_type, quantity)
        
        # scenarios_data contient déjà 'scenarios' et 'comparison'
        return jsonify({
            'success': True,
            'recommendation': recommendation,
            'scenarios': scenarios_data['scenarios'],
            'comparison': scenarios_data['comparison']
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

@app.route('/api/speed/optimize', methods=['POST'])
def optimize_speed():
    """Optimisation de la vitesse machine (Sweet Spot)"""
    try:
        data = request.json
        line_id = data.get('line_id', 'L1')
        product_type = data.get('product_type', 'Fond_Plat')
        
        # Trouver la vitesse optimale
        result = speed_optimizer.find_optimal_speed(line_id, product_type)
        
        return jsonify({
            'success': True,
            'optimization': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/speed/compare')
def compare_speeds():
    """Comparaison des vitesses optimales pour toutes les lignes"""
    try:
        product_type = request.args.get('product_type', 'Fond_Plat')
        
        # Obtenir recommandations pour toutes les lignes
        comparison = speed_optimizer.get_speed_recommendations_all_lines(product_type)
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/speed/predict', methods=['POST'])
def predict_at_speed():
    """Prédiction de production et qualité pour une vitesse donnée"""
    try:
        data = request.json
        line_id = data.get('line_id', 'L1')
        product_type = data.get('product_type', 'Fond_Plat')
        speed = int(data.get('speed', 1000))
        
        # Prédire à cette vitesse
        prediction = speed_optimizer.predict_at_speed(line_id, product_type, speed)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/speed/ranges')
def get_speed_ranges():
    """Récupérer les plages de vitesse disponibles par ligne"""
    try:
        return jsonify({
            'success': True,
            'ranges': speed_optimizer.speed_ranges,
            'products': list(speed_optimizer.product_characteristics.keys())
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ROUTES ADMINISTRATION - ANOMALIES & PRODUITS
# ============================================

@app.route('/admin')
def admin_panel():
    """Page d'administration"""
    return render_template('admin.html')

@app.route('/api/admin/anomalies', methods=['GET'])
def get_all_anomalies():
    """Récupérer toutes les anomalies"""
    try:
        anomalies = data_loader.anomalies_data.to_dict('records')
        return jsonify({
            'success': True,
            'anomalies': anomalies
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/anomalies', methods=['POST'])
def add_anomaly():
    """Ajouter une nouvelle anomalie"""
    try:
        data = request.json
        
        # Générer nouvel ID
        new_id = data_loader.anomalies_data['anomaly_id'].max() + 1 if len(data_loader.anomalies_data) > 0 else 1
        
        # Créer nouvelle anomalie
        new_anomaly = {
            'anomaly_id': new_id,
            'timestamp': datetime.now().isoformat(),
            'line_id': data.get('line_id', 'L1'),
            'machine_id': data.get('machine_id', 'M1-1'),
            'symptom': data.get('symptom', ''),
            'root_cause': data.get('root_cause', ''),
            'solution_applied': data.get('solution_applied', ''),
            'resolution_time_minutes': int(data.get('resolution_time_minutes', 60)),
            'impact_oee': int(data.get('impact_oee', -5)),
            'recurrence_count': int(data.get('recurrence_count', 1)),
            'priority': data.get('priority', 'Medium'),
            'status': data.get('status', 'Resolved')
        }
        
        # Ajouter au DataFrame
        data_loader.anomalies_data = pd.concat([
            data_loader.anomalies_data,
            pd.DataFrame([new_anomaly])
        ], ignore_index=True)
        
        # Sauvegarder
        data_loader.anomalies_data.to_csv(
            os.path.join(data_loader.data_path, 'anomalies_data.csv'),
            index=False
        )
        
        # Recharger base de connaissances
        anomaly_expert.load_knowledge_base()
        
        return jsonify({
            'success': True,
            'anomaly': new_anomaly
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/anomalies/<int:anomaly_id>', methods=['PUT'])
def update_anomaly(anomaly_id):
    """Modifier une anomalie existante"""
    try:
        data = request.json
        
        # Trouver l'anomalie
        idx = data_loader.anomalies_data[data_loader.anomalies_data['anomaly_id'] == anomaly_id].index
        
        if len(idx) == 0:
            return jsonify({'success': False, 'error': 'Anomalie non trouvée'}), 404
        
        # Mettre à jour
        for key, value in data.items():
            if key in data_loader.anomalies_data.columns and key != 'anomaly_id':
                data_loader.anomalies_data.at[idx[0], key] = value
        
        # Sauvegarder
        data_loader.anomalies_data.to_csv(
            os.path.join(data_loader.data_path, 'anomalies_data.csv'),
            index=False
        )
        
        # Recharger base de connaissances
        anomaly_expert.load_knowledge_base()
        
        return jsonify({
            'success': True,
            'message': 'Anomalie mise à jour'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/anomalies/<int:anomaly_id>', methods=['DELETE'])
def delete_anomaly(anomaly_id):
    """Supprimer une anomalie"""
    try:
        # Supprimer l'anomalie
        data_loader.anomalies_data = data_loader.anomalies_data[
            data_loader.anomalies_data['anomaly_id'] != anomaly_id
        ]
        
        # Sauvegarder
        data_loader.anomalies_data.to_csv(
            os.path.join(data_loader.data_path, 'anomalies_data.csv'),
            index=False
        )
        
        # Recharger base de connaissances
        anomaly_expert.load_knowledge_base()
        
        return jsonify({
            'success': True,
            'message': 'Anomalie supprimée'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/products', methods=['GET'])
def get_products():
    """Récupère la liste des produits TECPAP"""
    try:
        products = get_all_products()
        
        # Formater pour l'API
        products_formatted = []
        for product in products:
            products_formatted.append({
                'id': product['product_id'],
                'name': product['name'],
                'code': product['code'],
                'category': product['category'],
                'description': product['description'],
                'image': product['image'],
                'dimensions': f"{product['dimensions']['width_cm']}x{product['dimensions']['height_cm']}x{product['dimensions']['depth_cm']} cm",
                'optimal_speed': product['optimal_speed']
            })
        
        return jsonify({
            'success': True,
            'products': products_formatted
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
    
    # Configuration pour déploiement (Render, Heroku, etc.)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') != 'production'
    
    if debug_mode:
        print("\nDémarrage du serveur Flask...")
        print("Accédez à l'application sur: http://localhost:5000")
    else:
        print(f"Application en production sur le port {port}")
    
    print("=" * 60)
    print("=" * 60)
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
