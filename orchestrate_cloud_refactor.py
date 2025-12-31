#!/usr/bin/env python3
"""
Orchestrate Cloud Refactor CLI

Usage:
    python orchestrate_cloud_refactor.py --target ai/router --mode full
"""

import os
import sys
import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import the modal app (will use local mock if Modal not installed, which is fine for dry-run)
# But for real run, we need to invoke the remote function.
HAS_MODAL = False
try:
    import modal
    HAS_MODAL = True
except ImportError:
    pass

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
MAX_CONCURRENCY = 5
IGNORE_DIRS = {
    "venv", ".venv", ".git", "__pycache__", ".pytest_cache", 
    "node_modules", ".gemini", "tests", "refactor_reports"
}
IGNORE_FILES = {
    ".DS_Store", "poetry.lock", "package-lock.json"
}

# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------
def get_files(target_path: Path) -> List[Path]:
    """Recursively find .py files in target_path."""
    files = []
    if target_path.is_file():
        if target_path.suffix == ".py":
            files.append(target_path)
    elif target_path.is_dir():
        for root, dirs, filenames in os.walk(target_path):
            # Filtering
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for name in filenames:
                if name.endswith(".py") and name not in IGNORE_FILES:
                    files.append(Path(root) / name)
    return sorted(files)

