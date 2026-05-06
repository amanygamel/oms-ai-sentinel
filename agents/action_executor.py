import time

class ActionExecutor:
    def __init__(self):
        pass

    def execute(self, diagnostic_report):
        """Parses the report and takes action."""
        print(f"\n[Action Agent] Received Report: {diagnostic_report}")
        
        if "Trigger Heap Dump" in diagnostic_report:
            self.take_heap_dump()
        
        if "prepare for restart" in diagnostic_report:
            self.restart_service()
            
        if "Monitor closely" in diagnostic_report:
            print("[Action Agent] Increasing monitoring frequency...")

    def take_heap_dump(self):
        print("[Action Agent] EXECUTION: Generating JVM Heap Dump for analysis...")
        time.sleep(2)
        print("[Action Agent] SUCCESS: Heap dump saved to /data/dumps/oms_leak.hprof")

    def restart_service(self):
        print("[Action Agent] EXECUTION: Gracefully restarting OMS service...")
        time.sleep(3)
        print("[Action Agent] SUCCESS: OMS service restarted and healthy.")

if __name__ == "__main__":
    executor = ActionExecutor()
    executor.execute("DIAGNOSTIC: Leak detected. ACTION: Trigger Heap Dump and prepare for restart.")
