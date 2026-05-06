from cloud.gcp_client import GCPClient

class BQFeatureEngineer:
    def __init__(self):
        self.gcp = GCPClient()

    def get_historical_trend(self, metric_name, window_hours=24):
        """Queries BigQuery for historical trends."""
        query = f"""
            SELECT AVG(value) as avg_val, STDDEV(value) as std_val
            FROM `oms_metrics.raw_data`
            WHERE metric = '{metric_name}' 
            AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {window_hours} HOUR)
        """
        
        if not self.gcp.bq_client:
            # Simulated historical data
            return {"avg_val": 1024*1024*512, "std_val": 1024*1024*50}
        
        try:
            query_job = self.gcp.bq_client.query(query)
            results = query_job.result()
            for row in results:
                return dict(row)
        except Exception as e:
            print(f"BQ Query Error: {e}")
            return {"avg_val": 0, "std_val": 0}

if __name__ == "__main__":
    fe = BQFeatureEngineer()
    trend = fe.get_historical_trend("memory_usage")
    print(f"Historical Trend: {trend}")
