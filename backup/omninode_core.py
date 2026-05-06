import os
import time
import qrcode
import cv2
import chromadb
from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# --- [ CONFIGURATION ] ---
DB_PATH = "./omninode_v3_db"

# --- [ STATE DEFINITION ] ---
class AgentState(TypedDict):
    item_id: str
    environment: str
    category: str
    manual: str
    user_question: str
    agent_response: str
    next_step: str  # solve, ask_more, escalate

# --- [ DATABASE HELPERS ] ---
def get_db():
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(name="universal_knowledge")

# --- [ LANGGRAPH NODES ] ---

def analyze_node(state: AgentState):
    """
    The Brain: Analyzes the manual vs the user question.
    """
    print(f"\n[AGENT] Analyzing {state['item_id']} in {state['environment']}...")
    
    # We use a Prompt Template to force strict reasoning
    template = """You are a Diagnostic Agent. 
Environment: {env} | Category: {cat} | Item: {id}
Manual Content: {manual}

User Question: {question}

TASK: 
1. If the manual has a clear answer, set NEXT_STEP to 'solve'.
2. If the question is vague, set NEXT_STEP to 'ask_more'.
3. If the issue is NOT in the manual, set NEXT_STEP to 'escalate'.

Your response MUST start with the NEXT_STEP on the first line.
"""
    # For this version, we simulate the LLM decision if no API Key is found
    if "GOOGLE_API_KEY" not in os.environ:
        # Simple simulation logic
        if "help" in state['user_question'].lower() or "?" in state['user_question']:
            next_step = "ask_more"
            response = "I need more details about the symptoms you see."
        elif any(word in state['manual'].lower() for word in state['user_question'].lower().split()):
            next_step = "solve"
            response = "Based on the manual, you should follow the reboot procedure."
        else:
            next_step = "escalate"
            response = "This issue is not in my database. Escalating to human admin."
    else:
        # Real Gemini Call would go here
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        # (Simplified for this script)
        next_step = "solve" 
        response = "Real AI Response would go here."

    return {"agent_response": response, "next_step": next_step}

def solve_node(state: AgentState):
    print("🟢 [DECISION] Providing Solution...")
    return {"agent_response": f"SOLVED: {state['agent_response']}"}

def ask_more_node(state: AgentState):
    print("🟡 [DECISION] Asking for more info...")
    return {"agent_response": f"CLARIFY: {state['agent_response']}"}

def escalate_node(state: AgentState):
    print("🔴 [DECISION] ESCALATING to Human...")
    return {"agent_response": f"ALERT: {state['agent_response']}"}

# --- [ BUILDING THE GRAPH ] ---
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("analyze", analyze_node)
workflow.add_node("solve", solve_node)
workflow.add_node("ask_more", ask_more_node)
workflow.add_node("escalate", escalate_node)

# Add Edges (Routing)
workflow.set_entry_point("analyze")

def router(state):
    return state["next_step"]

workflow.add_conditional_edges(
    "analyze",
    router,
    {
        "solve": "solve",
        "ask_more": "ask_more",
        "escalate": "escalate"
    }
)

workflow.add_edge("solve", END)
workflow.add_edge("ask_more", END)
workflow.add_edge("escalate", END)

app_graph = workflow.compile()

# --- [ APP LOGIC ] ---

def ingest():
    print("\n--- [ INGESTION ] ---")
    env = input("Environment: ")
    cat = input("Category: ")
    id = input("Item ID: ")
    manual = input("Manual/Issues: ")
    
    collection = get_db()
    collection.upsert(ids=[id], documents=[manual], metadatas=[{"env": env, "cat": cat}])
    
    # QR Code
    qr_file = f"{id}_qr.png"
    img = qrcode.make(id)
    img.save(qr_file)
    print(f"[OK] Saved {id} and generated {qr_file}")

def scan():
    print("\n--- [ SCAN ] ---")
    file = input("QR File: ")
    if not os.path.exists(file): return
    
    img = cv2.imread(file)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    
    if data:
        print(f"[SCAN] Found ID: {data}")
        collection = get_db()
        res = collection.get(ids=[data])
        if res['documents']:
            manual = res['documents'][0]
            meta = res['metadatas'][0]
            
            print(f"\n[INFO] {meta['env']} > {meta['cat']} > {data}")
            question = input("Describe the problem: ")
            
            # Run LangGraph!
            inputs = {
                "item_id": data,
                "environment": meta['env'],
                "category": meta['cat'],
                "manual": manual,
                "user_question": question
            }
            for output in app_graph.stream(inputs):
                for key, value in output.items():
                    if "agent_response" in value:
                        print(f"\nResult: {value['agent_response']}")
        else:
            print("Not in DB.")

if __name__ == "__main__":
    while True:
        print("\n--- OmniNode Universal v3 ---")
        print("1. Ingest Asset")
        print("2. Scan & Diagnose (LangGraph)")
        print("3. Exit")
        choice = input("Choice: ")
        if choice == '1': ingest()
        elif choice == '2': scan()
        else: break
