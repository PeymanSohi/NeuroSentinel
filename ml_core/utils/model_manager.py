import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages model lifecycle, versioning, and deployment.
    """
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.metadata_file = self.model_dir / "metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict[str, Any]:
        """Load model metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
        return {"models": {}, "versions": {}}
    
    def _save_metadata(self):
        """Save model metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def register_model(self, model_name: str, model_type: str, 
                      version: str = None, description: str = "") -> str:
        """Register a new model."""
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_id = f"{model_name}_v{version}"
        
        if model_id in self.metadata["models"]:
            logger.warning(f"Model {model_id} already exists")
            return model_id
        
        model_info = {
            "name": model_name,
            "type": model_type,
            "version": version,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "status": "registered"
        }
        
        self.metadata["models"][model_id] = model_info
        self.metadata["versions"][model_name] = self.metadata["versions"].get(model_name, []) + [version]
        self._save_metadata()
        
        logger.info(f"Registered model: {model_id}")
        return model_id
    
    def save_model(self, model_id: str, model, filepath: str = None):
        """Save a model to disk."""
        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not registered")
        
        if filepath is None:
            filepath = self.model_dir / f"{model_id}.joblib"
        
        try:
            if hasattr(model, 'save'):
                model.save(str(filepath))
            else:
                import joblib
                joblib.dump(model, filepath)
            
            # Update metadata
            self.metadata["models"][model_id]["filepath"] = str(filepath)
            self.metadata["models"][model_id]["status"] = "saved"
            self.metadata["models"][model_id]["updated_at"] = datetime.now().isoformat()
            self._save_metadata()
            
            logger.info(f"Saved model {model_id} to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving model {model_id}: {e}")
            raise
    
    def load_model(self, model_id: str):
        """Load a model from disk."""
        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not registered")
        
        model_info = self.metadata["models"][model_id]
        filepath = model_info.get("filepath")
        
        if not filepath or not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        try:
            import joblib
            model = joblib.load(filepath)
            logger.info(f"Loaded model {model_id} from {filepath}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {e}")
            raise
    
    def deploy_model(self, model_id: str, environment: str = "production"):
        """Deploy a model to a specific environment."""
        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not registered")
        
        # Update metadata
        self.metadata["models"][model_id]["deployed_at"] = datetime.now().isoformat()
        self.metadata["models"][model_id]["environment"] = environment
        self.metadata["models"][model_id]["status"] = "deployed"
        self._save_metadata()
        
        logger.info(f"Deployed model {model_id} to {environment}")
    
    def list_models(self, model_name: str = None) -> List[Dict[str, Any]]:
        """List all models or models with specific name."""
        models = []
        for model_id, info in self.metadata["models"].items():
            if model_name is None or info["name"] == model_name:
                models.append({"id": model_id, **info})
        return models
    
    def get_latest_version(self, model_name: str) -> Optional[str]:
        """Get the latest version of a model."""
        versions = self.metadata["versions"].get(model_name, [])
        if versions:
            return versions[-1]
        return None
    
    def delete_model(self, model_id: str):
        """Delete a model and its files."""
        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not registered")
        
        model_info = self.metadata["models"][model_id]
        filepath = model_info.get("filepath")
        
        # Delete model file
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info(f"Deleted model file: {filepath}")
            except Exception as e:
                logger.error(f"Error deleting model file: {e}")
        
        # Remove from metadata
        model_name = model_info["name"]
        version = model_info["version"]
        
        del self.metadata["models"][model_id]
        
        # Remove version from versions list
        if model_name in self.metadata["versions"]:
            self.metadata["versions"][model_name] = [
                v for v in self.metadata["versions"][model_name] if v != version
            ]
            if not self.metadata["versions"][model_name]:
                del self.metadata["versions"][model_name]
        
        self._save_metadata()
        logger.info(f"Deleted model: {model_id}")
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get detailed information about a model."""
        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not registered")
        
        return self.metadata["models"][model_id].copy()
    
    def update_model_info(self, model_id: str, updates: Dict[str, Any]):
        """Update model information."""
        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not registered")
        
        self.metadata["models"][model_id].update(updates)
        self.metadata["models"][model_id]["updated_at"] = datetime.now().isoformat()
        self._save_metadata()
        
        logger.info(f"Updated model info: {model_id}") 