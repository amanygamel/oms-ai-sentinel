import time
import random
import numpy as np
from prometheus_client import start_http_server, Gauge
from cloud.gcp_client import GCPClient

# Define metrics
OMS_MEMORY_USAGE = Gauge('oms_memory_usage_bytes', 'Current memory usage of the OMS in bytes')
OMS_CPU_USAGE = Gauge('oms_cpu_usage_percent', 'Current CPU usage of the OMS in percent')
OMS_ORDER_COUNT = Gauge('oms_order_processed_total', 'Total number of orders processed')
OMS_GC_TIME = Gauge('oms_gc_time_seconds', 'Time spent in Garbage Collection')
OMS_REQUEST_RATE = Gauge('oms_request_rate_per_second', 'Inbound request rate')
OMS_DISK_USAGE = Gauge('oms_disk_usage_percent', 'Disk usage percentage')
OMS_NETWORK_TRAFFIC = Gauge('oms_network_traffic_bytes', 'Network traffic in bytes')

class OMSExporter:
    def __init__(self, port=8000):
        self.port = port
        self.base_memory = 512 * 1024 * 1024  # 512MB
        self.leak_rate = 0
        self.memory_usage = self.base_memory
        self.gcp = GCPClient()

    def simulate_metrics(self):
        """Simulates OMS metrics with a realistic daily cycle pattern."""
        print("Starting Realistic Workload Simulation...")
        while True:
            # Get current hour to simulate daily cycle
            current_hour = time.localtime().tm_hour
            # Sinusoidal wave: peaks at 14:00 (2 PM), lowest at 02:00 (2 AM)
            # Normalizes to 0.0 - 1.0
            cycle_factor = (np.sin((current_hour - 8) * (2 * np.pi / 24)) + 1) / 2
            
            # 1. CPU Usage: Base 10% + (Up to 70% based on cycle) + Random Noise
            cpu = 10 + (cycle_factor * 70) + random.uniform(-5, 5)
            OMS_CPU_USAGE.set(max(5, cpu))

            # 2. Request Rate: Base 50 + (Up to 1000 based on cycle)
            req_rate = 50 + (cycle_factor * 1000) + random.randint(-20, 20)
            OMS_REQUEST_RATE.set(max(10, req_rate))

            # 3. Memory Usage: Base 512MB + (Scale with req_rate) + LEAK + Noise
            # Each request consumes ~0.5MB in cache
            target_memory = self.base_memory + (req_rate * 0.5 * 1024 * 1024)
            
            # Smoothly transition to target memory
            diff = target_memory - self.memory_usage
            self.memory_usage += (diff * 0.1) + self.leak_rate + random.uniform(-1, 1) * 1024 * 1024
            
            if self.memory_usage < self.base_memory:
                self.memory_usage = self.base_memory
            OMS_MEMORY_USAGE.set(self.memory_usage)

            # 4. GC Time: Increases with CPU and Memory pressure
            gc_time = (cpu * 0.02) + (self.memory_usage / (1024**3) * 0.1) + random.uniform(0, 0.05)
            OMS_GC_TIME.set(gc_time)

            # 5. Disk & Network
            OMS_DISK_USAGE.set(42 + random.uniform(-0.5, 0.5))
            OMS_NETWORK_TRAFFIC.set(req_rate * 50 * 1024) # 50KB per request

            # Stream to BigQuery
            self.gcp.stream_metrics_to_bq("oms_metrics", "raw_data", [{
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
                "memory_usage": self.memory_usage,
                "cpu_usage": cpu,
                "gc_time": gc_time,
                "req_rate": req_rate
            }])

            print(f"[{time.strftime('%H:%M:%S')}] Metrics: CPU={cpu:.1f}%, MEM={self.memory_usage/(1024**2):.1f}MB, REQS={req_rate:.0f}/s")
            time.sleep(5)

    def trigger_leak(self, rate=10 * 1024 * 1024): # 10MB per tick
        """Increases the memory leak rate."""
        print(f"!!! Triggering Memory Leak: {rate / (1024*1024):.2f} MB/tick !!!")
        self.leak_rate = rate

    def start(self):
        print(f"Starting Exporter on port {self.port}...")
        start_http_server(self.port)
        self.simulate_metrics()

if __name__ == "__main__":
    exporter = OMSExporter()
    
    # In a real scenario, the leak would be triggered by an external event
    # For simulation, we'll start a leak after 60 seconds
    import threading
    def leak_timer():
        time.sleep(60)
        exporter.trigger_leak()
    
    threading.Thread(target=leak_timer, daemon=True).start()
    exporter.start()
