from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import logging
try:
    from ml_core.detectors import IsolationForestDetector, AutoEncoderDetector
    from ml_core.preprocessing import DataPreprocessor
    from ml_core.utils import AnomalyScorer, ModelManager
    from ml_core.models import AutoEncoder
except ImportError:
    from detectors import IsolationForestDetector, AutoEncoderDetector
    from preprocessing import DataPreprocessor
    from utils import AnomalyScorer, ModelManager
    from models import AutoEncoder
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NeuroSentinel ML Core", version="1.0.0")

# Global instances
model_manager = ModelManager()
anomaly_scorer = AnomalyScorer()

class TrainingRequest(BaseModel):
    model_type: str  # "isolation_forest" or "autoencoder"
    data: List[Dict[str, Any]]
    config: Dict[str, Any] = {}

class PredictionRequest(BaseModel):
    data: Dict[str, Any]
    model_id: str = None

@app.get("/")
def root():
    return {"message": "NeuroSentinel ML Core is running."}

@app.get("/health")
def health():
    return {"status": "ok", "models": len(model_manager.list_models())}

@app.post("/train")
async def train_model(request: TrainingRequest):
    """Train a new anomaly detection model."""
    try:
        # Preprocess data
        preprocessor = DataPreprocessor()
        preprocessor.fit_scalers(request.data)
        
        # Extract features
        feature_vectors = []
        for sample in request.data:
            features = preprocessor.extract_features(sample)
            X = preprocessor.normalize_features(features)
            if X.size > 0:
                feature_vectors.append(X.flatten())
        
        if not feature_vectors:
            raise HTTPException(status_code=400, detail="No valid features extracted")
        
        X_train = np.array(feature_vectors)
        
        # Create and train model
        if request.model_type == "isolation_forest":
            detector = IsolationForestDetector(**request.config.get("params", {}))
            detector.fit(X_train)
            model_name = "isolation_forest"
            
        elif request.model_type == "autoencoder":
            input_dim = X_train.shape[1]
            model = AutoEncoder(input_dim=input_dim, **request.config.get("model_params", {}))
            detector = AutoEncoderDetector(model, **request.config.get("detector_params", {}))
            # Note: AutoEncoder training would need a proper dataloader
            model_name = "autoencoder"
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model type: {request.model_type}")
        
        # Register and save model
        model_id = model_manager.register_model(model_name, request.model_type)
        model_manager.save_model(model_id, detector)
        
        return {"model_id": model_id, "status": "trained", "features": X_train.shape[1]}
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict_anomaly(request: PredictionRequest):
    """Predict anomaly for given data."""
    try:
        if request.model_id is None:
            # Use latest model
            models = model_manager.list_models()
            if not models:
                raise HTTPException(status_code=404, detail="No models available")
            request.model_id = models[-1]["id"]
        
        # Load model
        detector = model_manager.load_model(request.model_id)
        
        # Preprocess data
        preprocessor = DataPreprocessor()
        features = preprocessor.extract_features(request.data)
        X = preprocessor.normalize_features(features)
        
        if X.size == 0:
            raise HTTPException(status_code=400, detail="No valid features extracted")
        
        # Predict
        if hasattr(detector, 'anomaly_score'):
            score = detector.anomaly_score(X)
            is_anomalous = score > request.config.get("threshold", 0.5)
        else:
            prediction = detector.predict(X)
            is_anomalous = prediction[0] == -1  # IsolationForest convention
        
        return {
            "model_id": request.model_id,
            "is_anomalous": bool(is_anomalous),
            "anomaly_score": float(score[0]) if 'score' in locals() else None
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List all available models."""
    return {"models": model_manager.list_models()}

@app.get("/models/{model_id}")
async def get_model_info(model_id: str):
    """Get information about a specific model."""
    try:
        return model_manager.get_model_info(model_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)