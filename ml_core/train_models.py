#!/usr/bin/env python3
"""
Enhanced training script for NeuroSentinel ML Core anomaly detection models.
Implements best practices for ML training including logging, validation, and experiment tracking.
"""

import argparse
import json
import logging
import numpy as np
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from detectors import IsolationForestDetector, AutoEncoderDetector
from preprocessing import DataPreprocessor
from models import AutoEncoder, AutoEncoderTrainer
from utils import ModelManager, AnomalyScorer
import torch
from torch.utils.data import DataLoader, TensorDataset

class ExperimentTracker:
    """Track experiment details and save metadata."""
    
    def __init__(self, experiment_name: str, output_dir: str):
        self.experiment_name = experiment_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.start_time = datetime.now()
        
        # Create experiment directory
        self.experiment_dir = self.output_dir / f"{experiment_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}"
        self.experiment_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging."""
        log_file = self.experiment_dir / "training.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_experiment_info(self, config: Dict[str, Any], data_info: Dict[str, Any]):
        """Log experiment information."""
        # Get git commit hash
        try:
            git_commit = subprocess.getoutput("git rev-parse HEAD")
            git_branch = subprocess.getoutput("git branch --show-current")
        except:
            git_commit = "unknown"
            git_branch = "unknown"
        
        experiment_info = {
            "experiment_name": self.experiment_name,
            "start_time": self.start_time.isoformat(),
            "git_commit": git_commit,
            "git_branch": git_branch,
            "config": config,
            "data_info": data_info,
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        # Save experiment info
        with open(self.experiment_dir / "experiment_info.json", "w") as f:
            json.dump(experiment_info, f, indent=2)
        
        # Log to console
        self.logger.info(f"Starting experiment: {self.experiment_name}")
        self.logger.info(f"Git commit: {git_commit}")
        self.logger.info(f"Git branch: {git_branch}")
        self.logger.info(f"Config: {json.dumps(config, indent=2)}")
        self.logger.info(f"Data info: {json.dumps(data_info, indent=2)}")
        
    def save_artifacts(self, model, preprocessor, config: Dict[str, Any], metrics: Dict[str, Any]):
        """Save all experiment artifacts."""
        # Save model
        model_path = self.experiment_dir / "model.joblib"
        model.save(str(model_path))
        
        # Save preprocessor
        preprocessor_path = self.experiment_dir / "preprocessor.joblib"
        preprocessor.save_preprocessor(str(preprocessor_path))
        
        # Save config
        config_path = self.experiment_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        # Save metrics
        metrics_path = self.experiment_dir / "metrics.json"
        def to_native(obj):
            if isinstance(obj, dict):
                return {k: to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [to_native(v) for v in obj]
            elif hasattr(obj, 'item') and callable(obj.item):
                return obj.item()
            elif hasattr(obj, 'tolist') and callable(obj.tolist):
                return obj.tolist()
            else:
                return float(obj) if isinstance(obj, (np.floating,)) else obj
        with open(metrics_path, "w") as f:
            json.dump(to_native(metrics), f, indent=2)
        
        self.logger.info(f"Saved artifacts to: {self.experiment_dir}")
        
    def log_metrics(self, metrics: Dict[str, Any]):
        """Log training metrics."""
        self.logger.info("Training Metrics:")
        for metric, value in metrics.items():
            self.logger.info(f"  {metric}: {value}")

def load_training_data(data_path: str) -> List[Dict[str, Any]]:
    """Load training data from JSON file."""
    with open(data_path, 'r') as f:
        return json.load(f)

def load_validation_data(validation_path: str) -> List[Dict[str, Any]]:
    """Load validation data from JSON file."""
    if validation_path and os.path.exists(validation_path):
        with open(validation_path, 'r') as f:
            return json.load(f)
    return []

def evaluate_model(detector, preprocessor, validation_data: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate model on validation data."""
    if not validation_data:
        return {"validation_samples": 0}
    
    # Extract features from validation data
    feature_vectors = []
    labels = []  # 1 for anomaly, 0 for normal
    
    for sample in validation_data:
        features = preprocessor.extract_features(sample)
        X = preprocessor.normalize_features(features)
        if X.size > 0:
            feature_vectors.append(X.flatten())
            
            # Simple heuristic for anomaly labeling (you can improve this)
            is_anomaly = (
                sample.get('system', {}).get('cpu_percent', 0) > 80 or
                sample.get('system', {}).get('memory_percent', 0) > 90 or
                len(sample.get('threat_intel', {}).get('indicators', [])) > 0 or
                len(sample.get('security_tools', {}).get('ids_alerts', [])) > 0
            )
            labels.append(1 if is_anomaly else 0)
    
    if not feature_vectors:
        return {"validation_samples": 0}
    
    X_val = np.array(feature_vectors)
    y_val = np.array(labels)
    
    # Get predictions
    if hasattr(detector, 'anomaly_score'):
        scores = detector.anomaly_score(X_val)
        predictions = (scores > np.percentile(scores, config.get('evaluation', {}).get('threshold_percentile', 95))).astype(int)
    else:
        predictions = detector.predict(X_val)
        scores = np.zeros_like(predictions)  # Placeholder
    
    # Calculate metrics
    from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
    
    metrics = {
        "validation_samples": int(len(X_val)),
        "anomaly_samples": int(np.sum(y_val)),
        "normal_samples": int(len(y_val) - np.sum(y_val)),
        "precision": float(precision_score(y_val, predictions, zero_division=0)),
        "recall": float(recall_score(y_val, predictions, zero_division=0)),
        "f1_score": float(f1_score(y_val, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_val, scores) if len(np.unique(y_val)) > 1 else 0.5),
        "threshold_percentile": int(config.get('evaluation', {}).get('threshold_percentile', 95))
    }
    
    return metrics

