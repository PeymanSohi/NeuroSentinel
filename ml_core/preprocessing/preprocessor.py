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
        """
        features = {}
        
        # System metrics
        if 'system' in data:
            sys_data = data['system']
            features.update({
                'cpu_percent': sys_data.get('cpu_percent', 0),
                'memory_percent': sys_data.get('memory_percent', 0),
                'disk_usage_percent': sys_data.get('disk_usage_percent', 0),
                'load_average_1m': sys_data.get('load_average', [0, 0, 0])[0],
                'load_average_5m': sys_data.get('load_average', [0, 0, 0])[1],
                'load_average_15m': sys_data.get('load_average', [0, 0, 0])[2],
                'boot_time': sys_data.get('boot_time', 0),
                'uptime_hours': (pd.Timestamp.now().timestamp() - sys_data.get('boot_time', 0)) / 3600
            })
        
        # Process metrics
        if 'process' in data:
            proc_data = data['process']
            features.update({
                'total_processes': len(proc_data.get('processes', [])),
                'unique_users': len(set(p.get('username', '') for p in proc_data.get('processes', []))),
                'avg_process_cpu': np.mean([p.get('cpu_percent', 0) for p in proc_data.get('processes', [])]),
                'avg_process_memory': np.mean([p.get('memory_percent', 0) for p in proc_data.get('processes', [])]),
                'max_process_cpu': np.max([p.get('cpu_percent', 0) for p in proc_data.get('processes', [])]),
                'max_process_memory': np.max([p.get('memory_percent', 0) for p in proc_data.get('processes', [])])
            })
        
        # Network metrics
        if 'network' in data:
            net_data = data['network']
            features.update({
                'total_connections': len(net_data.get('connections', [])),
                'established_connections': len([c for c in net_data.get('connections', []) 
                                             if c.get('status') == 'ESTABLISHED']),
                'listening_ports': len([c for c in net_data.get('connections', []) 
                                      if c.get('status') == 'LISTEN']),
                'unique_remote_ips': len(set(c.get('raddr', {}).get('ip', '') 
                                           for c in net_data.get('connections', []) if c.get('raddr')))
            })
        
        # File system metrics
        if 'file' in data:
            file_data = data['file']
            features.update({
                'file_events_count': len(file_data.get('events', [])),
                'file_creations': len([e for e in file_data.get('events', []) 
                                     if e.get('event_type') == 'created']),
                'file_modifications': len([e for e in file_data.get('events', []) 
                                         if e.get('event_type') == 'modified']),
                'file_deletions': len([e for e in file_data.get('events', []) 
                                     if e.get('event_type') == 'deleted'])
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
            features.update({
                'running_containers': len(container_data.get('running_containers', [])),
                'total_containers': len(container_data.get('all_containers', [])),
                'container_cpu_usage': np.mean([c.get('cpu_percent', 0) for c in container_data.get('running_containers', [])]),
                'container_memory_usage': np.mean([c.get('memory_percent', 0) for c in container_data.get('running_containers', [])])
            })
        
        # Threat intelligence metrics
        if 'threat_intel' in data:
            threat_data = data['threat_intel']
            features.update({
                'threat_indicators': len(threat_data.get('indicators', [])),
                'high_risk_ips': len([i for i in threat_data.get('indicators', []) 
                                    if i.get('risk_score', 0) > 7]),
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