class DecisionEngine:
    def __init__(self):
        # Default policies
        self.policies = {
            "AUTO_HEAL_ENABLED": True,
            "CRITICAL_THRESHOLD": 0.8,
            "MAX_RESTARTS_PER_HOUR": 2
        }
        self.restart_history = []

    def make_decision(self, diagnostic_report, risk_level="low"):
        """Decides on the final action based on diagnostic and risk."""
        print(f"[Decision Engine] Evaluating Report: {diagnostic_report} (Risk: {risk_level})")
        
        decision = {
            "action": "IGNORE",
            "reason": "Normal behavior detected."
        }

        if "leak" in diagnostic_report.lower() or risk_level == "high":
            if self.policies["AUTO_HEAL_ENABLED"]:
                decision["action"] = "AUTO_HEAL"
                decision["reason"] = "Leak detected and Auto-Heal is enabled."
            else:
                decision["action"] = "ALERT_ONLY"
                decision["reason"] = "Leak detected but Auto-Heal is disabled."
        
        elif "potential" in diagnostic_report.lower():
            decision["action"] = "ALERT_ONLY"
            decision["reason"] = "Potential issue detected, monitoring required."

        return decision

if __name__ == "__main__":
    engine = DecisionEngine()
    d = engine.make_decision("High-confidence memory leak detected.", risk_level="high")
    print(f"Decision: {d}")