async def processing_worker(
    queue: asyncio.Queue, 
    results: List[Dict], 
    output_dir: Path, 
    mode: str,
    semaphore: asyncio.Semaphore,
    cloud_engine: Optional[Any] = None
):
    while True:
        file_path = await queue.get()
        relative_path = file_path.relative_to(Path.cwd())
        
        try:
            async with semaphore:
                print(f"🚀 Dispatching: {relative_path}...")
                
                # Read Content
                with open(file_path, "r") as f:
                    content = f.read()
                
                # Call Cloud Function
                # Note: cloud_engine is the Class Handle.
                # We expect cloud_engine to be the Class. We must instantiate it.
                if cloud_engine:
                    # Real Cloud Call
                    start_time = time.time()
                    # cloud_engine() acts as the constructor proxy
                    json_str = await asyncio.to_thread(cloud_engine().cloud_file_refactor.remote, str(relative_path), content)
                    duration = time.time() - start_time
                else:
                    # Fallback / Mock
                    await asyncio.sleep(0.5)
                    json_str = json.dumps({
                        "analysis": "Mock Analysis (Local)", 
                        "critique": ["Mock Critique"], 
                        "rewritten_code": content,
                        "generated_tests": "# Mock Test",
                        "fuzzing_scenarios": [],
                        "next_steps": []
                    })
                    duration = 0.5

                # Parse Response
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    data = {"error": "Failed to parse JSON response", "raw": json_str}

                # Save Artifacts (Shadow Structure)
                # 1. Rewritten Code
                if "rewritten_code" in data:
                    out_code = output_dir / "rewritten" / relative_path
                    out_code.parent.mkdir(parents=True, exist_ok=True)
                    with open(out_code, "w") as f:
                        f.write(data["rewritten_code"])
                        
                # 2. Analysis Report
                report_path = output_dir / "reports" / relative_path.with_suffix(".md")
                report_path.parent.mkdir(parents=True, exist_ok=True)
                with open(report_path, "w") as f:
                    f.write(f"# Cloud Refactor Report: {relative_path}\n\n")
                    f.write(f"**Mode**: {mode}\n")
                    f.write(f"**Duration**: {duration:.2f}s\n\n")
                    
                    if "analysis" in data:
                        f.write(f"## 1. Deep Analysis\n{data['analysis']}\n\n")
                    
                    if "critique" in data:
                        f.write(f"## 2. Critique\n")
                        for c in data["critique"]:
                            f.write(f"- {c}\n")
                        f.write("\n")
                        
                    if "fuzzing_scenarios" in data:
                        f.write(f"## 3. Security Fuzzing Scenarios\n")
                        for s in data["fuzzing_scenarios"]:
                            f.write(f"- {s}\n")
                        f.write("\n")

                    if "next_steps" in data:
                        f.write(f"## 4. Next Steps\n")
                        for n in data["next_steps"]:
                            f.write(f"- {n}\n")
                        f.write("\n")
                        
                # 3. Tests
                if "generated_tests" in data:
                    out_test = output_dir / "tests" / f"test_{relative_path.name}"
                    out_test.parent.mkdir(parents=True, exist_ok=True)
                    with open(out_test, "w") as f:
                        f.write(data["generated_tests"])

                print(f"✅ Completed: {relative_path} ({duration:.2f}s)")
                results.append({
                    "file": str(relative_path), 
                    "status": "success", 
                    "duration": duration,
                    "critique_count": len(data.get("critique", []))
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Error {relative_path}: {e}")
            results.append({"file": str(relative_path), "status": "error", "error": str(e)})
        finally:
            queue.task_done()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
async def main():
    global HAS_MODAL
    parser = argparse.ArgumentParser(description="Antigravity Cloud Refactor Orchestrator")
    parser.add_argument("--target", default=".", help="Target file or directory to process")
    parser.add_argument("--mode", default="full", choices=["full", "audit", "test", "docs"], help="Operation mode")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of files (for testing)")
    parser.add_argument("--dry-run", action="store_true", help="Run without invoking cloud functions")
    
    args = parser.parse_args()
    
    # Setup Output Dir
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_dir = Path("refactor_reports") / ts
    
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"📂 Output Directory: {out_dir}")
    
    # Discovery
    target_path = Path(args.target).resolve()
    if not target_path.exists():
        print(f"❌ Target not found: {target_path}")
        return
        
    files = get_files(target_path)
    if args.limit > 0:
        files = files[:args.limit]
        
    print(f"found {len(files)} python files to process.")
    
    # Confirmation
    if not HAS_MODAL:
        print("\n⚠️ WARNING: Modal client not installed/configured. This will be a LOCAL MOCK run.")
    
    print("\nFiles to be processed:")
    for f in files[:5]:
        print(f" - {f.relative_to(Path.cwd())}")
    if len(files) > 5:
        print(f" ... and {len(files)-5} more.")
        
    # Queue & Workers
    queue = asyncio.Queue()
    for f in files:
        queue.put_nowait(f)
        
    results = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    
    # Execution Context Wrapper
    
    # Force Mock override
    if args.dry_run:
        print("⚠️ DRY RUN ENABLED: Skipping Cloud Execution.")
        HAS_MODAL = False
        
    cloud_engine = None
    if HAS_MODAL:
        print("☁️ Connecting to Deployed Modal App (CloudEngineer Snapshot)...")
        import modal
        try:
            cloud_engine = modal.Cls.from_name("antigravity-night-shift", "CloudEngineer")
            print("✅ Connected to 'CloudEngineer'")
        except Exception as e:
            print(f"❌ Failed to lookup CloudEngineer: {e}")
            HAS_MODAL = False

    # Dispatch Loop
    workers = []
    num_workers = min(len(files), MAX_CONCURRENCY)
    
    # We pass the cloud_func explicitly to worker now, or attach it to something global?
    # Let's modify processing_worker signature slightly or just set a global.
    # Actually, better to pass it.
    
    for _ in range(num_workers):
        workers.append(asyncio.create_task(processing_worker(queue, results, out_dir, args.mode, semaphore, cloud_engine=cloud_engine)))
        
    # Wait
    await queue.join()
    for w in workers:
        w.cancel()
        
    # Summary
    print("\n🏁 Use 'summary.md' in output dir for details.")
    summary_path = out_dir / "summary.md"
    with open(summary_path, "w") as f:
        f.write(f"# Refactor Run Summary\n")
        f.write(f"Target: `{args.target}`\n")
        f.write(f"Mode: `{args.mode}`\n\n")
        f.write("| File | Status | Duration | Critiques |\n")
        f.write("|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['file']} | {r['status']} | {r.get('duration',0):.2f}s | {r.get('critique_count', '-')} |\n")

if __name__ == "__main__":
    asyncio.run(main())
