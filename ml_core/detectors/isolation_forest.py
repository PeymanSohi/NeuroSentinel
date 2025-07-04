from sklearn.ensemble import IsolationForest
import numpy as np
import joblib

class IsolationForestDetector:
    def __init__(self, n_estimators=100, contamination=0.05, random_state=42):
        self.model = IsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=random_state)
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        self.model.fit(X)
        self.is_fitted = True

    def predict(self, X: np.ndarray):
        if not self.is_fitted:
            raise RuntimeError("IsolationForest model is not fitted.")
        return self.model.predict(X)

    def anomaly_score(self, X: np.ndarray):
        if not self.is_fitted:
            raise RuntimeError("IsolationForest model is not fitted.")
        # Lower scores are more anomalous
        return -self.model.decision_function(X)

    def save(self, filepath: str):
        joblib.dump(self.model, filepath)

    def load(self, filepath: str):
        self.model = joblib.load(filepath)
        self.is_fitted = True 