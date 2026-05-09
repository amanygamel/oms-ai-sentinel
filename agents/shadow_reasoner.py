import os
import vertexai
from vertexai.generative_models import GenerativeModel

class ShadowReasoner:
    def __init__(self, project_id=None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "your-project-id")
        
        try:
            # Explicitly initialize Vertex AI
            vertexai.init(project=self.project_id, location="us-central1")
            # Use the more universal alias
            self.model = GenerativeModel("gemini-1.5-flash")
            print("🚀 Shadow Agent: Online via Vertex AI (Gemini)")
        except Exception as e:
            print(f"⚠️ Shadow Agent Init Error: {e}")
            self.model = None

    def reason(self, metrics, retrieved_context):
        if not self.model:
            return self._simulated_reason(metrics)

        prompt = f"""
        OMS Incident Analysis Request:
        -----------------------------
        Real-time Metrics: {metrics}
        Known Patterns: {retrieved_context}
        
        Task: 
        1. Identify the root cause.
        2. Explain the impact.
        3. Provide a clear recommendation (e.g., RESTART, SCALE, IGNORE).
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error in AI Reasoning: {e}"

    def _simulated_reason(self, metrics):
        return "ROOT CAUSE: Analysis in progress (Local Simulation)."
