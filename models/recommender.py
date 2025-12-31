"""
Système de recommandation de ligne optimale pour la production
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

class LineRecommender:
    def __init__(self):
        self.lines = ['L1', 'L2', 'L3']
        self.line_characteristics = {
            'L1': {
                'speed': 1200,  # pièces/heure
                'quality_rate': 0.97,
                'flexibility': 0.85,
                'maintenance_level': 'Good',
                'operators_required': 3
            },
            'L2': {
                'speed': 1400,
                'quality_rate': 0.94,
                'flexibility': 0.90,
                'maintenance_level': 'Medium',
                'operators_required': 4
            },
            'L3': {
                'speed': 1000,
                'quality_rate': 0.92,
                'flexibility': 0.75,
                'maintenance_level': 'Medium',
                'operators_required': 2
            }
        }
        self.predictor = None
    
    def initialize(self):
        """Initialise le système de recommandation"""
        from models.predictor import OEEPredictor
        self.predictor = OEEPredictor()
        
        # Charger le modèle s'il existe
        if not self.predictor.trained:
            self.predictor._load_model()
    
    def get_best_line(self):
        """Recommande la meilleure ligne globale"""
        from data.data_loader import DataLoader
        
        loader = DataLoader()
        loader.load_data()
        
        # Récupérer les performances récentes
        recent_data = loader.oee_data[
            loader.oee_data['timestamp'] >= 
            loader.oee_data['timestamp'].max() - timedelta(days=7)
        ]
        
        # Calculer les scores par ligne
        scores = {}
        for line in self.lines:
            line_data = recent_data[recent_data['line_id'] == line]
            
            if len(line_data) > 0:
                # Score basé sur plusieurs critères
                oee_score = line_data['oee'].mean()
                availability_score = line_data['availability'].mean()
                quality_score = line_data['quality'].mean()
                performance_score = line_data['performance'].mean()
                
                # Variabilité (moins c'est mieux)
                stability_score = 100 - line_data['oee'].std() * 2
                
                # Score global pondéré
                total_score = (
                    oee_score * 0.4 +
                    availability_score * 0.2 +
                    quality_score * 0.2 +
                    performance_score * 0.1 +
                    stability_score * 0.1
                )
                
                scores[line] = {
                    'total_score': round(total_score, 2),
                    'oee': round(oee_score, 2),
                    'availability': round(availability_score, 2),
                    'quality': round(quality_score, 2),
                    'performance': round(performance_score, 2),
                    'stability': round(stability_score, 2)
                }
        
        # Trouver la meilleure ligne
        best_line = max(scores.items(), key=lambda x: x[1]['total_score'])
        
        return {
            'recommended_line': best_line[0],
            'score': best_line[1]['total_score'],
            'details': best_line[1],
            'all_scores': scores,
            'confidence': 'High' if best_line[1]['total_score'] > 75 else 'Medium',
            'reason': self._generate_reason(best_line[0], best_line[1])
        }
    
    def recommend(self, product_type='standard', quantity=1000):
        """Recommande la meilleure ligne pour un produit spécifique"""
        from data.data_loader import DataLoader
        
        loader = DataLoader()
        loader.load_data()
        
        # Obtenir les prédictions OEE
        if self.predictor and self.predictor.trained:
            predictions = self.predictor.predict_next_days(days=1)
        else:
            predictions = None
        
        # Calculer le score pour chaque ligne
        recommendations = []
        
        for line in self.lines:
            chars = self.line_characteristics[line]
            
            # OEE prédit ou récent
            if predictions and line in predictions:
                predicted_oee = predictions[line][0]['oee_predicted']
            else:
                recent = loader.oee_data[loader.oee_data['line_id'] == line].tail(24)
                predicted_oee = recent['oee'].mean() if len(recent) > 0 else 70
            
            # Calcul du temps de production estimé
            production_time = quantity / chars['speed']
            
            # Facteurs de production
            good_pieces_rate = chars['quality_rate'] * (predicted_oee / 100)
            estimated_good_pieces = int(quantity / good_pieces_rate)
            
            # Score de recommandation
            speed_score = chars['speed'] / 1400 * 100  # Normalisé par rapport à la vitesse max
            quality_score = chars['quality_rate'] * 100
            oee_score = predicted_oee
            flexibility_score = chars['flexibility'] * 100
            
            total_score = (
                oee_score * 0.35 +
                quality_score * 0.25 +
                speed_score * 0.25 +
                flexibility_score * 0.15
            )
            
            recommendations.append({
                'line_id': line,
                'score': round(total_score, 2),
                'predicted_oee': round(predicted_oee, 2),
                'production_time_hours': round(production_time, 2),
                'estimated_pieces': estimated_good_pieces,
                'quality_rate': round(chars['quality_rate'] * 100, 1),
                'speed': chars['speed'],
                'operators_needed': chars['operators_required'],
                'maintenance_status': chars['maintenance_level']
            })
        
        # Trier par score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        best = recommendations[0]
        
        return {
            'recommended_line': best['line_id'],
            'score': best['score'],
            'details': best,
            'alternatives': recommendations[1:],
            'estimated_completion': datetime.now() + timedelta(hours=best['production_time_hours']),
            'confidence': 'High' if best['score'] > 80 else 'Medium'
        }
    
    def simulate_scenarios(self, product_type='standard', quantity=1000):
        """Simule différents scénarios de production"""
        scenarios = []
        
        # Obtenir les recommandations pour toutes les lignes
        all_recommendations = self.recommend(product_type, quantity)
        all_lines_data = [all_recommendations['details']] + all_recommendations['alternatives']
        
        for line in self.lines:
            # Trouver les détails pour cette ligne spécifique
            line_details = next(
                (s for s in all_lines_data if s['line_id'] == line), 
                None
            )
            
            if line_details:
                # Risques
                risk_level = 'Low'
                if line_details['predicted_oee'] < 70:
                    risk_level = 'High'
                elif line_details['predicted_oee'] < 75:
                    risk_level = 'Medium'
                
                scenarios.append({
                    'line_id': line,
                    'oee_predicted': round(line_details['predicted_oee'], 2),
                    'production_time': round(line_details['production_time_hours'], 2),
                    'risk_level': risk_level,
                    'quality_expected': round(line_details['quality_rate'], 2),
                    'recommendation_rank': len(scenarios) + 1
                })
        
        # Comparaison
        fastest_scenario = min(scenarios, key=lambda x: x['production_time'])
        safest_scenario = max(scenarios, key=lambda x: x['oee_predicted'])
        best_quality_scenario = max(scenarios, key=lambda x: x['quality_expected'])
        
        return {
            'scenarios': scenarios,
            'comparison': {
                'fastest': fastest_scenario['line_id'],
                'most_reliable': safest_scenario['line_id'],
                'best_quality': best_quality_scenario['line_id'],
                'time_difference': round(
                    max(s['production_time'] for s in scenarios) - 
                    min(s['production_time'] for s in scenarios), 
                    2
                )
            }
        }
    
    def _generate_reason(self, line, scores):
        """Génère une explication de la recommandation"""
        reasons = []
        
        if scores['oee'] > 75:
            reasons.append(f"OEE excellent ({scores['oee']}%)")
        
        if scores['quality'] > 95:
            reasons.append(f"Qualité supérieure ({scores['quality']}%)")
        
        if scores['stability'] > 90:
            reasons.append("Performance très stable")
        
        if scores['availability'] > 85:
            reasons.append(f"Disponibilité élevée ({scores['availability']}%)")
        
        if not reasons:
            reasons.append("Meilleur équilibre performance/fiabilité")
        
        return " - ".join(reasons)
