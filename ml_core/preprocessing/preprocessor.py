import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import hashlib
import json
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    Preprocesses system monitoring data for ML anomaly detection.
    Handles feature extraction, normalization, and encoding.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.scalers = {}
        self.label_encoders = {}
        self.tfidf_vectorizers = {}
        self.feature_names = []
        
    def extract_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract numerical and categorical features from system data.
        Ensures consistent feature set for all samples.
        """
        # Define expected features to ensure consistency
        expected_features = {
            # System metrics
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_usage_percent': 0.0,
            'load_average_1m': 0.0,
            'load_average_5m': 0.0,
            'load_average_15m': 0.0,
            'boot_time': 0.0,
            'uptime_hours': 0.0,
            
            # Process metrics
            'total_processes': 0,
            'unique_users': 0,
            'avg_process_cpu': 0.0,
            'avg_process_memory': 0.0,
            'max_process_cpu': 0.0,
            'max_process_memory': 0.0,
            
            # Network metrics
            'total_connections': 0,
            'established_connections': 0,
            'listening_ports': 0,
            'unique_remote_ips': 0,
            
            # File system metrics
            'file_events_count': 0,
            'file_creations': 0,
            'file_modifications': 0,
            'file_deletions': 0,
            
            # User activity metrics
            'logged_in_users': 0,
            'total_users': 0,
            'total_groups': 0,
            'recent_logins': 0,
            
            # Security metrics
            'antivirus_running': 0,
            'firewall_rules_count': 0,
            'ids_alerts': 0,
            'security_updates_pending': 0,
            
            # Container metrics
            'running_containers': 0,
            'total_containers': 0,
            'container_cpu_usage': 0.0,
            'container_memory_usage': 0.0,
            
            # Threat intelligence metrics
            'threat_indicators': 0,
            'high_risk_ips': 0,
            'malware_detections': 0
        }
        
        features = expected_features.copy()
        
        # System metrics
        if 'system' in data:
            sys_data = data['system']
            features.update({
                'cpu_percent': float(sys_data.get('cpu_percent', 0)),
                'memory_percent': float(sys_data.get('memory_percent', 0)),
                'disk_usage_percent': float(sys_data.get('disk_usage_percent', 0)),
                'load_average_1m': float(sys_data.get('load_average', [0, 0, 0])[0]),
                'load_average_5m': float(sys_data.get('load_average', [0, 0, 0])[1]),
                'load_average_15m': float(sys_data.get('load_average', [0, 0, 0])[2]),
                'boot_time': float(sys_data.get('boot_time', 0)),
                'uptime_hours': float((pd.Timestamp.now().timestamp() - sys_data.get('boot_time', 0)) / 3600)
            })
        
        # Process metrics
        if 'process' in data:
            proc_data = data['process']
            processes = proc_data.get('processes', [])
            if processes:
                features.update({
                    'total_processes': len(processes),
                    'unique_users': len(set(p.get('username', '') for p in processes)),
                    'avg_process_cpu': float(np.mean([p.get('cpu_percent', 0) for p in processes])),
                    'avg_process_memory': float(np.mean([p.get('memory_percent', 0) for p in processes])),
                    'max_process_cpu': float(np.max([p.get('cpu_percent', 0) for p in processes])),
                    'max_process_memory': float(np.max([p.get('memory_percent', 0) for p in processes]))
                })
        
        # Network metrics
        if 'network' in data:
            net_data = data['network']
            connections = net_data.get('connections', [])
            features.update({
                'total_connections': len(connections),
                'established_connections': len([c for c in connections if c.get('status') == 'ESTABLISHED']),
                'listening_ports': len([c for c in connections if c.get('status') == 'LISTEN']),
                'unique_remote_ips': len(set(c.get('raddr', {}).get('ip', '') for c in connections if c.get('raddr')))
            })
        
        # File system metrics
        if 'file' in data:
            file_data = data['file']
            events = file_data.get('events', [])
            features.update({
                'file_events_count': len(events),
                'file_creations': len([e for e in events if e.get('event_type') == 'created']),
                'file_modifications': len([e for e in events if e.get('event_type') == 'modified']),
                'file_deletions': len([e for e in events if e.get('event_type') == 'deleted'])
            })
        
        # User activity metrics
        if 'user' in data:
            user_data = data['user']
            features.update({
                'logged_in_users': len(user_data.get('logged_in_users', [])),
                'total_users': len(user_data.get('users', [])),
                'total_groups': len(user_data.get('groups', [])),
                'recent_logins': len(user_data.get('recent_logins', []))
            })
        
        # Security metrics
        if 'security_tools' in data:
            sec_data = data['security_tools']
            features.update({
                'antivirus_running': int(sec_data.get('antivirus_status', {}).get('running', False)),
                'firewall_rules_count': len(sec_data.get('firewall_rules', [])),
                'ids_alerts': len(sec_data.get('ids_alerts', [])),
                'security_updates_pending': len(sec_data.get('pending_updates', []))
            })
        
        # Container metrics
        if 'container' in data:
            container_data = data['container']
            running_containers = container_data.get('running_containers', [])
            features.update({
                'running_containers': len(running_containers),
                'total_containers': len(container_data.get('all_containers', [])),
                'container_cpu_usage': float(np.mean([c.get('cpu_percent', 0) for c in running_containers])) if running_containers else 0.0,
                'container_memory_usage': float(np.mean([c.get('memory_percent', 0) for c in running_containers])) if running_containers else 0.0
            })
        
        # Threat intelligence metrics
        if 'threat_intel' in data:
            threat_data = data['threat_intel']
            indicators = threat_data.get('indicators', [])
            features.update({
                'threat_indicators': len(indicators),
                'high_risk_ips': len([i for i in indicators if isinstance(i, dict) and i.get('risk_score', 0) > 7]),
                'malware_detections': len(threat_data.get('malware_detections', []))
            })
        
        return features
    
    def normalize_features(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Normalize features using appropriate scaling methods.
        """
        feature_vector = []
        feature_names = []
        
        for name, value in features.items():
            if isinstance(value, (int, float)) and not np.isnan(value):
                feature_vector.append(float(value))
                feature_names.append(name)
        
        # Convert to numpy array
        X = np.array(feature_vector).reshape(1, -1)
        
        # Store feature names for later use
        if not self.feature_names:
            self.feature_names = feature_names
        
        # Apply scaling if scaler is fitted
        if 'main_scaler' in self.scalers:
            X = self.scalers['main_scaler'].transform(X)
        
        return X
    
    def fit_scalers(self, data_samples: List[Dict[str, Any]]):
        """
        Fit scalers on historical data samples.
        """
        feature_vectors = []
        
        for sample in data_samples:
            features = self.extract_features(sample)
            feature_vector = []
            feature_names = []
            
            for name, value in features.items():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    feature_vector.append(float(value))
                    feature_names.append(name)
            
            if feature_vector:
                feature_vectors.append(feature_vector)
                if not self.feature_names:
                    self.feature_names = feature_names
        
        if feature_vectors:
            X = np.array(feature_vectors)
            self.scalers['main_scaler'] = StandardScaler()
            self.scalers['main_scaler'].fit(X)
            logger.info(f"Fitted scaler on {len(feature_vectors)} samples with {X.shape[1]} features")
    
    def create_sequence_features(self, data_samples: List[Dict[str, Any]], 
                               sequence_length: int = 10) -> np.ndarray:
        """
        Create sequence features for time-series anomaly detection.
        """
        if len(data_samples) < sequence_length:
            return np.array([])
        
        sequences = []
        for i in range(len(data_samples) - sequence_length + 1):
            sequence = data_samples[i:i + sequence_length]
            sequence_features = []
            
            for sample in sequence:
                features = self.extract_features(sample)
                feature_vector = [float(features.get(name, 0)) for name in self.feature_names]
                sequence_features.extend(feature_vector)
            
            sequences.append(sequence_features)
        
        return np.array(sequences)
    
    def extract_text_features(self, text_data: List[str], feature_name: str) -> np.ndarray:
        """
        Extract features from text data using TF-IDF.
        """
        if feature_name not in self.tfidf_vectorizers:
            self.tfidf_vectorizers[feature_name] = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
            return self.tfidf_vectorizers[feature_name].fit_transform(text_data)
        else:
            return self.tfidf_vectorizers[feature_name].transform(text_data)
    
    def save_preprocessor(self, filepath: str):
        """
        Save preprocessor state to file.
        """
        import joblib
        preprocessor_state = {
            'scalers': self.scalers,
            'label_encoders': self.label_encoders,
            'tfidf_vectorizers': self.tfidf_vectorizers,
            'feature_names': self.feature_names,
            'config': self.config
        }
        joblib.dump(preprocessor_state, filepath)
        logger.info(f"Saved preprocessor to {filepath}")
    
    def load_preprocessor(self, filepath: str):
        """
        Load preprocessor state from file.
        """
        import joblib
        preprocessor_state = joblib.load(filepath)
        self.scalers = preprocessor_state['scalers']
        self.label_encoders = preprocessor_state['label_encoders']
        self.tfidf_vectorizers = preprocessor_state['tfidf_vectorizers']
        self.feature_names = preprocessor_state['feature_names']
        self.config = preprocessor_state['config']
        logger.info(f"Loaded preprocessor from {filepath}") 