
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
    1. Loads all entities/relations from RAG.
    2. Sends them to Modal (graph_community_detection).
    3. Updates the RAG graph with 'community_id' tags.
    """
    logger.info("🕸️ Graph Optimizer: Starting Cloud Analysis...")
    
    # 1. Fetch Graph Data (Mocked for now as we don't have direct graph export)
    nodes = [1, 2, 3, 4]
    edges = [(1,2), (2,3), (3,4), (4,1)]
    
    # 2. Call Modal
    try:
        if hasattr(graph_community_detection, "remote"):
            # We are in a Modal-enabled environment
            logger.info("Offloading graph to Modal Cloud...")
            result = graph_community_detection.remote(nodes, edges)
            logger.info(f"Graph Result: {result}")
        else:
            logger.warning("Modal not active. Skipping.")
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
    Identifying and removing low-confidence facts.
    """
    logger.info("🕸️ Stale Pruner: Scanning for decay...")
    # Placeholder


