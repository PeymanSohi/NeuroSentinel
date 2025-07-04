import torch
from ml_core.models import SimpleAnomalyDetector

def train_model(data_loader, input_dim):
    model = SimpleAnomalyDetector(input_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = torch.nn.BCELoss()
    for epoch in range(10):
        for x, y in data_loader:
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
    return model