def train_isolation_forest(data_samples: List[Dict[str, Any]], validation_data: List[Dict[str, Any]], 
                          config: Dict[str, Any], tracker: ExperimentTracker) -> Tuple[IsolationForestDetector, DataPreprocessor]:
    """Train IsolationForest model with enhanced logging."""
    tracker.logger.info("Training IsolationForest model...")
    
    # Set random seed for reproducibility
    np.random.seed(config.get('params', {}).get('random_state', 42))
    
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
    
    if not feature_vectors:
        raise ValueError("No valid features extracted from training data")
    
    X_train = np.array(feature_vectors)
    tracker.logger.info(f"Training on {X_train.shape[0]} samples with {X_train.shape[1]} features")
    
    # Create and train model
    detector = IsolationForestDetector(**config.get("params", {}))
    detector.fit(X_train)
    
    # Evaluate on validation data
    metrics = evaluate_model(detector, preprocessor, validation_data, config)
    tracker.log_metrics(metrics)
    
    return detector, preprocessor, metrics

def train_autoencoder(data_samples: List[Dict[str, Any]], validation_data: List[Dict[str, Any]], 
                     config: Dict[str, Any], tracker: ExperimentTracker) -> Tuple[AutoEncoderDetector, DataPreprocessor]:
    """Train AutoEncoder model with enhanced logging."""
    tracker.logger.info("Training AutoEncoder model...")
    
    # Set random seed for reproducibility
    torch.manual_seed(config.get('params', {}).get('random_state', 42))
    np.random.seed(config.get('params', {}).get('random_state', 42))
    
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
    
    if not feature_vectors:
        raise ValueError("No valid features extracted from training data")
    
    X_train = np.array(feature_vectors)
    tracker.logger.info(f"Training on {X_train.shape[0]} samples with {X_train.shape[1]} features")
    
    # Create model
    input_dim = X_train.shape[1]
    model_params = config.get("model_params", {})
    model = AutoEncoder(input_dim=input_dim, **model_params)
    
    # Create trainer
    trainer_params = config.get("trainer_params", {})
    trainer = AutoEncoderTrainer(model, **trainer_params)
    
    # Create dataloader
    X_tensor = torch.tensor(X_train, dtype=torch.float32)
    dataset = TensorDataset(X_tensor)
    dataloader = DataLoader(dataset, batch_size=config.get("training", {}).get("batch_size", 32), shuffle=True)
    
    # Train model
    epochs = config.get("training", {}).get("epochs", 10)
    training_losses = []
    
    for epoch in range(epochs):
        loss = trainer.train_epoch(dataloader)
        training_losses.append(loss)
        
        if epoch % 5 == 0 or epoch == epochs - 1:
            tracker.logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {loss:.6f}")
    
    # Compute threshold
    threshold = trainer.compute_threshold(dataloader, percentile=config.get("detector_params", {}).get("threshold_percentile", 95))
    
    # Create detector
    detector_params = config.get("detector_params", {}).copy()
    detector_params.pop("threshold", None)  # Remove threshold if present
    detector_params.pop("threshold_percentile", None)  # Remove threshold_percentile if present
    detector = AutoEncoderDetector(model, threshold=threshold, **detector_params)
    
    # Evaluate on validation data
    metrics = evaluate_model(detector, preprocessor, validation_data, config)
    metrics["final_training_loss"] = training_losses[-1] if training_losses else 0
    metrics["threshold"] = threshold
    tracker.log_metrics(metrics)
    
    return detector, preprocessor, metrics

