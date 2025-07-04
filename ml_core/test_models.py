#!/usr/bin/env python3
"""
Test script for NeuroSentinel ML Core components.
"""

import sys
import os
import json
import logging
import numpy as np
from pathlib import Path

# Ensure ml_core is in sys.path for both direct and module execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from detectors import IsolationForestDetector, AutoEncoderDetector
    from preprocessing import DataPreprocessor
    from models import AutoEncoder
    from utils import AnomalyScorer, ModelManager
except ImportError:
    # Try absolute imports if running as a module
    from ml_core.detectors import IsolationForestDetector, AutoEncoderDetector
    from ml_core.preprocessing import DataPreprocessor
    from ml_core.models import AutoEncoder
    from ml_core.utils import AnomalyScorer, ModelManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_data(n_samples: int = 100) -> list:
    """Create sample system monitoring data for testing."""
    samples = []
    
    for i in range(n_samples):
        sample = {
            "agent_id": f"test_agent_{i}",
            "timestamp": 1234567890 + i,
            "system": {
                "cpu_percent": np.random.uniform(10, 80),
                "memory_percent": np.random.uniform(20, 90),
                "disk_usage_percent": np.random.uniform(30, 95),
                "load_average": [np.random.uniform(0.1, 2.0) for _ in range(3)],
                "boot_time": 1234567890
            },
            "process": {
                "processes": [
                    {
                        "pid": np.random.randint(1, 10000),
                        "name": f"process_{j}",
                        "cpu_percent": np.random.uniform(0, 10),
                        "memory_percent": np.random.uniform(0, 5)
                    }
                    for j in range(np.random.randint(50, 200))
                ]
            },
            "network": {
                "connections": [
                    {
                        "status": np.random.choice(["ESTABLISHED", "LISTEN", "TIME_WAIT"]),
                        "raddr": {"ip": f"192.168.1.{np.random.randint(1, 255)}"}
                    }
                    for _ in range(np.random.randint(10, 100))
                ]
            },
            "file": {
                "events": [
                    {
                        "event_type": np.random.choice(["created", "modified", "deleted"]),
                        "src_path": f"/tmp/file_{j}.txt"
                    }
                    for j in range(np.random.randint(0, 5))
                ]
            },
            "user": {
                "logged_in_users": [f"user_{j}" for j in range(np.random.randint(1, 5))],
                "users": [f"user_{j}" for j in range(10)],
                "groups": [f"group_{j}" for j in range(5)]
            },
            "security_tools": {
                "antivirus_status": {"running": np.random.choice([True, False])},
                "firewall_rules": [f"rule_{j}" for j in range(np.random.randint(5, 20))],
                "ids_alerts": [],
                "pending_updates": []
            },
            "container": {
                "running_containers": [
                    {
                        "name": f"container_{j}",
                        "cpu_percent": np.random.uniform(0, 15),
                        "memory_percent": np.random.uniform(0, 10)
                    }
                    for j in range(np.random.randint(0, 10))
                ],
                "all_containers": []
            },
            "threat_intel": {
                "indicators": [],
                "malware_detections": []
            }
        }
        samples.append(sample)
    
    return samples

def test_preprocessor():
    """Test the DataPreprocessor."""
    logger.info("Testing DataPreprocessor...")
    
    # Create sample data
    data_samples = create_sample_data(50)
    
    # Test preprocessor
    preprocessor = DataPreprocessor()
    
    # Test feature extraction
    features = preprocessor.extract_features(data_samples[0])
    logger.info(f"Extracted {len(features)} features")
    
    # Test normalization
    X = preprocessor.normalize_features(features)
    logger.info(f"Normalized features shape: {X.shape}")
    
    # Test scaler fitting
    preprocessor.fit_scalers(data_samples)
    logger.info("Scalers fitted successfully")
    
    # Test with fitted scaler
    X_fitted = preprocessor.normalize_features(features)
    logger.info(f"Features after fitting: {X_fitted.shape}")
    
    return preprocessor

