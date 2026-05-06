import streamlit as st
import pandas as pd
import time
from google.cloud import bigquery
import plotly.express as px

# Page Config
st.set_page_config(page_title="OMS Sentinel Dashboard", layout="wide", page_icon="🛸")

st.title("🛸 OMS Sentinel: AI-Driven Command Center")
st.markdown("---")

# GCP Config
PROJECT_ID = "oms-agentic-sentinel"
client = bigquery.Client(project=PROJECT_ID)

# Placeholders for metrics
col1, col2, col3 = st.columns(3)
health_metric = col1.empty()
fail_prob_metric = col2.empty()
status_metric = col3.empty()

# Main UI layout
chart_col, log_col = st.columns([2, 1])

with chart_col:
    st.subheader("📈 Real-time System Metrics")
    memory_chart = st.empty()
    cpu_chart = st.empty()

with log_col:
    st.subheader("🧠 AI Diagnosis & Insights")
    ai_log = st.empty()
    st.subheader("🚨 Incident History")
    incident_log = st.empty()

def fetch_data():
    query = f"""
        SELECT timestamp, memory_usage, cpu_usage, req_rate 
        FROM `{PROJECT_ID}.oms_metrics.raw_data` 
        ORDER BY timestamp DESC LIMIT 100
    """
    df = client.query(query).to_dataframe()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.sort_values('timestamp')

# Loop to refresh dashboard
while True:
    try:
        data = fetch_data()
        latest = data.iloc[-1]
        
        # Calculate scores
        mem_gb = latest['memory_usage'] / (1024**3)
        health = max(0, 100 - (mem_gb * 10))
        
        # Update metrics
        health_metric.metric("System Health", f"{health:.1f}%", delta=None)
        fail_prob_metric.metric("Failure Prob", f"{(100-health)/100:.2f}", delta=None, delta_color="inverse")
        status_metric.metric("Status", "STABLE" if health > 70 else "CRITICAL")

        # Update Charts
        with chart_col:
            fig_mem = px.line(data, x='timestamp', y='memory_usage', title="Memory Usage Trend", template="plotly_dark")
            memory_chart.plotly_chart(fig_mem, width='stretch')
            
            fig_cpu = px.line(data, x='timestamp', y='cpu_usage', title="CPU Workload", template="plotly_dark")
            cpu_chart.plotly_chart(fig_cpu, width='stretch')

        # In a real app, AI logs would be fetched from a table too
        with log_col:
            ai_log.info(f"**Latest AI Analysis:**\nMemory trend shows growth. Root cause: Potential leak in order_service.")
            incident_log.warning(f"Incident: High Memory at {latest['timestamp'].strftime('%H:%M:%S')}. Action: Auto-Heal Triggered.")

    except Exception as e:
        st.error(f"Waiting for data... ({e})")
        
    time.sleep(5)
