import json
import os
import time
from pathlib import Path
import math

# Configuration
# Read from PROCESSED since we moved it there
SOURCE_FILE = Path("/Users/bee/Sync/Antigravity/ai/agent_fs_root/processed/rav2D0ijeq@2026-01-03.json")
OUTPUT_DIR = Path("/Users/bee/Sync/Antigravity/ai/agent_fs_root/ingest")
CHUNK_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB per file

def main():
    source_path = SOURCE_FILE
    if not source_path.exists():
        # Fallback to deferred if not in processed
        fallback = Path("/Users/bee/Sync/Antigravity/ai/agent_fs_root/deferred/rav2D0ijeq@2026-01-03.json")
        if fallback.exists():
            source_path = fallback
        else:
            print(f"Error: Source file not found in processed or deferred.")
            return

    print(f"Reading {source_path}...")
    with open(source_path, 'r') as f:
        data = json.load(f)

    docs = data.get("docs", [])
    print(f"Found {len(docs)} documents. Building ID Map...")
    
    # 1. Build ID -> Name Map
    id_map = {}
    for doc in docs:
        doc_id = doc.get("id")
        name = doc.get("props", {}).get("name", "Untitled")
        if doc_id:
            id_map[doc_id] = name
            
    print("ID Map built. Starting conversion...")

    current_chunk_idx = 1
    current_chunk_content = []
    current_chunk_size = 0
    
    for doc in docs:
        entry = format_doc(doc, id_map)
        entry_size = len(entry.encode('utf-8'))
        
        if current_chunk_size + entry_size > CHUNK_SIZE_BYTES:
            safe_write(current_chunk_idx, current_chunk_content)
            current_chunk_idx += 1
            current_chunk_content = []
            current_chunk_size = 0
        
        current_chunk_content.append(entry)
        current_chunk_size += entry_size

    if current_chunk_content:
        safe_write(current_chunk_idx, current_chunk_content)

    print("Conversion V2 Complete.")

def format_doc(doc, id_map):
    """Converts a JSON doc node into a Markdown section with children resolution."""
    props = doc.get("props", {})
    doc_id = doc.get("id", "UNKNOWN_ID")
    name = props.get("name", "Untitled")
    description = props.get("description", "")
    created_ts = props.get("created", 0)
    
    try:
        created_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created_ts / 1000))
    except:
        created_str = str(created_ts)

    lines = []
    # Use HTML anchor for ID linking if needed, but standard Markdown header is usually enough
    lines.append(f"## [{doc_id}] {name}")
    if description:
        lines.append(f"**Description**: {description}")
    lines.append(f"**Created**: {created_str}")
    lines.append(f"**Type**: {props.get('_docType', 'Standard Node')}")
    
    # Children (The Graph Connections)
    children = doc.get("children", [])
    if children:
        lines.append("\n**Children / Contents**:")
        for child_id in children:
            child_name = id_map.get(child_id, "Unknown Node")
            # Format as: - [Name](ChildID)
            lines.append(f"- [[{child_name}]] (ID: {child_id})")
            
    # Flatten other props
    other_props = {k: v for k, v in props.items() if k not in ['name', 'description', 'created', '_docType', '_ownerId', '_metaNodeId']}
    if other_props:
        lines.append("\n**Properties**:")
        lines.append("```yaml")
        lines.append(json.dumps(other_props, indent=2))
        lines.append("```")
    
    lines.append("\n---\n")
    return "\n".join(lines)

def safe_write(idx, content_list):
    filename = f"Truth_Export_Part_{idx:03d}.md"
    path = OUTPUT_DIR / filename
    
    full_content = f"# Knowledge Graph Export (Part {idx}) - V2 (Linked)\n\n" + "\n".join(content_list)
    
    with open(path, 'w') as f:
        f.write(full_content)
    
    print(f"Generated {filename} ({len(full_content)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    main()
