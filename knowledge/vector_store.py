import chromadb
from chromadb.utils import embedding_functions
import os

class OMSVectorStore:
    def __init__(self, db_path="./data/vector_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.emb_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="oms_knowledge", 
            embedding_function=self.emb_fn
        )

    def add_knowledge(self, text, metadata, doc_id):
        """Adds a document to the vector store."""
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, query_text, n_results=3):
        """Queries the vector store for relevant knowledge."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

    def seed_initial_knowledge(self):
        """Seeds the DB with basic OMS troubleshooting info."""
        knowledge_base = [
            {
                "id": "leak_001",
                "text": "Memory leak in OMS often occurs in the Order Cache if entries are not evicted properly. Symptom: monotonic increase in heap usage.",
                "meta": {"topic": "memory", "severity": "high"}
            },
            {
                "id": "cpu_001",
                "text": "High CPU usage with frequent GC usually indicates JVM heap exhaustion. Action: Increase Xmx or check for memory leaks.",
                "meta": {"topic": "cpu", "severity": "medium"}
            },
            {
                "id": "restart_001",
                "text": "Restarting the OMS service clears the ephemeral order cache and resets GC handles. Should be a last resort.",
                "meta": {"topic": "action", "severity": "low"}
            }
        ]
        
        for entry in knowledge_base:
            self.add_knowledge(entry["text"], entry["meta"], entry["id"])
        print("Vector DB seeded with initial knowledge.")

if __name__ == "__main__":
    v_store = OMSVectorStore()
    v_store.seed_initial_knowledge()
    res = v_store.query("What causes memory leaks?")
    print(f"Query Result: {res['documents']}")
