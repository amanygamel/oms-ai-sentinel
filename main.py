import time
import threading
from exporter.oms_exporter import OMSExporter
from knowledge.vector_store import OMSVectorStore
from models.vae_anomaly_detector import VAEAnomalyDetector
from agents.shadow_reasoner import ShadowReasoner
from agents.decision_engine import DecisionEngine
from agents.action_executor import ActionExecutor
from agents.notification_agent import NotificationAgent
from models.diffusion_predictor import DiffusionPredictor
from agents.reporting_bridge import ReportingAgent, OnPremBridge

class OMSSelfHealingPipeline:
    def __init__(self):
        # Initialize all agents
        self.exporter = OMSExporter()
        self.v_store = OMSVectorStore()
        self.detector = VAEAnomalyDetector(input_dim=5)
        self.shadow_agent = ShadowReasoner()
        self.decision_engine = DecisionEngine()
        self.action_agent = ActionExecutor()
        self.notifier = NotificationAgent()
        
        # New Advanced Agents
        self.diffusion = DiffusionPredictor()
        self.reporter = ReportingAgent(self.exporter.gcp)
        self.onprem = OnPremBridge()
        
        # Seed knowledge
        self.v_store.seed_initial_knowledge()

    def start(self):
        # Start Exporter
        threading.Thread(target=self.exporter.start, daemon=True).start()
        
        # --- THE REAL SCENARIO MASTER ---
        def scenario_master():
            print("\n🎬 [Scenario] Phase 1: Normal Operations (Morning hours)")
            time.sleep(20)
            
            print("\n🚀 [Scenario] Phase 2: FLASH SALE TRIGGERED! (Traffic Spiking...)")
            self.exporter.leak_rate = 5 * 1024 * 1024 # Small creep starts
            
            time.sleep(30)
            print("\n🚨 [Scenario] Phase 3: CRITICAL MEMORY LEAK DETECTED!")
            self.exporter.leak_rate = 100 * 1024 * 1024 # Extreme leak
            
            time.sleep(60)
            print("\n✅ [Scenario] Scenario Complete.")

        threading.Thread(target=scenario_master, daemon=True).start()
        self.run_loop()

    def run_loop(self):
        print("\n" + "="*50)
        print("🛸 HYBRID CLOUD OMS SENTINEL: ACTIVE")
        print("="*50 + "\n")
        
        while True:
            # 1. Collection
            metrics = {
                'mem_gb': self.exporter.memory_usage / (1024**3),
                'leak_rate_mb': self.exporter.leak_rate / (1024**2),
                'cpu_pct': self.exporter.OMS_CPU_USAGE._value.get() if hasattr(self.exporter, 'OMS_CPU_USAGE') else 45,
                'req_rate': self.exporter.OMS_REQUEST_RATE._value.get() if hasattr(self.exporter, 'OMS_REQUEST_RATE') else 500
            }
            
            # 2. Diffusion Failure Prediction (The 'Diffusion' part)
            failure_analysis = self.diffusion.predict_failure_probability(metrics, self.exporter.leak_rate)
            prob = failure_analysis['failure_probability']
            
            print(f"[{time.strftime('%H:%M:%S')}] Health: {100-(prob*100):.1f}% | Fail Prob: {prob:.2f} | Status: {failure_analysis['status']}")

            # 3. VAE Anomaly Detection
            features = [metrics['mem_gb'], metrics['leak_rate_mb'], 1.0 if metrics['leak_rate_mb'] > 0 else 0.0, metrics['cpu_pct']/100, 0.1]
            is_anomaly, error = self.detector.detect([features])

            if is_anomaly or prob > 0.6:
                print(f"📢 [Alert] System Instability Detected! (VAE Error: {error:.2f})")
                
                # 4. RAG & Gemini Reasoning
                query = "System trending towards failure during high request load"
                knowledge = self.v_store.query(query)['documents'][0]
                
                print("🧠 [Shadow Agent] Analyzing with Gemini...")
                reasoning = self.shadow_agent.reason(metrics, knowledge)
                print(f"💡 [AI Analysis]: {reasoning}")

                # 5. Decision & On-Prem Bridge
                decision = self.decision_engine.make_decision(reasoning, "high" if prob > 0.8 else "medium")
                
                if decision['action'] == "AUTO_HEAL":
                    # Generate Report before healing
                    report = self.reporter.generate_bq_report()
                    print(f"📊 [BI Report Summary]: Peak Mem={report['peak_memory']}, Health={report['system_health_index']}")
                    
                    # Execute via On-Prem Bridge
                    self.onprem.execute_onprem_fix("AUTO_RECOVERY_PROTOCOL", reasoning)
                    
                    self.notifier.notify(f"Self-Healing: {decision['reason']}", severity="CRITICAL")
                    self.action_agent.execute(reasoning)
                    
                    # RESETBaseline
                    self.exporter.leak_rate = 0
                    self.exporter.memory_usage = self.exporter.base_memory
                    print("♻️ [System] Baseline Restored.")
                
            time.sleep(10)

if __name__ == "__main__":
    pipeline = OMSSelfHealingPipeline()
    pipeline.start()
