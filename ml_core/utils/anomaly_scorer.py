import numpy as np
from typing import Dict, List, Any, Tuple
import logging
try:
    from ml_core.detectors import IsolationForestDetector, AutoEncoderDetector
    from ml_core.preprocessing import DataPreprocessor
except ImportError:
    from detectors import IsolationForestDetector, AutoEncoderDetector
    from preprocessing import DataPreprocessor

logger = logging.getLogger(__name__)

class AnomalyScorer:
    """
    Combines multiple anomaly detection methods and provides unified scoring.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.detectors = {}
        self.preprocessor = DataPreprocessor()
        self.weights = self.config.get('weights', {'isolation_forest': 0.5, 'autoencoder': 0.5})
        
    def add_detector(self, name: str, detector, weight: float = 1.0):
        """Add an anomaly detector with a weight."""
        self.detectors[name] = detector
        if name not in self.weights:
            self.weights[name] = weight
    
    def fit(self, data_samples: List[Dict[str, Any]]):
        """Fit all detectors on the provided data."""
        # Preprocess data
        self.preprocessor.fit_scalers(data_samples)
        
        # Extract features for all samples
        feature_vectors = []
        for sample in data_samples:
            features = self.preprocessor.extract_features(sample)
            X = self.preprocessor.normalize_features(features)
            if X.size > 0:
                feature_vectors.append(X.flatten())
        
        if not feature_vectors:
            logger.warning("No valid feature vectors found for training")
            return
        
        X_train = np.array(feature_vectors)
        logger.info(f"Training detectors on {X_train.shape[0]} samples with {X_train.shape[1]} features")
        
        # Fit each detector
        for name, detector in self.detectors.items():
            try:
                if hasattr(detector, 'fit'):
                    detector.fit(X_train)
                    logger.info(f"Fitted detector: {name}")
                else:
                    logger.warning(f"Detector {name} has no fit method")
            except Exception as e:
                logger.error(f"Error fitting detector {name}: {e}")
    
    def score(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Score a single data sample using all detectors."""
        # Extract and normalize features
        features = self.preprocessor.extract_features(data)
        X = self.preprocessor.normalize_features(features)
        
        if X.size == 0:
            return {name: 0.0 for name in self.detectors.keys()}
        
        scores = {}
        for name, detector in self.detectors.items():
            try:
                if hasattr(detector, 'anomaly_score'):
                    score = detector.anomaly_score(X)
                    scores[name] = float(score[0]) if hasattr(score, '__len__') else float(score)
                else:
                    scores[name] = 0.0
            except Exception as e:
                logger.error(f"Error scoring with detector {name}: {e}")
                scores[name] = 0.0
        
        return scores
    
    def combined_score(self, data: Dict[str, Any]) -> float:
        """Get combined anomaly score from all detectors."""
        individual_scores = self.score(data)
        
        # Weighted average
        total_score = 0.0
        total_weight = 0.0
        
        for name, score in individual_scores.items():
            weight = self.weights.get(name, 1.0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def is_anomalous(self, data: Dict[str, Any], threshold: float = 0.5) -> bool:
        """Determine if data is anomalous based on combined score."""
        score = self.combined_score(data)
        return score > threshold
    
    def get_detector_status(self) -> Dict[str, bool]:
        """Get status of all detectors (fitted or not)."""
        status = {}
        for name, detector in self.detectors.items():
            if hasattr(detector, 'is_fitted'):
                status[name] = detector.is_fitted
            else:
                status[name] = True  # Assume fitted if no status attribute
        return status
    
    def save_scorer(self, filepath: str):
        """Save the anomaly scorer state."""
        import joblib
        scorer_state = {
            'detectors': self.detectors,
            'weights': self.weights,
            'config': self.config
        }
        joblib.dump(scorer_state, filepath)
        self.preprocessor.save_preprocessor(filepath + '_preprocessor')
        logger.info(f"Saved anomaly scorer to {filepath}")
    
    def load_scorer(self, filepath: str):
        """Load the anomaly scorer state."""
        import joblib
        scorer_state = joblib.load(filepath)
        self.detectors = scorer_state['detectors']
        self.weights = scorer_state['weights']
        self.config = scorer_state['config']
        self.preprocessor.load_preprocessor(filepath + '_preprocessor')
        logger.info(f"Loaded anomaly scorer from {filepath}") 