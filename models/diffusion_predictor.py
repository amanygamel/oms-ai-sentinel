import numpy as np

class DiffusionPredictor:
    def __init__(self):
        self.noise_schedule = np.linspace(0.0001, 0.02, 1000)
        
    def predict_failure_probability(self, current_metrics, trend_slope):
        """
        Uses a diffusion-inspired probabilistic approach to estimate 
        the probability of system exhaustion (Failure Score).
        """
        # Normalize metrics
        mem_load = current_metrics.get('mem_gb', 0) / 8.0 # Assuming 8GB limit
        slope_factor = trend_slope / (100 * 1024 * 1024) # Normalize 100MB/tick
        
        # Base probability from VAE or current state
        base_prob = (mem_load * 0.4) + (slope_factor * 0.6)
        
        # Add 'diffusion noise' to simulate uncertainty in the environment
        noise = np.random.choice(self.noise_schedule)
        prob_with_uncertainty = base_prob + (noise * 10)
        
        # Failure Probability (0.0 to 1.0)
        final_score = np.clip(prob_with_uncertainty, 0, 1)
        
        status = "STABLE"
        if final_score > 0.8: status = "CRITICAL - IMMINENT FAILURE"
        elif final_score > 0.5: status = "WARNING - TRENDING TO FAILURE"
        
        return {
            "failure_probability": float(final_score),
            "status": status,
            "time_to_exhaustion": f"{max(1, (8 - current_metrics.get('mem_gb', 0)) / (trend_slope/1024**3 + 0.001)):.1f} cycles"
        }

if __name__ == "__main__":
    predictor = DiffusionPredictor()
    print(predictor.predict_failure_probability({'mem_gb': 6.5}, 50 * 1024 * 1024))
