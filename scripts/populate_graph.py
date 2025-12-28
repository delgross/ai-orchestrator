import requests
import json
import time

RAG_URL = "http://localhost:5555"

def populate():
    print("Populating Graph...")
    
    # define some nodes
    entities = [
        {"name": "Dr_Ed", "type": "Person", "description": "The user, a retired radiologist."},
        {"name": "Farm", "type": "Location", "description": "The user's residence and farm."},
        {"name": "Starlink", "type": "Technology", "description": "Primary internet connection."},
        {"name": "Omada", "type": "Technology", "description": "Network infrastructure."},
        {"name": "Agent_Zero", "type": "AI", "description": "The orchestrator agent."},
        {"name": "SurrealDB", "type": "Software", "description": "Memory database."},
        {"name": "Dashboard", "type": "Software", "description": "Frontend interface."}
    ]
    
    relations = [
        {"source": "Dr_Ed", "target": "Farm", "relation": "lives_at", "description": "Ed lives at the farm"},
        {"source": "Farm", "target": "Starlink", "relation": "uses", "description": "Farm uses Starlink for internet"},
        {"source": "Farm", "target": "Omada", "relation": "has_infrastructure", "description": "Farm has Omada network"},
        {"source": "Agent_Zero", "target": "SurrealDB", "relation": "stores_memory_in", "description": "Agent saves data to Surreal"},
        {"source": "Dashboard", "target": "Agent_Zero", "relation": "interacts_with", "description": "Dashboard controls Agent"},
        {"source": "Dr_Ed", "target": "Agent_Zero", "relation": "uses", "description": "Ed uses the Agent"},
    ]
    
    payload = {
        "origin_file": "manual_seed",
        "entities": entities,
        "relations": relations
    }
    
    try:
        r = requests.post(f"{RAG_URL}/ingest/graph", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    populate()
