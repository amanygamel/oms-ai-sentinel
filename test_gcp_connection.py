import os
from cloud.gcp_client import GCPClient
from agents.shadow_reasoner import ShadowReasoner

def test_connection():
    print("🔍 [GCP Test] Starting Connection Verification...\n")
    
    # 1. Project & Auth Test
    print("📡 Step 1: Testing GCP Project & Authentication...")
    gcp = GCPClient()
    if gcp.bq_client:
        print("✅ BigQuery Connection: SUCCESS")
    else:
        print("❌ BigQuery Connection: FAILED (Running in Local Mode)")

    # 2. Gemini API Test
    print("\n🧠 Step 2: Testing Gemini AI Reasoning...")
    shadow = ShadowReasoner()
    result = shadow.reason({"status": "testing"}, "Initial test query")
    
    if "Error" in result:
        print(f"❌ Gemini AI: FAILED - {result}")
    else:
        print("✅ Gemini AI: SUCCESS")
        print(f"   [Gemini Response]: {result[:100]}...")

    print("\n" + "="*40)
    if gcp.bq_client and "Error" not in result:
        print("🎉 ALL SYSTEMS GO! You are fully connected to GCP.")
    else:
        print("⚠️ Some systems are still in LOCAL mode. Check credentials/APIs.")
    print("="*40)

if __name__ == "__main__":
    test_connection()
