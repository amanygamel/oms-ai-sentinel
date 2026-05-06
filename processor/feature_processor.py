import pandas as pd
import numpy as np
import requests
import time

class FeatureProcessor:
    def __init__(self, prometheus_url="http://localhost:9090"):
        self.prometheus_url = prometheus_url

    def fetch_metric(self, query, duration="5m"):
        """Fetches metric data from Prometheus."""
        try:
            params = {
                'query': f'{query}[{duration}]'
            }
            response = requests.get(f"{self.prometheus_url}/api/v1/query", params=params)
            data = response.json()
            
            if data['status'] == 'success':
                results = data['data']['result']
                if results:
                    values = results[0]['values']
                    df = pd.DataFrame(values, columns=['timestamp', 'value'])
                    df['value'] = df['value'].astype(float)
                    return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching from Prometheus: {e}")
            return pd.DataFrame()

    def process_features(self, df):
        """Calculates features from raw metrics."""
        if df.empty:
            return {}

        features = {
            'current_val': df['value'].iloc[-1],
            'mean': df['value'].mean(),
            'std': df['value'].std(),
            'trend_slope': self.calculate_slope(df['value']),
            'volatility': df['value'].diff().std()
        }
        return features

    def calculate_slope(self, series):
        """Calculates the linear trend slope."""
        if len(series) < 2:
            return 0
        y = series.values
        x = np.arange(len(y))
        slope = np.polyfit(x, y, 1)[0]
        return slope

    def run(self):
        print("Feature Processor Agent started...")
        while True:
            # In a real scenario, we'd query Prometheus
            # For development, we'll log what we're doing
            mem_df = self.fetch_metric('oms_memory_usage_bytes')
            if not mem_df.empty:
                features = self.process_features(mem_df)
                print(f"Processed Features: {features}")
            else:
                print("No data found in Prometheus. Is it running?")
            
            time.sleep(10)

if __name__ == "__main__":
    processor = FeatureProcessor()
    processor.run()
