#!/usr/bin/env python3
"""
Lint for SurrealQL safety: block SQL-style patterns (HAVING, LIKE, %-wildcards).
Run this to ensure no SurrealDB queries use SQL syntax.
"""
import re
import sys
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = [
    re.compile(r"\bHAVING\b", re.IGNORECASE),
    re.compile(r"\sLIKE\s", re.IGNORECASE),  # Avoid false hits on JSON-like
    re.compile(r"%[^\\s]*%", re.IGNORECASE),
]

# Curated allowlist of Surreal query sources (SurrealDB only)
QUERY_FILES = {
    "agent_runner/memory_server.py",
    "agent_runner/maintenance_tasks.py",
    "agent_runner/config_manager.py",
    "agent_runner/config.py",
    "agent_runner/engine.py",
    "agent_runner/intent.py",
    "agent_runner/routes/admin.py",
    "agent_runner/tools/system.py",
    "agent_runner/tools/admin_status.py",
    "agent_runner/rag_helpers.py",
    "agent_runner/mcp_parser.py",
    "agent_runner/health_monitor.py",
    "agent_runner/state.py",
    "agent_runner/modal_tasks.py",
    "agent_runner/background_tasks.py",
    "agent_runner/main.py",
}

QUERY_KEYWORDS = (
    "SELECT",
    "UPDATE",
    "UPSERT",
    "DELETE",
    "DEFINE",
    "LET ",
    "USE NS",
    "USE DB",
    "INFO FOR DB",
)

def scan_file(path: Path) -> list[str]:
    findings = []
    try:
        source = path.read_text()
        tree = ast.parse(source, filename=str(path))
    except Exception:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            upper_val = val.upper()
            if any(k in upper_val for k in QUERY_KEYWORDS):
                for pat in PATTERNS:
                    if pat.search(val):
                        findings.append(f"{path}:{getattr(node, 'lineno', '?')} contains disallowed SQL pattern '{pat.pattern}' in query string")
    return findings

def main() -> int:
    findings: list[str] = []
    for rel in sorted(QUERY_FILES):
        path = ROOT / rel
        if path.exists():
            findings.extend(scan_file(path))
    if findings:
        print("SurrealQL lint failed:")
        for f in findings:
            print(f"- {f}")
        return 1
    print("SurrealQL lint passed (no SQL-style patterns found).")
    return 0

if __name__ == "__main__":
    sys.exit(main())

