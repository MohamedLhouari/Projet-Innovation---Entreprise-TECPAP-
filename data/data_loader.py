"""
Gestionnaire de chargement et gestion des données Evocon simulées
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

class DataLoader:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), 'generated')
        self.oee_data = None
        self.stops_data = None
        self.quality_data = None
        self.anomalies_data = None
        
    def load_data(self):
        """Charge toutes les données"""
        try:
            # Vérifier si les données existent, sinon les générer
            if not os.path.exists(self.data_path):
                os.makedirs(self.data_path)
                self._generate_data()
            
            # Charger les données
            self.oee_data = pd.read_csv(os.path.join(self.data_path, 'oee_data.csv'))
            self.stops_data = pd.read_csv(os.path.join(self.data_path, 'stops_data.csv'))
            self.quality_data = pd.read_csv(os.path.join(self.data_path, 'quality_data.csv'))
            self.anomalies_data = pd.read_csv(os.path.join(self.data_path, 'anomalies_data.csv'))
            
            # Conversion des dates
            self.oee_data['timestamp'] = pd.to_datetime(self.oee_data['timestamp'])
            self.stops_data['start_time'] = pd.to_datetime(self.stops_data['start_time'])
            self.stops_data['end_time'] = pd.to_datetime(self.stops_data['end_time'])
            self.quality_data['timestamp'] = pd.to_datetime(self.quality_data['timestamp'])
            self.anomalies_data['timestamp'] = pd.to_datetime(self.anomalies_data['timestamp'])
            
            return True
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            return False
    
    def _generate_data(self):
        """Génère des données synthétiques volumineuses et réalistes"""
        print("Génération des données synthétiques Evocon...")
        
        # Paramètres
        start_date = datetime.now() - timedelta(days=730)  # 2 ans de données
        lines = ['L1', 'L2', 'L3']
        machines_per_line = {'L1': ['M1-1', 'M1-2', 'M1-3'], 
                            'L2': ['M2-1', 'M2-2', 'M2-3', 'M2-4'],
                            'L3': ['M3-1', 'M3-2']}
        
        # Types de produits TECPAP (sacs papier Kraft)
        product_types = [
            'Fond_Plat',
            'Fond_Carre_Sans_Poignees',
            'Fond_Carre_Poignees_Plates',
            'Fond_Carre_Poignees_Torsadees'
        ]
        
        # Vitesses optimales par ligne (pièces/heure)
        optimal_speeds = {'L1': 1000, 'L2': 1100, 'L3': 900}
        speed_ranges = {'L1': (700, 1300), 'L2': (800, 1400), 'L3': (600, 1200)}
        
        # 1. Génération des données OEE (par heure)
        oee_records = []
        for day in range(730):
            date = start_date + timedelta(days=day)
            for hour in range(24):
                timestamp = date + timedelta(hours=hour)
                
                # Ignorer les heures de non-production (week-end, nuits)
                if date.weekday() >= 5 or hour < 6 or hour > 22:
                    continue
                
                for line in lines:
                    # OEE de base par ligne (L1 meilleure que L3)
                    base_oee = {'L1': 78, 'L2': 73, 'L3': 69}[line]
                    
                    # Sélection aléatoire du type de produit
                    product_type = np.random.choice(product_types)
                    
                    # Génération de la vitesse machine (avec distribution réaliste)
                    min_speed, max_speed = speed_ranges[line]
                    # 70% du temps proche de l'optimal, 30% éloigné
                    if np.random.random() < 0.7:
                        machine_speed = np.random.normal(optimal_speeds[line], 50)
                    else:
                        machine_speed = np.random.uniform(min_speed, max_speed)
                    machine_speed = int(np.clip(machine_speed, min_speed, max_speed))
                    
                    # Variations réalistes
                    seasonal_effect = 5 * np.sin(2 * np.pi * day / 365)
                    hour_effect = -3 if hour < 8 or hour > 20 else 0
                    random_var = np.random.normal(0, 3)
                    
                    # Impact de la vitesse sur OEE (courbe en U)
                    # Plus on s'éloigne de l'optimal, plus l'OEE baisse
                    speed_deviation = abs(machine_speed - optimal_speeds[line])
                    speed_penalty = (speed_deviation / 100) ** 1.5  # Pénalité non-linéaire
                    
                    # Anomalies aléatoires (5% de chance)
                    anomaly = -15 if np.random.random() < 0.05 else 0
                    
                    oee = base_oee + seasonal_effect + hour_effect + random_var - speed_penalty + anomaly
                    oee = max(40, min(95, oee))  # Bornes réalistes
                    
                    # Composantes OEE (impactées par la vitesse)
                    # Vitesse trop élevée → baisse qualité
                    # Vitesse trop basse → baisse performance
                    speed_ratio = machine_speed / optimal_speeds[line]
                    
                    availability = oee * np.random.uniform(0.85, 0.95) / 0.9
                    performance = oee * np.random.uniform(0.88, 0.98) / 0.93
                    if speed_ratio > 1.15:  # Trop rapide
                        performance *= 1.05  # Meilleure performance
                    elif speed_ratio < 0.85:  # Trop lent
                        performance *= 0.92  # Pire performance
                    
                    quality = oee * np.random.uniform(0.92, 0.99) / 0.96
                    if speed_ratio > 1.15:  # Trop rapide
                        quality *= 0.90  # Plus de défauts
                    elif speed_ratio < 0.85:  # Trop lent
                        quality *= 1.02  # Meilleure qualité
                    
                    # Production réelle basée sur la vitesse
                    production_rate = machine_speed  # pièces/heure
                    actual_production = int(production_rate * (oee / 100))
                    
                    oee_records.append({
                        'timestamp': timestamp,
                        'line_id': line,
                        'product_type': product_type,
                        'machine_speed': machine_speed,
                        'oee': round(oee, 2),
                        'availability': round(min(100, max(40, availability)), 2),
                        'performance': round(min(100, max(40, performance)), 2),
                        'quality': round(min(100, max(40, quality)), 2),
                        'production_time': 60,
                        'planned_production_time': 60,
                        'good_pieces': int(actual_production * (quality / 100)),
                        'total_pieces': actual_production
                    })
        
        oee_df = pd.DataFrame(oee_records)
        oee_df.to_csv(os.path.join(self.data_path, 'oee_data.csv'), index=False)
        print(f"✓ {len(oee_records)} enregistrements OEE générés")
        
        # 2. Génération des arrêts
        stop_types = [
            'Changement_Format', 'Panne_Mecanique', 'Panne_Electrique',
            'Reglage', 'Nettoyage', 'Attente_Materiel', 'Bourrage',
            'Maintenance_Preventive', 'Probleme_Qualite', 'Attente_Operateur'
        ]
        
        stops_records = []
        stop_id = 1
        for day in range(730):
            date = start_date + timedelta(days=day)
            if date.weekday() >= 5:
                continue
            
            for line in lines:
                # Nombre d'arrêts par jour (distribution réaliste)
                num_stops = np.random.poisson(8)
                
                for _ in range(num_stops):
                    stop_type = np.random.choice(stop_types)
                    
                    # Durée selon le type
                    duration_ranges = {
                        'Changement_Format': (30, 120),
                        'Panne_Mecanique': (20, 180),
                        'Panne_Electrique': (10, 90),
                        'Reglage': (5, 30),
                        'Nettoyage': (15, 45),
                        'Attente_Materiel': (10, 60),
                        'Bourrage': (5, 25),
                        'Maintenance_Preventive': (60, 240),
                        'Probleme_Qualite': (10, 120),
                        'Attente_Operateur': (5, 30)
                    }
                    
                    min_dur, max_dur = duration_ranges[stop_type]
                    duration = np.random.randint(min_dur, max_dur)
                    
                    start_hour = np.random.randint(6, 22)
                    start_time = date + timedelta(hours=start_hour, minutes=np.random.randint(0, 60))
                    end_time = start_time + timedelta(minutes=duration)
                    
                    machine = np.random.choice(machines_per_line[line])
                    
                    stops_records.append({
                        'stop_id': stop_id,
                        'line_id': line,
                        'machine_id': machine,
                        'stop_type': stop_type,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration_minutes': duration,
                        'description': f"{stop_type} sur {machine}",
                        'operator': f"OP{np.random.randint(1, 15)}",
                        'resolved': True
                    })
                    stop_id += 1
        
        stops_df = pd.DataFrame(stops_records)
        stops_df.to_csv(os.path.join(self.data_path, 'stops_data.csv'), index=False)
        print(f"✓ {len(stops_records)} arrêts générés")
        
        # 3. Génération des données qualité
        quality_records = []
        defect_types = [
            'Dimension_Hors_Tolerance', 'Defaut_Surface', 'Pliage_Incorrect',
            'Impression_Defectueuse', 'Contamination', 'Deformation'
        ]
        
        for day in range(730):
            date = start_date + timedelta(days=day)
            if date.weekday() >= 5:
                continue
            
            for line in lines:
                for shift in range(3):  # 3 équipes
                    timestamp = date + timedelta(hours=8 * shift)
                    
                    total_produced = np.random.randint(8000, 12000)
                    defect_rate = np.random.uniform(0.01, 0.08)
                    total_defects = int(total_produced * defect_rate)
                    
                    quality_records.append({
                        'timestamp': timestamp,
                        'line_id': line,
                        'shift': shift + 1,
                        'total_produced': total_produced,
                        'total_defects': total_defects,
                        'defect_rate': round(defect_rate * 100, 2),
                        'defect_type': np.random.choice(defect_types),
                        'rework_count': int(total_defects * 0.3),
                        'scrap_count': int(total_defects * 0.7)
                    })
        
        quality_df = pd.DataFrame(quality_records)
        quality_df.to_csv(os.path.join(self.data_path, 'quality_data.csv'), index=False)
        print(f"✓ {len(quality_records)} enregistrements qualité générés")
        
        # 4. Génération des anomalies et solutions
        anomalies_records = []
        anomaly_id = 1
        
        anomaly_templates = [
            {
                'symptom': 'Baisse soudaine de performance de 15%',
                'root_cause': 'Usure des courroies de transmission',
                'solution': 'Remplacement des courroies et réalignement',
                'impact_oee': -15
            },
            {
                'symptom': 'Arrêts micro-répétitifs toutes les 10 minutes',
                'root_cause': 'Capteur de position défectueux',
                'solution': 'Remplacement du capteur et recalibration',
                'impact_oee': -8
            },
            {
                'symptom': 'Augmentation du taux de rebut à 7%',
                'root_cause': 'Dérive de la température de séchage',
                'solution': 'Recalibration du système de contrôle thermique',
                'impact_oee': -5
            },
            {
                'symptom': 'Bourrage fréquent au niveau de l\'alimentation',
                'root_cause': 'Tension d\'alimentation incorrecte',
                'solution': 'Ajustement de la tension et nettoyage des rouleaux',
                'impact_oee': -12
            },
            {
                'symptom': 'Vibrations anormales détectées',
                'root_cause': 'Roulements usés sur l\'axe principal',
                'solution': 'Remplacement des roulements et équilibrage',
                'impact_oee': -10
            },
            {
                'symptom': 'Qualité d\'impression dégradée',
                'root_cause': 'Viscosité d\'encre non conforme',
                'solution': 'Ajustement de la viscosité et nettoyage des buses',
                'impact_oee': -6
            }
        ]
        
        for day in range(0, 730, 7):  # Une anomalie toutes les semaines environ
            date = start_date + timedelta(days=day)
            line = np.random.choice(lines)
            machine = np.random.choice(machines_per_line[line])
            template = np.random.choice(anomaly_templates)
            
            resolution_time = np.random.randint(30, 480)  # 30min à 8h
            
            anomalies_records.append({
                'anomaly_id': anomaly_id,
                'timestamp': date,
                'line_id': line,
                'machine_id': machine,
                'symptom': template['symptom'],
                'root_cause': template['root_cause'],
                'solution_applied': template['solution'],
                'resolution_time_minutes': resolution_time,
                'impact_oee': template['impact_oee'],
                'recurrence_count': np.random.randint(1, 5),
                'priority': np.random.choice(['Low', 'Medium', 'High', 'Critical']),
                'status': 'Resolved'
            })
            anomaly_id += 1
        
        anomalies_df = pd.DataFrame(anomalies_records)
        anomalies_df.to_csv(os.path.join(self.data_path, 'anomalies_data.csv'), index=False)
        print(f"✓ {len(anomalies_records)} anomalies générées")
        
        print("\nGénération des données terminée avec succès!")
        print(f"Total: {len(oee_records) + len(stops_records) + len(quality_records) + len(anomalies_records)} enregistrements")
    
    def get_current_metrics(self):
        """Récupère les métriques actuelles"""
        if self.oee_data is None:
            return {}
        
        # Dernières 24h
        latest = self.oee_data[self.oee_data['timestamp'] >= 
                              self.oee_data['timestamp'].max() - timedelta(days=1)]
        
        metrics = {}
        for line in ['L1', 'L2', 'L3']:
            line_data = latest[latest['line_id'] == line]
            if len(line_data) > 0:
                metrics[line] = {
                    'oee': round(line_data['oee'].mean(), 2),
                    'availability': round(line_data['availability'].mean(), 2),
                    'performance': round(line_data['performance'].mean(), 2),
                    'quality': round(line_data['quality'].mean(), 2),
                    'status': 'Running' if line_data['oee'].iloc[-1] > 60 else 'Warning'
                }
        
        return metrics
    
    def get_historical_data(self, line_id='all', days=90):
        """Récupère les données historiques"""
        if self.oee_data is None:
            return []
        
        cutoff = self.oee_data['timestamp'].max() - timedelta(days=days)
        data = self.oee_data[self.oee_data['timestamp'] >= cutoff]
        
        if line_id != 'all':
            data = data[data['line_id'] == line_id]
        
        return data.to_dict('records')
    
    def get_average_oee(self):
        """Calcule l'OEE moyen global"""
        if self.oee_data is None:
            return 0
        
        # Moyenne sur les 30 derniers jours
        cutoff = self.oee_data['timestamp'].max() - timedelta(days=30)
        recent = self.oee_data[self.oee_data['timestamp'] >= cutoff]
        
        return round(recent['oee'].mean(), 2)
    
    def get_data_for_training(self):
        """Prépare les données pour l'entraînement des modèles"""
        if self.oee_data is None:
            return None
        
        # Enrichissement avec features temporelles
        df = self.oee_data.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        
        # Ajout des features de stops
        if self.stops_data is not None:
            # Compter les arrêts par jour et par ligne
            df['date'] = df['timestamp'].dt.date
            stops_per_day = self.stops_data.groupby([
                self.stops_data['start_time'].dt.date,
                'line_id'
            ])['duration_minutes'].agg(['count', 'sum']).reset_index()
            stops_per_day.columns = ['date', 'line_id', 'stop_count', 'stop_duration']
            
            df = df.merge(stops_per_day, on=['date', 'line_id'], how='left')
            df['stop_count'] = df['stop_count'].fillna(0)
            df['stop_duration'] = df['stop_duration'].fillna(0)
        
        return df
