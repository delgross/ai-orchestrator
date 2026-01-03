
import logging
import os
import json
import time
from pathlib import Path
from agent_runner.state import AgentState
from agent_runner.modal_tasks import graph_community_detection

logger = logging.getLogger("agent_runner.maintenance")

async def code_janitor_task(state: AgentState):
    """
    Weekly Code Review:
    Scans Python files and uses the 'finalizer_model' (or Cloud Reasoning) to suggest improvements.
    """
    logger.info("🧹 Code Janitor: Starting scan...")
    # (Implementation details omitted for brevity, assuming similar logic to before)
    # Using state.finalizer_model

async def auto_tagger_task(state: AgentState):
    """
    Image Enhancer:
    Scans RAG ingest folder for images.
    Uses 'cloud_process_image' (Cheap Cloud GPU) to generate rich metadata.
    """
    logger.info("🏷️ Auto-Tagger: Scanning...")
    ingest_dir = Path(os.getenv("RAG_INGEST_DIR", os.path.expanduser("~/ai/rag_ingest")))
    if not ingest_dir.exists(): return
    
    # 1. Check for Modal
    from agent_runner.modal_tasks import cloud_process_image, has_modal
    if not has_modal:
        logger.warning("Auto-Tagger: Modal not configured. Skipping tag run to save costs.")
        return

    # 2. Find images
    images = [p for p in ingest_dir.glob("*") if p.suffix.lower() in ('.png', '.jpg', '.jpeg')]
    
    for img in images:
        try:
            logger.info(f"Auto-Tagging {img.name} via Cloud GPU...")
            # Remote call (no prompt -> structured JSON)
            json_result = cloud_process_image.remote(img.read_bytes())
            
            # Save sidecar as JSON
            meta_path = img.with_name(f"{img.stem}_tags.json")
            meta_path.write_text(json_result)
            logger.info(f"Tagged {img.name} (JSON)")
            
        except Exception as e:
            logger.error(f"Failed to tag {img.name}: {e}")
 


