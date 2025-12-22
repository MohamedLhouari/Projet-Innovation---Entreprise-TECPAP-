"""
Système expert pour la gestion et l'analyse des anomalies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

class AnomalyExpert:
    def __init__(self):
        self.knowledge_base = None
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.symptom_vectors = None
        self.active_alerts = []
    
    def load_knowledge_base(self):
        """Charge la base de connaissances des anomalies"""
        from data.data_loader import DataLoader
        
        loader = DataLoader()
        loader.load_data()
        
        if loader.anomalies_data is not None:
            self.knowledge_base = loader.anomalies_data
            
            # Créer des vecteurs pour la recherche de similarité
            if len(self.knowledge_base) > 0:
                symptoms = self.knowledge_base['symptom'].fillna('') + ' ' + \
                          self.knowledge_base['root_cause'].fillna('')
                self.symptom_vectors = self.vectorizer.fit_transform(symptoms)
            
            # Générer des alertes actives
            self._generate_active_alerts(loader)
            
            return True
        
        return False
    
    def _generate_active_alerts(self, loader):
        """Génère des alertes basées sur les données récentes"""
        if loader.oee_data is None:
            return
        
        # Analyser les dernières 24h
        recent = loader.oee_data[
            loader.oee_data['timestamp'] >= 
            loader.oee_data['timestamp'].max() - timedelta(days=1)
        ]
        
        self.active_alerts = []
        
        for line in ['L1', 'L2', 'L3']:
            line_data = recent[recent['line_id'] == line]
            
            if len(line_data) == 0:
                continue
            
            current_oee = line_data['oee'].iloc[-1]
            avg_oee = line_data['oee'].mean()
            std_oee = line_data['oee'].std()
            
            # Détection d'anomalies
            
            # 1. Baisse soudaine de l'OEE
            if current_oee < avg_oee - 2 * std_oee and current_oee < 65:
                self.active_alerts.append({
                    'id': len(self.active_alerts) + 1,
                    'line_id': line,
                    'severity': 'Critical',
                    'type': 'Performance_Drop',
                    'message': f'Baisse critique de performance sur {line}',
                    'current_value': round(current_oee, 2),
                    'expected_value': round(avg_oee, 2),
                    'deviation': round(avg_oee - current_oee, 2),
                    'timestamp': datetime.now().isoformat(),
                    'recommended_action': 'Inspection immédiate requise'
                })
            
            # 2. OEE en dessous du seuil
            elif current_oee < 70:
                self.active_alerts.append({
                    'id': len(self.active_alerts) + 1,
                    'line_id': line,
                    'severity': 'High',
                    'type': 'Low_OEE',
                    'message': f'OEE en dessous du seuil sur {line}',
                    'current_value': round(current_oee, 2),
                    'threshold': 70,
                    'timestamp': datetime.now().isoformat(),
                    'recommended_action': 'Vérifier les causes de sous-performance'
                })
            
            # 3. Variabilité élevée
            if std_oee > 8:
                self.active_alerts.append({
                    'id': len(self.active_alerts) + 1,
                    'line_id': line,
                    'severity': 'Medium',
                    'type': 'High_Variability',
                    'message': f'Forte variabilité détectée sur {line}',
                    'std_deviation': round(std_oee, 2),
                    'timestamp': datetime.now().isoformat(),
                    'recommended_action': 'Analyser les causes de variabilité'
                })
            
            # 4. Disponibilité faible
            if len(line_data) > 0 and line_data['availability'].iloc[-1] < 80:
                self.active_alerts.append({
                    'id': len(self.active_alerts) + 1,
                    'line_id': line,
                    'severity': 'High',
                    'type': 'Low_Availability',
                    'message': f'Disponibilité insuffisante sur {line}',
                    'current_value': round(line_data['availability'].iloc[-1], 2),
                    'timestamp': datetime.now().isoformat(),
                    'recommended_action': 'Vérifier les arrêts non planifiés'
                })
            
            # 5. Problème de qualité
            if len(line_data) > 0 and line_data['quality'].iloc[-1] < 93:
                self.active_alerts.append({
                    'id': len(self.active_alerts) + 1,
                    'line_id': line,
                    'severity': 'Medium',
                    'type': 'Quality_Issue',
                    'message': f'Taux de qualité en baisse sur {line}',
                    'current_value': round(line_data['quality'].iloc[-1], 2),
                    'timestamp': datetime.now().isoformat(),
                    'recommended_action': 'Contrôle qualité renforcé requis'
                })
    
    def get_active_alerts(self):
        """Retourne les alertes actives"""
        return self.active_alerts
    
    def get_recent_anomalies(self, days=30):
        """Récupère les anomalies récentes"""
        if self.knowledge_base is None:
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        recent = self.knowledge_base[
            pd.to_datetime(self.knowledge_base['timestamp']) >= cutoff
        ]
        
        anomalies = []
        for _, row in recent.iterrows():
            anomalies.append({
                'id': int(row['anomaly_id']),
                'date': row['timestamp'],
                'line': row['line_id'],
                'machine': row['machine_id'],
                'symptom': row['symptom'],
                'cause': row['root_cause'],
                'solution': row['solution_applied'],
                'resolution_time': int(row['resolution_time_minutes']),
                'impact': float(row['impact_oee']),
                'priority': row['priority'],
                'status': row['status']
            })
        
        return sorted(anomalies, key=lambda x: x['date'], reverse=True)
    
    def find_similar(self, description, machine_id=''):
        """Trouve des anomalies similaires dans l'historique"""
        if self.knowledge_base is None or self.symptom_vectors is None:
            return []
        
        # Vectoriser la description
        query_vector = self.vectorizer.transform([description + ' ' + machine_id])
        
        # Calculer les similarités
        similarities = cosine_similarity(query_vector, self.symptom_vectors)[0]
        
        # Trouver les top 5 cas similaires
        top_indices = np.argsort(similarities)[-5:][::-1]
        
        similar_cases = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Seuil de similarité
                row = self.knowledge_base.iloc[idx]
                similar_cases.append({
                    'similarity': round(float(similarities[idx]) * 100, 1),
                    'anomaly_id': int(row['anomaly_id']),
                    'line': row['line_id'],
                    'machine': row['machine_id'],
                    'symptom': row['symptom'],
                    'root_cause': row['root_cause'],
                    'solution': row['solution_applied'],
                    'resolution_time': int(row['resolution_time_minutes']),
                    'impact': float(row['impact_oee']),
                    'recurrence': int(row['recurrence_count']),
                    'effectiveness': 'High' if row['recurrence_count'] < 2 else 'Medium'
                })
        
        return similar_cases
    
    def suggest_solution(self, symptom, line_id='', machine_id=''):
        """Suggère une solution basée sur l'historique"""
        similar = self.find_similar(symptom, machine_id)
        
        if not similar:
            return {
                'confidence': 'Low',
                'message': 'Aucun cas similaire trouvé dans l\'historique',
                'recommendation': 'Effectuer un diagnostic complet et documenter la solution'
            }
        
        # Analyser les solutions des cas similaires
        top_match = similar[0]
        
        # Vérifier si plusieurs cas similaires ont la même solution
        common_solutions = {}
        for case in similar:
            sol = case['solution']
            if sol not in common_solutions:
                common_solutions[sol] = {'count': 0, 'avg_time': 0, 'cases': []}
            common_solutions[sol]['count'] += 1
            common_solutions[sol]['avg_time'] += case['resolution_time']
            common_solutions[sol]['cases'].append(case)
        
        # Trouver la solution la plus fréquente
        best_solution = max(common_solutions.items(), key=lambda x: x[1]['count'])
        solution_text = best_solution[0]
        solution_data = best_solution[1]
        
        avg_resolution_time = solution_data['avg_time'] / solution_data['count']
        
        confidence = 'High' if solution_data['count'] >= 3 else 'Medium'
        
        return {
            'confidence': confidence,
            'recommended_solution': solution_text,
            'estimated_time': round(avg_resolution_time, 0),
            'success_rate': round((solution_data['count'] / len(similar)) * 100, 1),
            'similar_cases_count': len(similar),
            'top_match': {
                'similarity': top_match['similarity'],
                'symptom': top_match['symptom'],
                'cause': top_match['root_cause']
            },
            'detailed_steps': self._get_solution_steps(solution_text),
            'expected_impact': abs(np.mean([c['impact'] for c in solution_data['cases']]))
        }
    
    def _get_solution_steps(self, solution):
        """Génère des étapes détaillées pour une solution"""
        # Base de connaissances des étapes détaillées
        steps_database = {
            'Remplacement des courroies et réalignement': [
                '1. Arrêter la machine et consigner',
                '2. Retirer les protections d\'accès aux courroies',
                '3. Vérifier l\'usure et remplacer les courroies défectueuses',
                '4. Vérifier l\'alignement des poulies',
                '5. Réajuster la tension des courroies selon spécifications',
                '6. Tester en marche à vide',
                '7. Vérifier les vibrations et le bruit'
            ],
            'Remplacement du capteur et recalibration': [
                '1. Identifier le capteur défectueux',
                '2. Couper l\'alimentation électrique',
                '3. Déconnecter et retirer le capteur',
                '4. Installer le nouveau capteur',
                '5. Reconnecter et vérifier le câblage',
                '6. Recalibrer selon la procédure constructeur',
                '7. Tester le fonctionnement'
            ],
            'Recalibration du système de contrôle thermique': [
                '1. Vérifier les consignes de température',
                '2. Nettoyer les sondes de température',
                '3. Recalibrer les sondes si nécessaire',
                '4. Vérifier le système de régulation',
                '5. Ajuster les paramètres PID',
                '6. Effectuer un cycle de test',
                '7. Valider la stabilité thermique'
            ],
            'Ajustement de la tension et nettoyage des rouleaux': [
                '1. Arrêter la ligne',
                '2. Nettoyer tous les rouleaux d\'alimentation',
                '3. Vérifier l\'état des rouleaux',
                '4. Ajuster la tension d\'alimentation progressivement',
                '5. Tester avec différentes vitesses',
                '6. Valider l\'absence de bourrage',
                '7. Documenter les nouveaux réglages'
            ],
            'Remplacement des roulements et équilibrage': [
                '1. Diagnostiquer les roulements défectueux',
                '2. Commander les pièces de rechange',
                '3. Démonter l\'ensemble concerné',
                '4. Remplacer les roulements',
                '5. Procéder à l\'équilibrage dynamique',
                '6. Remonter et aligner',
                '7. Effectuer des mesures vibratoires de validation'
            ]
        }
        
        # Rechercher les étapes correspondantes
        for key in steps_database:
            if key.lower() in solution.lower():
                return steps_database[key]
        
        # Étapes génériques si non trouvé
        return [
            '1. Diagnostiquer précisément le problème',
            '2. Consigner la machine',
            '3. Appliquer la solution identifiée',
            '4. Vérifier le résultat',
            '5. Remettre en service',
            '6. Documenter l\'intervention'
        ]
    
    def analyze_trend(self, line_id='', days=90):
        """Analyse les tendances d'anomalies"""
        if self.knowledge_base is None:
            return {}
        
        cutoff = datetime.now() - timedelta(days=days)
        data = self.knowledge_base[
            pd.to_datetime(self.knowledge_base['timestamp']) >= cutoff
        ]
        
        if line_id:
            data = data[data['line_id'] == line_id]
        
        # Analyse par type
        by_symptom = data.groupby('symptom').agg({
            'anomaly_id': 'count',
            'resolution_time_minutes': 'mean',
            'impact_oee': 'mean'
        }).reset_index()
        by_symptom.columns = ['symptom', 'count', 'avg_resolution_time', 'avg_impact']
        by_symptom = by_symptom.sort_values('count', ascending=False)
        
        # Machine la plus problématique
        by_machine = data.groupby('machine_id')['anomaly_id'].count().sort_values(ascending=False)
        
        # Tendance temporelle
        data['month'] = pd.to_datetime(data['timestamp']).dt.to_period('M')
        by_month = data.groupby('month')['anomaly_id'].count()
        
        return {
            'total_anomalies': len(data),
            'avg_resolution_time': round(data['resolution_time_minutes'].mean(), 1),
            'total_impact_oee': round(data['impact_oee'].sum(), 2),
            'most_common': by_symptom.head(3).to_dict('records'),
            'most_problematic_machine': by_machine.index[0] if len(by_machine) > 0 else 'N/A',
            'trend': 'Increasing' if by_month.iloc[-1] > by_month.mean() else 'Stable'
        }