def main():
    parser = argparse.ArgumentParser(description="Train NeuroSentinel anomaly detection models with best practices")
    parser.add_argument("--data", required=True, help="Path to training data JSON file")
    parser.add_argument("--validation", help="Path to validation data JSON file")
    parser.add_argument("--model-type", choices=["isolation_forest", "autoencoder"], required=True,
                       help="Type of model to train")
    parser.add_argument("--config", help="Path to model configuration JSON file")
    parser.add_argument("--output-dir", default="models", help="Output directory for trained models")
    parser.add_argument("--model-name", help="Name for the trained model")
    parser.add_argument("--experiment-name", help="Name for the experiment")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Load training data
    print(f"Loading training data from {args.data}")
    data_samples = load_training_data(args.data)
    
    # Load validation data
    validation_data = []
    if args.validation:
        print(f"Loading validation data from {args.validation}")
        validation_data = load_validation_data(args.validation)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Setup experiment tracking
    experiment_name = args.experiment_name or f"{args.model_type}_experiment"
    tracker = ExperimentTracker(experiment_name, str(output_dir))
    
    # Log data info
    data_info = {
        "training_samples": len(data_samples),
        "validation_samples": len(validation_data),
        "training_data_path": args.data,
        "validation_data_path": args.validation
    }
    tracker.log_experiment_info(config, data_info)
    
    # Train model
    try:
        if args.model_type == "isolation_forest":
            detector, preprocessor, metrics = train_isolation_forest(data_samples, validation_data, config, tracker)
        elif args.model_type == "autoencoder":
            detector, preprocessor, metrics = train_autoencoder(data_samples, validation_data, config, tracker)
        else:
            raise ValueError(f"Unsupported model type: {args.model_type}")
        
        # Save artifacts
        tracker.save_artifacts(detector, preprocessor, config, metrics)
        
        # Register with model manager
        model_name = args.model_name or f"{args.model_type}_model"
        model_manager = ModelManager(str(output_dir))
        model_id = model_manager.register_model(model_name, args.model_type, 
                                              description=f"Trained on {len(data_samples)} samples")
        model_manager.save_model(model_id, detector, str(tracker.experiment_dir / "model.joblib"))
        
        tracker.logger.info(f"Training completed successfully!")
        tracker.logger.info(f"Model ID: {model_id}")
        tracker.logger.info(f"Experiment directory: {tracker.experiment_dir}")
        
    except Exception as e:
        tracker.logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main() 