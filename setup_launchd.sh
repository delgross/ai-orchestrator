#!/usr/bin/env bash
set -Eeuo pipefail

USER_UID="$(id -u)"
USER_HOME="$HOME"
LA="$HOME/Library/LaunchAgents"
LOGDIR="$HOME/Library/Logs/ai"

ROUTER_PLIST="$LA/local.ai.router.plist"
AGENT_PLIST="$LA/local.ai.agent_runner.plist"

mkdir -p "$LA" "$LOGDIR"

backup() {
  local f="$1"
  [ -f "$f" ] && cp -v "$f" "$f.bak.$(date +%Y%m%d-%H%M%S)" || true
}

echo "== backup existing plists =="
backup "$ROUTER_PLIST"
backup "$AGENT_PLIST"

# Detect the actual project root (where this script lives)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT

echo "== write plists via python plistlib (always valid XML) =="
echo "Project root: $PROJECT_ROOT"
python3 - <<PY
import os, plistlib, pathlib

home = os.environ["HOME"]
project_root = os.environ["PROJECT_ROOT"]
router_plist = pathlib.Path(home) / "Library/LaunchAgents/local.ai.router.plist"
agent_plist  = pathlib.Path(home) / "Library/LaunchAgents/local.ai.agent_runner.plist"

# Router: delegate to bin/run_router.sh so env + venv are handled in one place.
router = {
  "Label": "local.ai.router",
  "WorkingDirectory": project_root,
  "EnvironmentVariables": {
    "PYTHONPATH": project_root,
    "PROVIDERS_YAML": f"{project_root}/providers.yaml",
    "OLLAMA_BASE": "http://127.0.0.1:11434",
    "AGENT_RUNNER_URL": "http://127.0.0.1:5460",
    "NO_PROXY": "127.0.0.1,localhost",
    "no_proxy": "127.0.0.1,localhost",
  },
  "ProgramArguments": [
    "/bin/bash",
    f"{project_root}/bin/run_router.sh",
  ],
  "RunAtLoad": True,
  "KeepAlive": True,
  "StandardOutPath": f"{home}/Library/Logs/ai/router.out.log",
  "StandardErrorPath": f"{home}/Library/Logs/ai/router.err.log",
}

# Agent-runner: delegate to bin/run_agent_runner.sh
agent = {
  "Label": "local.ai.agent_runner",
  "WorkingDirectory": f"{project_root}/agent_runner",
  "EnvironmentVariables": {
    "GATEWAY_BASE": "http://127.0.0.1:5455",
    "AGENT_FS_ROOT": f"{project_root}/agent_fs_root",
    "NO_PROXY": "127.0.0.1,localhost",
    "no_proxy": "127.0.0.1,localhost",
  },
  "ProgramArguments": [
    "/bin/zsh",
    f"{project_root}/bin/run_agent_runner.sh",
  ],
  "RunAtLoad": True,
  "KeepAlive": True,
  "StandardOutPath": f"{home}/Library/Logs/ai/agent_runner.out.log",
  "StandardErrorPath": f"{home}/Library/Logs/ai/agent_runner.err.log",
}

router_plist.parent.mkdir(parents=True, exist_ok=True)
agent_plist.parent.mkdir(parents=True, exist_ok=True)

router_plist.write_bytes(plistlib.dumps(router, fmt=plistlib.FMT_XML, sort_keys=True))
agent_plist.write_bytes(plistlib.dumps(agent, fmt=plistlib.FMT_XML, sort_keys=True))

print("Wrote:", router_plist)
print("Wrote:", agent_plist)
PY

echo "== fix perms/xattrs + lint =="
chmod 644 "$ROUTER_PLIST" "$AGENT_PLIST"
chown "$(whoami)":staff "$ROUTER_PLIST" "$AGENT_PLIST"
xattr -cr "$ROUTER_PLIST" "$AGENT_PLIST" 2>/dev/null || true
plutil -lint "$ROUTER_PLIST"
plutil -lint "$AGENT_PLIST"

echo "== bootout any existing copies (ignore errors) =="
launchctl bootout "gui/$USER_UID" "$ROUTER_PLIST" 2>/dev/null || true
launchctl bootout "gui/$USER_UID" "$AGENT_PLIST" 2>/dev/null || true
launchctl bootout "user/$USER_UID" "$ROUTER_PLIST" 2>/dev/null || true
launchctl bootout "user/$USER_UID" "$AGENT_PLIST" 2>/dev/null || true

echo "== bootstrap + kickstart (try gui first; fallback to user) =="
if launchctl bootstrap "gui/$USER_UID" "$ROUTER_PLIST" && launchctl bootstrap "gui/$USER_UID" "$AGENT_PLIST"; then
  DOMAIN="gui/$USER_UID"
else
  DOMAIN="user/$USER_UID"
  launchctl bootstrap "$DOMAIN" "$ROUTER_PLIST"
  launchctl bootstrap "$DOMAIN" "$AGENT_PLIST"
fi

launchctl kickstart -k "$DOMAIN/local.ai.router"
launchctl kickstart -k "$DOMAIN/local.ai.agent_runner"

echo "== health =="
curl -sS http://127.0.0.1:5455/ | python -m json.tool
curl -sS http://127.0.0.1:5460/ | python -m json.tool
