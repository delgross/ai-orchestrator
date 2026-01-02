
import os
import argparse
from pathlib import Path

def trigger_processing(target_dir: str):
    """
    Creates a .trigger_now file in the RAG ingest directory to force
    immediate processing of heavy files (Night Shift logic).
    """
    ingest_dir = Path(target_dir).resolve()
    if not ingest_dir.exists():
        print(f"Error: Ingest directory {ingest_dir} does not exist.")
        return False
        
    trigger_file = ingest_dir / ".trigger_now"
    trigger_file.touch()
    print(f"✅ Triggered Night Shift processing in {ingest_dir}")
    print("The background RAG ingestor will detect this file and start processing heavy files immediately.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger Night Shift Processing")
    parser.add_argument("--dir", default="/Users/bee/Sync/Antigravity/ai/agent_fs_root/ingest", help="RAG Ingest Directory")
    args = parser.parse_args()
    
    trigger_processing(args.dir)
