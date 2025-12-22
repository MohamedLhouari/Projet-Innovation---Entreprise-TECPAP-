"""
Modèle de prédiction OEE utilisant des algorithmes de Machine Learning
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime, timedelta

class OEEPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.models_path = os.path.join(os.path.dirname(__file__), 'saved_models')
        self.trained = False
        
        # Créer le dossier des modèles s'il n'existe pas
        if not os.path.exists(self.models_path):
            os.makedirs(self.models_path)
    
    def prepare_features(self, df):
        """Prépare les features pour l'entraînement"""
        features = df.copy()
        
        # Features temporelles
        if 'timestamp' in features.columns:
            features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
            features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
            features['month'] = pd.to_datetime(features['timestamp']).dt.month
            features['day_of_year'] = pd.to_datetime(features['timestamp']).dt.dayofyear
            features['week_of_year'] = pd.to_datetime(features['timestamp']).dt.isocalendar().week
        
        # Encoding de la ligne
        features['line_L1'] = (features['line_id'] == 'L1').astype(int)
        features['line_L2'] = (features['line_id'] == 'L2').astype(int)
        features['line_L3'] = (features['line_id'] == 'L3').astype(int)
        
        # Features de tendance (moyennes mobiles)
        if 'oee' in features.columns:
            features['oee_ma_7'] = features.groupby('line_id')['oee'].transform(
                lambda x: x.rolling(window=7, min_periods=1).mean()
            )
            features['oee_ma_24'] = features.groupby('line_id')['oee'].transform(
                lambda x: x.rolling(window=24, min_periods=1).mean()
            )
            features['oee_std_7'] = features.groupby('line_id')['oee'].transform(
                lambda x: x.rolling(window=7, min_periods=1).std()
            ).fillna(0)
        
        # Features de performance
        if 'availability' in features.columns:
            features['avail_perf_ratio'] = features['availability'] / (features['performance'] + 0.01)
            features['perf_quality_ratio'] = features['performance'] / (features['quality'] + 0.01)
        
        # Sélection des colonnes numériques
        numeric_features = ['hour', 'day_of_week', 'month', 'day_of_year', 'week_of_year',
                          'line_L1', 'line_L2', 'line_L3']
        
        if 'availability' in features.columns:
            numeric_features.extend(['availability', 'performance', 'quality',
                                   'oee_ma_7', 'oee_ma_24', 'oee_std_7',
                                   'avail_perf_ratio', 'perf_quality_ratio'])
        
        if 'stop_count' in features.columns:
            numeric_features.extend(['stop_count', 'stop_duration'])
            features['stop_count'] = features['stop_count'].fillna(0)
            features['stop_duration'] = features['stop_duration'].fillna(0)
        
        # Garder seulement les colonnes qui existent
        numeric_features = [col for col in numeric_features if col in features.columns]
        
        return features[numeric_features]
    
    def train(self):
        """Entraîne le modèle de prédiction"""
        from data.data_loader import DataLoader
        
        print("Entraînement du modèle de prédiction OEE...")
        
        # Charger les données
        loader = DataLoader()
        loader.load_data()
        df = loader.get_data_for_training()
        
        if df is None or len(df) == 0:
            print("Erreur: Pas de données disponibles pour l'entraînement")
            return False
        
        # Préparation des features et target
        X = self.prepare_features(df)
        y = df['oee']
        
        self.feature_columns = X.columns.tolist()
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normalisation
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entraînement d'un ensemble de modèles
        print("  - Entraînement Random Forest...")
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=10,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_scaled, y_train)
        
        print("  - Entraînement Gradient Boosting...")
        gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=7,
            learning_rate=0.1,
            random_state=42
        )
        gb_model.fit(X_train_scaled, y_train)
        
        # Évaluation
        rf_pred = rf_model.predict(X_test_scaled)
        gb_pred = gb_model.predict(X_test_scaled)
        
        # Prédiction ensembliste (moyenne pondérée)
        y_pred = 0.6 * rf_pred + 0.4 * gb_pred
        
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"  - MAE: {mae:.2f}%")
        print(f"  - R²: {r2:.3f}")
        
        # Utiliser le meilleur modèle individuel ou l'ensemble
        if r2 > 0.75:
            # Créer un modèle ensembliste
            self.model = {
                'rf': rf_model,
                'gb': gb_model,
                'weights': [0.6, 0.4]
            }
            self.trained = True
            
            # Sauvegarder
            joblib.dump(self.model, os.path.join(self.models_path, 'oee_model.pkl'))
            joblib.dump(self.scaler, os.path.join(self.models_path, 'scaler.pkl'))
            joblib.dump(self.feature_columns, os.path.join(self.models_path, 'features.pkl'))
            
            print("  - Modèle entraîné et sauvegardé avec succès")
            return True
        else:
            print("  - Performance insuffisante, réentraînement nécessaire")
            return False
    
    def predict(self, features_df):
        """Fait une prédiction OEE"""
        if not self.trained:
            self._load_model()
        
        if self.model is None:
            return None
        
        # Préparer les features
        X = self.prepare_features(features_df)
        
        # Assurer que toutes les colonnes sont présentes
        for col in self.feature_columns:
            if col not in X.columns:
                X[col] = 0
        
        X = X[self.feature_columns]
        X_scaled = self.scaler.transform(X)
        
        # Prédiction ensembliste
        rf_pred = self.model['rf'].predict(X_scaled)
        gb_pred = self.model['gb'].predict(X_scaled)
        
        predictions = (self.model['weights'][0] * rf_pred + 
                      self.model['weights'][1] * gb_pred)
        
        # Contraintes réalistes
        predictions = np.clip(predictions, 40, 95)
        
        return predictions
    
    def predict_next_days(self, days=7):
        """Prédit l'OEE pour les prochains jours"""
        from data.data_loader import DataLoader
        
        if not self.trained:
            self._load_model()
        
        loader = DataLoader()
        loader.load_data()
        
        # Récupérer les dernières données
        recent_data = loader.oee_data.tail(168)  # Dernière semaine
        
        predictions = {}
        for line in ['L1', 'L2', 'L3']:
            line_data = recent_data[recent_data['line_id'] == line]
            
            if len(line_data) == 0:
                continue
            
            # Préparer les features futures
            last_timestamp = line_data['timestamp'].max()
            future_dates = [last_timestamp + timedelta(days=i+1) for i in range(days)]
            
            future_features = []
            for date in future_dates:
                # Moyenne des heures de production (8h à 20h)
                for hour in range(8, 21):
                    feature_row = {
                        'timestamp': date + timedelta(hours=hour),
                        'line_id': line,
                        'availability': line_data['availability'].tail(24).mean(),
                        'performance': line_data['performance'].tail(24).mean(),
                        'quality': line_data['quality'].tail(24).mean(),
                        'stop_count': 0,
                        'stop_duration': 0
                    }
                    future_features.append(feature_row)
            
            future_df = pd.DataFrame(future_features)
            
            # Prédire
            preds = self.predict(future_df)
            
            if preds is not None:
                # Agréger par jour
                daily_preds = []
                for i in range(days):
                    day_preds = preds[i*13:(i+1)*13]
                    daily_preds.append({
                        'date': (last_timestamp + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                        'oee_predicted': round(float(np.mean(day_preds)), 2),
                        'confidence': 'High' if len(day_preds) > 0 else 'Low',
                        'trend': self._calculate_trend(day_preds)
                    })
                
                predictions[line] = daily_preds
        
        return predictions
    
    def predict_line(self, line_id, horizon=7):
        """Prédiction détaillée pour une ligne spécifique"""
        predictions = self.predict_next_days(days=horizon)
        
        if line_id not in predictions:
            return None
        
        line_preds = predictions[line_id]
        
        # Calculs statistiques
        oee_values = [p['oee_predicted'] for p in line_preds]
        
        return {
            'line_id': line_id,
            'predictions': line_preds,
            'statistics': {
                'mean': round(np.mean(oee_values), 2),
                'min': round(np.min(oee_values), 2),
                'max': round(np.max(oee_values), 2),
                'std': round(np.std(oee_values), 2),
                'trend': 'Stable' if np.std(oee_values) < 3 else 'Variable'
            }
        }
    
    def _calculate_trend(self, predictions):
        """Calcule la tendance"""
        if len(predictions) < 2:
            return 'Stable'
        
        # Régression linéaire simple
        x = np.arange(len(predictions))
        slope = np.polyfit(x, predictions, 1)[0]
        
        if slope > 0.5:
            return 'Augmentation'
        elif slope < -0.5:
            return 'Diminution'
        else:
            return 'Stable'
    
    def _load_model(self):
        """Charge le modèle sauvegardé"""
        try:
            model_path = os.path.join(self.models_path, 'oee_model.pkl')
            scaler_path = os.path.join(self.models_path, 'scaler.pkl')
            features_path = os.path.join(self.models_path, 'features.pkl')
            
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.feature_columns = joblib.load(features_path)
                self.trained = True
                return True
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {e}")
        
        return False
