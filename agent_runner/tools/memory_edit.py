
import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.memory_edit")

async def tool_remove_memory_from_file(state: AgentState, target_text: str, file_path: str) -> Dict[str, Any]:
    """
    Surgically removes a memory/fact from a source file using Intelligence.
    
    Args:
        target_text: The concept, fact, or text snippet to remove (e.g. "Remove the section about Uplink").
        file_path: The absolute path to the file (must be within allowed dirs).
    """
    try:
        abs_path = Path(file_path).resolve()
        
        # Security Boundary Check (Basic)
        if "brain" not in str(abs_path) and "Antigravity" not in str(abs_path):
             return {"ok": False, "error": "Access Denied: Can only edit files in brain/ or project root."}
             
        if not abs_path.exists():
            return {"ok": False, "error": f"File not found: {abs_path}"}
            
        original_content = abs_path.read_text(encoding="utf-8")
        
        # Intelligence Step: Identification
        # We ask the Agent Model (or appropriate model) to identify the exact line range to remove
        prompt = (
            f"I need to 'Forget' the following concept from the text:\n"
            f"Concept to Remove: '{target_text}'\n\n"
            f"File Content:\n"
            f"```\n{original_content}\n```\n\n"
            "Task: Identify the contiguous block of lines that represents this concept.\n"
            "Return JSON ONLY: {'start_line': int, 'end_line': int, 'reason': '...'}\n"
            "If the concept is not found, return {'found': false}.\n"
            "Lines are 1-indexed."
        )
        
        client = await state.get_http_client()
        url = f"{state.gateway_base}/v1/chat/completions"
        
        payload = {
            "model": state.agent_model, # Use smart model for this surgical task
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        
        resp = await client.post(url, json=payload, timeout=30.0)
        if resp.status_code != 200:
            return {"ok": False, "error": f"LLM Call failed: {resp.text}"}
            
        plan = json.loads(resp.json()["choices"][0]["message"]["content"])
        
        if not plan.get("found", True): # Default to true if key missing
             return {"ok": False, "error": "Concept not found in file."}
             
        start = plan.get("start_line")
        end = plan.get("end_line")
        
        if not start or not end:
             return {"ok": False, "error": "Failed to identify line numbers."}
             
        # Execution Step: Surgery
        lines = original_content.splitlines()
        
        # 1-based to 0-based
        idx_start = start - 1
        idx_end = end # slice is exclusive, so this covers up to end_line
        
        # Validation
        if idx_start < 0 or idx_end > len(lines):
             return {"ok": False, "error": "LLM returned invalid line range."}
        
        logger.info(f"Surgically removing lines {start}-{end} from {file_path}")
        
        # Keep lines BEFORE start and AFTER end
        new_lines = lines[:idx_start] + lines[idx_end:]
        new_content = "\n".join(new_lines)
        
        # Write back
        abs_path.write_text(new_content, encoding="utf-8")
        
        # Trigger Re-ingest
        # We can call the manual ingest logic or let the watcher handle it.
        # Ideally, we return success and let the caller trigger ingest.
        
        return {
            "ok": True, 
            "message": f"Removed lines {start}-{end} from {abs_path.name}", 
            "lines_removed": end - start + 1
        }

    except Exception as e:
        logger.error(f"Memory Surgery Failed: {e}")
        return {"ok": False, "error": str(e)}