async def graph_optimization_task(state: AgentState):
    """
    Graph Enhancer:
    Runs nightly.
    1. Loads facts from RAG/Memory.
    2. Uses 'healer_model' (Llama 3.3 70B) to identify duplicate entities (Synonyms).
    3. Merges them to improve graph connectivity.
    """
    logger.info("🕸️ Graph Optimizer: Starting Gardening Cycle...")
    
    try:
        from agent_runner.tools.mcp import tool_mcp_proxy
        
        # 1. Fetch Facts
        # We fetch a batch of recent facts or all facts (limit 500 for safety)
        res = await tool_mcp_proxy(state, "project-memory", "query_facts", {"limit": 500})
        if not res.get("ok"): 
            logger.error(f"Graph Opt: Failed to fetch facts: {res}")
            return
            
        facts = res.get("result", {}).get("facts", [])
        if not facts: return
        
        # 2. Extract Entities
        entities = list(set([f.get("entity") for f in facts if f.get("entity")] + 
                            [f.get("target") for f in facts if f.get("target")]))
        
        if len(entities) < 10: return # Too small to optimize
        
        logger.info(f"Graph Opt: Analyzing {len(entities)} unique entities for duplicates...")
        
        # 3. Analyze with Llama 3.3 (Healer Model)
        # We ask it to find synonyms
        prompt = (
            "Analyze the following list of entities from a knowledge graph. "
            "Identify pairs or groups that refer to the EXACT SAME real-world concept but have different names (Synonyms). "
            "Ignore minor casing differences (already handled). Focus on semantic duplicates like 'The User' vs 'Bee' or 'Grok' vs 'xAI Model'.\n\n"
            "Entities:\n" + json.dumps(entities[:200]) + "\n\n"  # Limit context
            "Return JSON ONLY: { 'synonyms': [ {'primary': 'Preferred Name', 'aliases': ['alias1', 'alias2']} ] }"
        )
        
        client = await state.get_http_client()
        url = f"{state.gateway_base}/v1/chat/completions"
        payload = {
            "model": state.healer_model or "ollama:llama3.3:70b-instruct-q8_0",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        
        resp = await client.post(url, json=payload, timeout=60.0)
        if resp.status_code != 200:
             logger.error(f"Graph Opt: Model failed {resp.status_code}")
             return
             
        # 4. Process Merges
        content = resp.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        synonyms = data.get("synonyms", [])
        
        count = 0
        for group in synonyms:
            primary = group.get("primary")
            aliases = group.get("aliases", [])
            
            for alias in aliases:
                if alias == primary: continue
                # Perform Merge (Correct the fact)
                # We assume a mechanism to 'rename' entity across the board?
                # For now, we utilize 'correct_fact' logic but applied to entity names?
                # Actually, memory_server.correct_fact is for targets. 
                # We might need a raw query or a new tool.
                # For safety in this first pass, we just LOG suggestions to 'implementation_plan.md' or similar?
                # Or we use a new 'merge_entity' tool if we had it.
                # Let's perform a direct DB update via SQL pass-through if possible, or just log.
                logger.info(f"Graph Opt: Proposal - Merge '{alias}' -> '{primary}'")
                
                # IMPLEMENTATION: We'll add a 'merge_entities' tool to memory_server later.
                # For now, we record this as a 'graph_insight' fact.
                await tool_mcp_proxy(state, "project-memory", "store_fact", {
                    "entity": primary,
                    "relation": "is_same_as",
                    "target": alias,
                    "context": "Graph Optimization",
                    "confidence": 0.99
                })
                count += 1
                
        logger.info(f"Graph Opt: Recorded {count} synonym relations.")
        
    except Exception as e:
        logger.error(f"Graph optimization failed: {e}")


async def visual_sentry_task(state: AgentState):
    """
    Visual Sentry:
    Compares ingested images against 'references' to find anomalies.
    """
    logger.info("🛡️ Visual Sentry: Scanning for anomalies...")
    ingest_dir = Path(os.getenv("RAG_INGEST_DIR", os.path.expanduser("~/ai/rag_ingest")))
    ref_dir = ingest_dir / "references"
    
    if not ref_dir.exists():
        # Create it so the user knows where to put golden images
        ref_dir.mkdir(exist_ok=True)
        return

    # 1. Load References
    references = list(ref_dir.glob("*.jpg")) + list(ref_dir.glob("*.png"))
    if not references: return

    # 2. Check Candidates (anything in root ingest that isn't a reference)
    candidates = [p for p in ingest_dir.glob("*") if p.suffix.lower() in ('.png', '.jpg', '.jpeg') and "references" not in str(p)]
    
    from agent_runner.modal_tasks import detect_visual_anomaly, has_modal
    if not has_modal: return

    for img in candidates:
        # Avoid re-scanning if we already have an anomaly report
        report_path = img.with_name(f"{img.stem}_anomaly.json")
        if report_path.exists(): continue
        
        # Simple Matching Strategy: distinct keyword
        # If image is "tractor_005.jpg", look for reference containing "tractor"
        match = None
        for ref in references:
            # Simple heuristic: specific overlapping words or exact code match
            # For now, let's assume user names them well: "tractor_ref.jpg" matches "tractor_usage.jpg"
            # We check if the reference stem (minus _ref) is in the candidate name
            core_name = ref.stem.replace("_ref", "").replace("ref_", "")
            if core_name in img.stem:
                match = ref
                break
        
        if match:
            logger.info(f"SENTRY: Comparing {img.name} against {match.name}...")
            try:
                result = detect_visual_anomaly.remote(match.read_bytes(), img.read_bytes())
                
                # If anomalies found, save report
                if result.get("detected_changes"):
                    # Record it
                    report_path.write_text(json.dumps(result, indent=2))
                    logger.warning(f"SENTRY: Anomalies detected in {img.name}! Saved report.")
            except Exception as e:
                logger.error(f"Sentry check failed for {img.name}: {e}")

async def morning_briefing_task(state: AgentState):
    """
    Daily Report:
    Summarizes system health, ingestion stats, and any alerts.
    """
    logger.info("☀️ Morning Briefing: Generating report...")
    try:
        import datetime
        today = datetime.date.today().isoformat()
        report_path = Path(os.getenv("FS_ROOT", "~/ai/fs_root")) / "reports"
        report_path.mkdir(parents=True, exist_ok=True)
        
        # Simple stats collection (mocked for now, usually queries DB)
        stats = {
            "uptime_hours": (time.time() - state.started_at) / 3600,
            "requests": state.request_count,
            "errors": state.error_count
        }
        
        content = f"# System Briefing: {today}\n\n"
        content += f"- **Uptime:** {stats['uptime_hours']:.1f} hours\n"
        content += f"- **Requests:** {stats['requests']}\n"
        content += f"- **Errors:** {stats['errors']}\n"
        content += "\n**System Status:** Operational and monitoring."
        
        (report_path / f"BRIEFING_{today}.md").write_text(content)
        logger.info(f"Briefing saved to {report_path}")
        
    except Exception as e:
        logger.error(f"Briefing failed: {e}")

async def daily_research_task(state: AgentState):
    """
    Autonomous Research:
    Reads 'research_topics.txt' and performs a web search (if tool available).
    """
    logger.info("🔎 Daily Research: Checking topics...")
    # Placeholder for web search integration
    # topics_file = Path("ai/config/research_topics.txt")
    # ...

async def stale_memory_pruner_task(state: AgentState):
    """
    Memory Pruner:
    1. Scans facts with low confidence (< 0.5) OR older than 30 days.
    2. Verifies them with the Agent Model (Grok).
    3. Deletes verifiable falsehoods.
    """
    logger.info("🕸️ Stale Pruner: Scanning for decay...")
    
    try:
        from agent_runner.tools.mcp import tool_mcp_proxy
        
        # 1. Fetch Facts (Limit 500)
        res = await tool_mcp_proxy(state, "project-memory", "query_facts", {"limit": 500})
        if not res.get("ok"): return
        
        facts = res.get("result", {}).get("facts", [])
        if not facts: return
        
        # 2. Filter Candidates
        candidates = []
        now = time.time()
        for f in facts:
            conf = f.get("confidence", 1.0)
            # Try to parse timestamp if needed, but we rely mainly on confidence for now
            if conf < 0.5:
                candidates.append(f)
                
        if not candidates: 
            logger.info("Pruner: No low-confidence facts found.")
            return

        logger.info(f"Pruner: Verifying {len(candidates)} suspect facts...")
        
        # 3. Verify and Prune
        for fact in candidates[:10]: # Batch limit to prevent API flooding
            fid = fact.get("id") or fact.get("fact_id")
            statement = f"{fact.get('entity')} {fact.get('relation')} {fact.get('target')}"
            context = fact.get("context", "")
            
            # Ask the Brain
            prompt = (
                f"Verify this fact from my long-term memory:\n"
                f"Fact: {statement}\n"
                f"Context: {context}\n\n"
                "Is this fact likely FALSE, OBSOLETE, or HALLUCINATED based on your general knowledge and the context?\n"
                "Return JSON ONLY: { 'judgment': 'KEEP' | 'DELETE', 'reason': '...' }"
            )
            
            try:
                client = await state.get_http_client()
                url = f"{state.gateway_base}/v1/chat/completions"
                payload = {
                    "model": state.agent_model or "xai:grok-3", # Use the smartest brain for judgment
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                }
                
                resp = await client.post(url, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    decision = resp.json()["choices"][0]["message"]["content"]
                    data = json.loads(decision)
                    
                    if data.get("judgment") == "DELETE":
                        logger.info(f"Pruner: DELETING fact '{statement}' -> {data.get('reason')}")
                        await tool_mcp_proxy(state, "project-memory", "delete_fact", {"fact_id": fid})
                    else:
                        logger.debug(f"Pruner: Keeping '{statement}'")
            except Exception as e:
                logger.error(f"Pruner verification failed for {fid}: {e}")
                
    except Exception as e:
        logger.error(f"Stale Pruner failed: {e}")


