import os
import time
import json
import numpy as np
import faiss
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from litellm import embedding
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
LOG_FILE = "mysql_connection.log"
DIMENSION = 1536  # Standard for OpenAI/Gemini embeddings
MODEL = os.getenv("LLM_MODEL", "ollama/llama3.2")

# 1. Initialize Drain3 for Log Mining
config = TemplateMinerConfig()
# In production, you would configure specific regexes here for IP addresses, IDs, etc.
template_miner = TemplateMiner(config=config)

# 2. Initialize FAISS for Vector Search
index = faiss.IndexFlatL2(DIMENSION)
template_store = []  # Maps FAISS ID -> {template_id: X, template_text: "..."}

def get_embedding(text):
    """Fetches embedding for a single string."""
    try:
        # Use litellm for generic provider support
        # Note: In production, use a dedicated embedding model (e.g. text-embedding-3-small)
        response = embedding(model=MODEL, input=[text])
        return np.array(response.data[0]['embedding']).astype('float32')
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def process_log_line(line):
    global index, template_store
    
    # Step A: Extract Template (Log Mining)
    result = template_miner.add_log_message(line)
    template_id = result["cluster_id"]
    template_content = result["template_mined"]
    
    # Step B: Check if this is a NEW template
    # result["change_type"] will be "cluster_created" or "cluster_template_changed"
    if result["change_type"] == "cluster_created":
        print(f"New Template Found [ID:{template_id}]: {template_content}")
        
        # Step C: Embed only the UNIQUE template
        vector = get_embedding(template_content)
        if vector is not None:
            index.add(np.array([vector]))
            template_store.append({
                "id": template_id,
                "text": template_content,
                "occurrence_count": 1
            })
    else:
        # Just increment the count for an existing template
        for t in template_store:
            if t["id"] == template_id:
                t["occurrence_count"] += 1
                break

def tail_log(filename):
    """Simulates 'tail -f' to process logs as they arrive."""
    with open(filename, "r") as f:
        # Start by reading existing logs to build the initial state
        for line in f:
            process_log_line(line.strip())
            
        # Then wait for new logs
        print("\n--- Initial indexing complete. Monitoring for new logs... ---\n")
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            process_log_line(line.strip())

def main():
    if not os.path.exists(LOG_FILE):
        print(f"Error: {LOG_FILE} not found. Run 'python3 log_generator.py' first.")
        return

    try:
        tail_log(LOG_FILE)
    except KeyboardInterrupt:
        print("\nSaving state and exiting...")
        # In a real system, you would save the FAISS index and Drain3 state here
        print(f"Final Report: Discovered {len(template_store)} unique log templates.")
        for t in template_store:
            print(f" - [{t['occurrence_count']} times]: {t['text']}")

if __name__ == "__main__":
    main()
