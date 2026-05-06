import matplotlib.pyplot as plt
from google.cloud import bigquery
import pandas as pd
import os

def generate_grand_report(project_id="oms-agentic-sentinel"):
    print("🎨 [Visual Agent] Generating Grand Performance Report...")
    client = bigquery.Client(project=project_id)
    
    # Query last 100 metrics
    query = f"""
        SELECT timestamp, memory_usage, cpu_usage, req_rate 
        FROM `{project_id}.oms_metrics.raw_data` 
        ORDER BY timestamp DESC LIMIT 50
    """
    
    try:
        df = client.query(query).to_dataframe()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Create Plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Memory & Requests
        ax1.plot(df['timestamp'], df['memory_usage'] / (1024**2), color='#3498db', label='Memory (MB)', linewidth=2)
        ax1.set_title('OMS Resource Trends', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Memory (MB)')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        ax1_twin = ax1.twinx()
        ax1_twin.bar(df['timestamp'], df['req_rate'], alpha=0.2, color='#e74c3c', label='Req Rate')
        ax1_twin.set_ylabel('Requests/sec')
        ax1_twin.legend(loc='upper right')

        # Plot 2: CPU Usage
        ax2.plot(df['timestamp'], df['cpu_usage'], color='#2ecc71', label='CPU Usage (%)', linewidth=2)
        ax2.set_ylabel('CPU %')
        ax2.set_xlabel('Timeline')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        report_path = "oms_performance_report.png"
        plt.savefig(report_path)
        print(f"✨ SUCCESS: Grand Report generated at {os.path.abspath(report_path)}")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")

if __name__ == "__main__":
    generate_grand_report()
