import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class VAE(nn.Module):
    def __init__(self, input_dim, latent_dim=2):
        super(VAE, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU()
        )
        
        self.fc_mu = nn.Linear(8, latent_dim)
        self.fc_logvar = nn.Linear(8, latent_dim)
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 8),
            nn.ReLU(),
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim),
            nn.Sigmoid() # Normalize output between 0 and 1
        )

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        h = self.encoder(x)
        mu, logvar = self.fc_mu(h), self.fc_logvar(h)
        z = self.reparameterize(mu, logvar)
        return self.decoder(z), mu, logvar

def vae_loss_function(recon_x, x, mu, logvar):
    BCE = nn.functional.mse_loss(recon_x, x, reduction='sum')
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return BCE + KLD

class VAEAnomalyDetector:
    def __init__(self, input_dim=5):
        self.model = VAE(input_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=1e-3)
        self.threshold = 0.1 # Default threshold

    def train_step(self, data):
        self.model.train()
        data = torch.FloatTensor(data)
        self.optimizer.zero_grad()
        recon_batch, mu, logvar = self.model(data)
        loss = vae_loss_function(recon_batch, data, mu, logvar)
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def detect(self, data):
        self.model.eval()
        with torch.no_grad():
            data = torch.FloatTensor(data)
            recon, mu, logvar = self.model(data)
            error = torch.mean((recon - data)**2).item()
            is_anomaly = error > self.threshold
            return is_anomaly, error

if __name__ == "__main__":
    # Test simulation
    detector = VAEAnomalyDetector(input_dim=5)
    mock_data = np.random.rand(1, 5)
    
    print("Training on mock data...")
    for _ in range(100):
        detector.train_step(mock_data)
        
    is_anomaly, error = detector.detect(mock_data)
    print(f"Test Detect: Anomaly={is_anomaly}, Error={error:.4f}")
