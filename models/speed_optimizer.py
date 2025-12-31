"""
Optimiseur de vitesse machine (Sweet Spot Finder)
Trouve la vitesse optimale pour maximiser la production nette (production × qualité)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

class SpeedOptimizer:
    def __init__(self):
        self.model_production = None  # Prédit production_rate = f(speed, line, product)
        self.model_quality = None     # Prédit quality_rate = f(speed, line, product)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Vitesses par ligne (pièces/heure)
        self.speed_ranges = {
            'L1': {'min': 700, 'max': 1300, 'optimal_estimate': 1000},
            'L2': {'min': 800, 'max': 1400, 'optimal_estimate': 1100},
            'L3': {'min': 600, 'max': 1200, 'optimal_estimate': 900}
        }
        
        # Caractéristiques produits TECPAP
        self.product_characteristics = {
            'Fond_Plat': {'complexity': 0.7, 'speed_factor': 1.15},
            'Fond_Carre_Sans_Poignees': {'complexity': 0.8, 'speed_factor': 1.10},
            'Fond_Carre_Poignees_Plates': {'complexity': 0.9, 'speed_factor': 0.95},
            'Fond_Carre_Poignees_Torsadees': {'complexity': 1.0, 'speed_factor': 0.85}
        }
    
    def prepare_features(self, df):
        """Prépare les features pour l'entraînement"""
        features = df.copy()
        
        # Encoding des variables catégorielles
        # Line
        features['line_L1'] = (features['line_id'] == 'L1').astype(int)
        features['line_L2'] = (features['line_id'] == 'L2').astype(int)
        features['line_L3'] = (features['line_id'] == 'L3').astype(int)
        
        # Product type
        for product in self.product_characteristics.keys():
            col_name = f'product_{product}'
            features[col_name] = (features['product_type'] == product).astype(int)
        
        # Feature engineering: vitesse relative
        # Ratio vitesse actuelle / vitesse optimale estimée
        def get_speed_ratio(row):
            optimal = self.speed_ranges[row['line_id']]['optimal_estimate']
            return row['machine_speed'] / optimal
        
        features['speed_ratio'] = features.apply(get_speed_ratio, axis=1)
        
        # Sélection des features numériques
        numeric_features = [
            'machine_speed', 'speed_ratio',
            'line_L1', 'line_L2', 'line_L3',
            'product_Fond_Plat', 'product_Fond_Carre_Sans_Poignees',
            'product_Fond_Carre_Poignees_Plates', 'product_Fond_Carre_Poignees_Torsadees'
        ]
        
        return features[numeric_features]
    
    def train(self, data):
        """
        Entraîne les modèles de prédiction
        Args:
            data: DataFrame avec colonnes [machine_speed, line_id, product_type, 
                  performance, quality, total_pieces, good_pieces]
        """
        print("Entraînement de l'optimiseur de vitesse...")
        
        # Calculer les variables target
        # 1. Production rate (pièces/heure) - basé sur total_pieces
        data['production_rate'] = data['total_pieces']  # Déjà des pièces/heure
        
        # 2. Quality rate (%) - ratio pièces bonnes / total
        data['quality_rate'] = (data['good_pieces'] / data['total_pieces']) * 100
        data['quality_rate'] = data['quality_rate'].fillna(0)
        
        # Préparer les features
        X = self.prepare_features(data)
        
        # Target 1: Production rate
        y_production = data['production_rate']
        
        # Target 2: Quality rate
        y_quality = data['quality_rate']
        
        # Split train/test
        X_train, X_test, y_prod_train, y_prod_test = train_test_split(
            X, y_production, test_size=0.2, random_state=42
        )
        _, _, y_qual_train, y_qual_test = train_test_split(
            X, y_quality, test_size=0.2, random_state=42
        )
        
        # Normalisation
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Modèle 1: Prédiction de la production
        print("  → Entraînement modèle production...")
        self.model_production = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.model_production.fit(X_train_scaled, y_prod_train)
        
        prod_score = self.model_production.score(X_test_scaled, y_prod_test)
        print(f"  ✓ Score production: {prod_score:.3f}")
        
        # Modèle 2: Prédiction de la qualité
        print("  → Entraînement modèle qualité...")
        self.model_quality = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.model_quality.fit(X_train_scaled, y_qual_train)
        
        qual_score = self.model_quality.score(X_test_scaled, y_qual_test)
        print(f"  ✓ Score qualité: {qual_score:.3f}")
        
        self.is_trained = True
        print("Optimiseur de vitesse entraîné avec succès!\n")
        
        return {
            'production_score': prod_score,
            'quality_score': qual_score
        }
    
    def predict_at_speed(self, line_id, product_type, speed):
        """Prédit production et qualité pour une vitesse donnée"""
        if not self.is_trained:
            raise Exception("Modèle non entraîné. Appelez train() d'abord.")
        
        # Créer un dataframe pour la prédiction
        test_data = pd.DataFrame([{
            'line_id': line_id,
            'product_type': product_type,
            'machine_speed': speed
        }])
        
        # Préparer les features
        X = self.prepare_features(test_data)
        X_scaled = self.scaler.transform(X)
        
        # Prédictions
        production = self.model_production.predict(X_scaled)[0]
        quality = self.model_quality.predict(X_scaled)[0]
        
        # Output net (pièces bonnes par heure)
        net_output = production * (quality / 100)
        
        # Taux de défauts
        defect_rate = 100 - quality
        
        return {
            'speed': int(speed),
            'production_rate': round(production, 1),
            'quality_rate': round(quality, 2),
            'defect_rate': round(defect_rate, 2),
            'net_output': round(net_output, 1)
        }
    
    def find_optimal_speed(self, line_id, product_type, step=25):
        """
        Trouve la vitesse optimale (Sweet Spot)
        Args:
            line_id: 'L1', 'L2', ou 'L3'
            product_type: Type de sac
            step: Pas de recherche (défaut: 25 pcs/h)
        Returns:
            dict avec optimal_speed, max_net_output, et courbe complète
        """
        if not self.is_trained:
            raise Exception("Modèle non entraîné. Appelez train() d'abord.")
        
        # Plage de vitesses à tester
        min_speed = self.speed_ranges[line_id]['min']
        max_speed = self.speed_ranges[line_id]['max']
        speeds = np.arange(min_speed, max_speed + step, step)
        
        results = []
        best_net_output = 0
        optimal_speed = None
        
        # Tester chaque vitesse
        for speed in speeds:
            prediction = self.predict_at_speed(line_id, product_type, speed)
            results.append(prediction)
            
            if prediction['net_output'] > best_net_output:
                best_net_output = prediction['net_output']
                optimal_speed = prediction['speed']
        
        # Calcul du gain potentiel
        # Vitesse actuelle moyenne (estimation)
        current_speed = self.speed_ranges[line_id]['optimal_estimate']
        current_prediction = self.predict_at_speed(line_id, product_type, current_speed)
        
        improvement_pct = ((best_net_output - current_prediction['net_output']) / 
                          current_prediction['net_output']) * 100
        
        # Analyse de la recommandation
        if optimal_speed > current_speed * 1.1:
            recommendation = f"Augmenter la vitesse à {optimal_speed} pcs/h"
            action = "increase"
        elif optimal_speed < current_speed * 0.9:
            recommendation = f"Réduire la vitesse à {optimal_speed} pcs/h"
            action = "decrease"
        else:
            recommendation = f"Maintenir la vitesse actuelle (~{current_speed} pcs/h)"
            action = "maintain"
        
        # Niveau de confiance
        if abs(improvement_pct) > 5:
            confidence = "High"
        elif abs(improvement_pct) > 2:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return {
            'optimal_speed': optimal_speed,
            'max_net_output': round(best_net_output, 1),
            'current_speed': current_speed,
            'current_net_output': round(current_prediction['net_output'], 1),
            'improvement_pct': round(improvement_pct, 2),
            'recommendation': recommendation,
            'action': action,
            'confidence': confidence,
            'curve_data': results,
            'line_id': line_id,
            'product_type': product_type
        }
    
    def save_model(self, filepath='models/saved_models/speed_optimizer.pkl'):
        """Sauvegarde le modèle entraîné"""
        if not self.is_trained:
            raise Exception("Modèle non entraîné. Rien à sauvegarder.")
        
        model_data = {
            'model_production': self.model_production,
            'model_quality': self.model_quality,
            'scaler': self.scaler,
            'speed_ranges': self.speed_ranges,
            'product_characteristics': self.product_characteristics
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model_data, filepath)
        print(f"✓ Modèle sauvegardé: {filepath}")
    
    def load_model(self, filepath='models/saved_models/speed_optimizer.pkl'):
        """Charge un modèle sauvegardé"""
        if not os.path.exists(filepath):
            return False
        
        model_data = joblib.load(filepath)
        self.model_production = model_data['model_production']
        self.model_quality = model_data['model_quality']
        self.scaler = model_data['scaler']
        self.speed_ranges = model_data['speed_ranges']
        self.product_characteristics = model_data['product_characteristics']
        self.is_trained = True
        
        print(f"✓ Modèle chargé: {filepath}")
        return True
    
    def get_speed_recommendations_all_lines(self, product_type):
        """Recommandations pour toutes les lignes (comparaison)"""
        recommendations = {}
        
        for line_id in ['L1', 'L2', 'L3']:
            try:
                result = self.find_optimal_speed(line_id, product_type)
                recommendations[line_id] = result
            except Exception as e:
                recommendations[line_id] = {'error': str(e)}
        
        # Identifier la meilleure ligne
        best_line = None
        best_output = 0
        
        for line_id, result in recommendations.items():
            if 'max_net_output' in result and result['max_net_output'] > best_output:
                best_output = result['max_net_output']
                best_line = line_id
        
        return {
            'recommendations': recommendations,
            'best_line': best_line,
            'product_type': product_type
        }
