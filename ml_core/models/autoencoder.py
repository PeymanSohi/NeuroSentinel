import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AutoEncoder(nn.Module):
    """
    AutoEncoder neural network for anomaly detection.
    Learns normal patterns and flags deviations as anomalies.
    """
    
    def __init__(self, input_dim: int, hidden_dims: list = None, 
                 dropout_rate: float = 0.2, activation: str = 'relu'):
        super(AutoEncoder, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims or [input_dim // 2, input_dim // 4, input_dim // 8]
        self.dropout_rate = dropout_rate
        
        # Choose activation function
        if activation == 'relu':
            self.activation = nn.ReLU()
        elif activation == 'tanh':
            self.activation = nn.Tanh()
        elif activation == 'sigmoid':
            self.activation = nn.Sigmoid()
        else:
            self.activation = nn.ReLU()
        
        # Build encoder
        encoder_layers = []
        prev_dim = input_dim
        
        for hidden_dim in self.hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                self.activation,
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Build decoder (reverse of encoder)
        decoder_layers = []
        hidden_dims_reversed = list(reversed(self.hidden_dims))
        
        for i, hidden_dim in enumerate(hidden_dims_reversed):
            if i == 0:
                prev_dim = hidden_dim
            else:
                decoder_layers.extend([
                    nn.Linear(prev_dim, hidden_dim),
                    self.activation,
                    nn.Dropout(dropout_rate)
                ])
                prev_dim = hidden_dim
        
        # Final layer to reconstruct input
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        
        self.decoder = nn.Sequential(*decoder_layers)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through the autoencoder.
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
            
        Returns:
            Tuple of (encoded_features, reconstructed_input)
        """
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return encoded, decoded
    
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent representation."""
        return self.encoder(x)
    
    def decode(self, encoded: torch.Tensor) -> torch.Tensor:
        """Decode latent representation back to input space."""
        return self.decoder(encoded)
    
    def compute_reconstruction_error(self, x: torch.Tensor) -> torch.Tensor:
        """
        Compute reconstruction error for anomaly detection.
        
        Args:
            x: Input tensor
            
        Returns:
            Reconstruction error tensor
        """
        encoded, decoded = self.forward(x)
        return torch.mean(torch.square(x - decoded), dim=1)
    
    def predict_anomaly(self, x: torch.Tensor, threshold: float) -> torch.Tensor:
        """
        Predict if input is anomalous based on reconstruction error.
        
        Args:
            x: Input tensor
            threshold: Reconstruction error threshold
            
        Returns:
            Boolean tensor indicating anomalies
        """
        reconstruction_error = self.compute_reconstruction_error(x)
        return reconstruction_error > threshold

class AutoEncoderTrainer:
    """
    Trainer class for AutoEncoder models.
    """
    
    def __init__(self, model: AutoEncoder, learning_rate: float = 0.001, 
                 weight_decay: float = 1e-5):
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate, 
                                   weight_decay=weight_decay)
        self.criterion = nn.MSELoss()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
    def train_epoch(self, dataloader: torch.utils.data.DataLoader) -> float:
        """
        Train for one epoch.
        
        Args:
            dataloader: DataLoader for training data
            
        Returns:
            Average training loss
        """
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch in dataloader:
            if isinstance(batch, (list, tuple)):
                data = batch[0]
            else:
                data = batch
            
            data = data.to(self.device)
            
            # Forward pass
            encoded, decoded = self.model(data)
            loss = self.criterion(decoded, data)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    def validate(self, dataloader: torch.utils.data.DataLoader) -> float:
        """
        Validate the model.
        
        Args:
            dataloader: DataLoader for validation data
            
        Returns:
            Average validation loss
        """
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in dataloader:
                if isinstance(batch, (list, tuple)):
                    data = batch[0]
                else:
                    data = batch
                
                data = data.to(self.device)
                
                # Forward pass
                encoded, decoded = self.model(data)
                loss = self.criterion(decoded, data)
                
                total_loss += loss.item()
                num_batches += 1
        
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    def compute_threshold(self, dataloader: torch.utils.data.DataLoader, 
                         percentile: float = 95) -> float:
        """
        Compute anomaly threshold based on reconstruction errors.
        
        Args:
            dataloader: DataLoader for normal data
            percentile: Percentile for threshold calculation
            
        Returns:
            Threshold value
        """
        self.model.eval()
        reconstruction_errors = []
        
        with torch.no_grad():
            for batch in dataloader:
                if isinstance(batch, (list, tuple)):
                    data = batch[0]
                else:
                    data = batch
                
                data = data.to(self.device)
                error = self.model.compute_reconstruction_error(data)
                reconstruction_errors.extend(error.cpu().numpy())
        
        threshold = np.percentile(reconstruction_errors, percentile)
        logger.info(f"Computed anomaly threshold: {threshold:.6f} (percentile: {percentile})")
        return threshold
    
    def save_model(self, filepath: str):
        """Save model to file."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'model_config': {
                'input_dim': self.model.input_dim,
                'hidden_dims': self.model.hidden_dims,
                'dropout_rate': self.model.dropout_rate
            }
        }, filepath)
        logger.info(f"Saved model to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from file."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        logger.info(f"Loaded model from {filepath}") 