def test_isolation_forest():
    """Test IsolationForest detector."""
    logger.info("Testing IsolationForest detector...")
    
    # Create sample data
    data_samples = create_sample_data(100)
    
    # Preprocess data
    preprocessor = DataPreprocessor()
    preprocessor.fit_scalers(data_samples)
    
    # Extract features
    feature_vectors = []
    for sample in data_samples:
        features = preprocessor.extract_features(sample)
        X = preprocessor.normalize_features(features)
        if X.size > 0:
            feature_vectors.append(X.flatten())
    
    X_train = np.array(feature_vectors)
    
    # Create and train detector
    detector = IsolationForestDetector(n_estimators=50, contamination=0.1)
    detector.fit(X_train)
    
    # Test prediction
    test_features = preprocessor.extract_features(data_samples[0])
    test_X = preprocessor.normalize_features(test_features)
    
    prediction = detector.predict(test_X)
    score = detector.anomaly_score(test_X)
    
    logger.info(f"IsolationForest prediction: {prediction}")
    logger.info(f"IsolationForest anomaly score: {score}")
    
    return detector

def test_autoencoder():
    """Test AutoEncoder detector."""
    logger.info("Testing AutoEncoder detector...")
    
    # Create sample data
    data_samples = create_sample_data(100)
    
    # Preprocess data
    preprocessor = DataPreprocessor()
    preprocessor.fit_scalers(data_samples)
    
    # Extract features
    feature_vectors = []
    for sample in data_samples:
        features = preprocessor.extract_features(sample)
        X = preprocessor.normalize_features(features)
        if X.size > 0:
            feature_vectors.append(X.flatten())
    
    X_train = np.array(feature_vectors)
    
    # Create model
    input_dim = X_train.shape[1]
    model = AutoEncoder(input_dim=input_dim, hidden_dims=[input_dim//2, input_dim//4])
    
    # Create detector
    detector = AutoEncoderDetector(model)
    
    # Test prediction (without training for speed)
    test_features = preprocessor.extract_features(data_samples[0])
    test_X = preprocessor.normalize_features(test_features)
    
    score = detector.anomaly_score(test_X)
    logger.info(f"AutoEncoder anomaly score: {score}")
    
    return detector

def test_anomaly_scorer():
    """Test AnomalyScorer."""
    logger.info("Testing AnomalyScorer...")
    
    # Create sample data
    data_samples = create_sample_data(50)
    
    # Create scorer
    scorer = AnomalyScorer()
    
    # Add detectors
    scorer.add_detector("isolation_forest", IsolationForestDetector(n_estimators=50))
    
    # Test fitting
    scorer.fit(data_samples)
    
    # Test scoring
    test_data = data_samples[0]
    scores = scorer.score(test_data)
    combined_score = scorer.combined_score(test_data)
    
    logger.info(f"Individual scores: {scores}")
    logger.info(f"Combined score: {combined_score}")
    
    return scorer

def test_model_manager():
    """Test ModelManager."""
    logger.info("Testing ModelManager...")
    
    # Create model manager
    model_manager = ModelManager("test_models")
    
    # Test model registration
    model_id = model_manager.register_model("test_model", "isolation_forest", 
                                          description="Test model")
    logger.info(f"Registered model: {model_id}")
    
    # Test model listing
    models = model_manager.list_models()
    logger.info(f"Listed {len(models)} models")
    
    # Test model info
    model_info = model_manager.get_model_info(model_id)
    logger.info(f"Model info: {model_info}")
    
    # Cleanup
    model_manager.delete_model(model_id)
    logger.info("Model deleted")
    
    return model_manager

def main():
    """Run all tests."""
    logger.info("Starting ML Core tests...")
    
    try:
        # Test components
        test_preprocessor()
        test_isolation_forest()
        test_autoencoder()
        test_anomaly_scorer()
        test_model_manager()
        
        logger.info("All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    main() 