import torch
import numpy as np
try:
    from ml_core.models.autoencoder import AutoEncoder
except ImportError:
    from models.autoencoder import AutoEncoder

class AutoEncoderDetector:
    def __init__(self, model: AutoEncoder, threshold: float = None, device: str = None):
        self.model = model
        self.threshold = threshold
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def fit(self, dataloader, trainer, epochs=10):
        for epoch in range(epochs):
            loss = trainer.train_epoch(dataloader)
        # Optionally compute threshold after training
        self.threshold = trainer.compute_threshold(dataloader)

    def predict(self, X: np.ndarray):
        self.model.eval()
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            _, decoded = self.model(X_tensor)
            errors = torch.mean((X_tensor - decoded) ** 2, dim=1).cpu().numpy()
        if self.threshold is not None:
            return (errors > self.threshold).astype(int)
        return errors

    def anomaly_score(self, X: np.ndarray):
        self.model.eval()
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            _, decoded = self.model(X_tensor)
            errors = torch.mean((X_tensor - decoded) ** 2, dim=1).cpu().numpy()
        return errors

    def save(self, filepath: str):
        torch.save(self.model.state_dict(), filepath)

    def load(self, filepath: str):
        self.model.load_state_dict(torch.load(filepath, map_location=self.device))
        self.model.to(self.device) 