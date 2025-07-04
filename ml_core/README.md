# NeuroSentinel ML Core

The ML Core module provides machine learning-based anomaly detection capabilities for the NeuroSentinel cyber defense platform.

## Overview

This module implements two main anomaly detection approaches:

1. **IsolationForest**: A tree-based ensemble method for detecting outliers in tabular data
2. **AutoEncoder**: A neural network-based approach that learns normal patterns and flags deviations

## Components

### 1. Preprocessing (`preprocessing/`)
- **DataPreprocessor**: Extracts features from system monitoring data and normalizes them
- Handles feature extraction from system, process, network, file, user, security, container, and threat intelligence data
- Supports scaling, encoding, and sequence feature creation

### 2. Models (`models/`)
- **AutoEncoder**: PyTorch-based neural network for anomaly detection
- **AutoEncoderTrainer**: Training utilities for AutoEncoder models
- Supports configurable architectures with different activation functions and dropout

### 3. Detectors (`detectors/`)
- **IsolationForestDetector**: Wrapper around scikit-learn's IsolationForest
- **AutoEncoderDetector**: Wrapper around AutoEncoder models for anomaly detection
- Both provide unified interfaces for training, prediction, and scoring

### 4. Utilities (`utils/`)
- **AnomalyScorer**: Combines multiple detectors with weighted scoring
- **ModelManager**: Handles model lifecycle, versioning, and deployment

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from ml_core.detectors import IsolationForestDetector
from ml_core.preprocessing import DataPreprocessor

# Create preprocessor
preprocessor = DataPreprocessor()

# Extract features from system data
features = preprocessor.extract_features(system_data)
X = preprocessor.normalize_features(features)

# Create and train detector
detector = IsolationForestDetector(n_estimators=100, contamination=0.05)
detector.fit(X)

# Predict anomalies
anomaly_score = detector.anomaly_score(X)
is_anomalous = detector.predict(X)
```

### Training Models

Use the training script to train models on your data:

```bash
# Train IsolationForest
python train_models.py --data training_data.json --model-type isolation_forest

# Train AutoEncoder
python train_models.py --data training_data.json --model-type autoencoder --config config.json
```

### API Usage

Start the ML Core API server:

```bash
python main.py
```

The API provides endpoints for:
- `POST /train`: Train new models
- `POST /predict`: Predict anomalies
- `GET /models`: List available models
- `GET /models/{model_id}`: Get model information

## Configuration

### IsolationForest Configuration

```json
{
  "params": {
    "n_estimators": 100,
    "contamination": 0.05,
    "random_state": 42
  }
}
```

### AutoEncoder Configuration

```json
{
  "model_params": {
    "hidden_dims": [64, 32, 16],
    "dropout_rate": 0.2,
    "activation": "relu"
  },
  "trainer_params": {
    "learning_rate": 0.001,
    "weight_decay": 1e-5
  },
  "detector_params": {
    "threshold": null
  },
  "batch_size": 32,
  "epochs": 10,
  "threshold_percentile": 95
}
```

## Testing

Run the test suite to verify all components:

```bash
python test_models.py
```

## Integration with Agent

To integrate anomaly detection with the agent:

1. Train models on normal system data
2. Save models using ModelManager
3. Load models in the agent
4. Apply anomaly detection to collected data
5. Report anomalies to the central server

## Features

- **Feature Extraction**: Comprehensive feature extraction from system monitoring data
- **Multiple Algorithms**: Support for both statistical and deep learning approaches
- **Model Management**: Versioning, deployment, and lifecycle management
- **API Interface**: RESTful API for training and inference
- **Scalability**: Designed for distributed deployment
- **Extensibility**: Easy to add new detection algorithms

## Dependencies

- numpy
- pandas
- scikit-learn
- torch
- joblib
- fastapi
- uvicorn

## License

See the main project license. 