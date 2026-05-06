import time

class NotificationAgent:
    def __init__(self):
        self.channels = ["SLACK", "EMAIL", "TELEGRAM"]

    def notify(self, message, severity="INFO"):
        """Sends a notification to all configured channels."""
        print(f"\n[Notification Agent] !!! {severity} ALERT !!!")
        for channel in self.channels:
            self._send_to_channel(channel, message)

    def _send_to_channel(self, channel, message):
        # In a real setup, we'd use requests to hit a webhook
        print(f"[Notification Agent] Sending to {channel}: {message}")
        time.sleep(0.1)

if __name__ == "__main__":
    notifier = NotificationAgent()
    notifier.notify("Memory Leak detected on OMS-01", severity="CRITICAL")
