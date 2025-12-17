#!/usr/bin/env bash
set -euo pipefail

U="$(id -u)"
DOMAIN="gui/$U"

RPL="$HOME/Library/LaunchAgents/local.ai.router.plist"
APL="$HOME/Library/LaunchAgents/local.ai.agent_runner.plist"

RS="$HOME/ai/bin/run_router.sh"
AS="$HOME/ai/bin/run_agent_runner.sh"

[ -x "$RS" ] || { echo "Missing/executable: $RS"; exit 1; }
[ -x "$AS" ] || { echo "Missing/executable: $AS"; exit 1; }

echo "== patch plists to call wrappers =="
python3 - <<PY
import plistlib
from pathlib import Path
home = Path.home()

def patch(plist_path, script_path):
    p = Path(plist_path)
    d = plistlib.loads(p.read_bytes())
    d["ProgramArguments"] = ["/bin/bash", str(Path(script_path))]
    p.write_bytes(plistlib.dumps(d, fmt=plistlib.FMT_XML, sort_keys=True))
    print("patched", p)

patch("$RPL", "$RS")
patch("$APL", "$AS")
PY

echo "== lint plists =="
plutil -lint "$RPL"
plutil -lint "$APL"

echo "== bootout existing jobs (ignore errors) =="
launchctl bootout "$DOMAIN" "$RPL" 2>/dev/null || true
launchctl bootout "$DOMAIN" "$APL" 2>/dev/null || true

echo "== kill anything still holding ports =="
lsof -ti tcp:5455 2>/dev/null | xargs -r kill -9 || true
lsof -ti tcp:5460 2>/dev/null | xargs -r kill -9 || true
sleep 1

echo "== bootstrap + kickstart =="
launchctl bootstrap "$DOMAIN" "$RPL"
launchctl bootstrap "$DOMAIN" "$APL"
launchctl kickstart -k "$DOMAIN/local.ai.router"
launchctl kickstart -k "$DOMAIN/local.ai.agent_runner"
sleep 1

echo "== confirm program path is /bin/bash (wrapper) =="
launchctl print "$DOMAIN/local.ai.router" | egrep -a 'program =|program arguments|path =|last exit' | head -n 60 || true
launchctl print "$DOMAIN/local.ai.agent_runner" | egrep -a 'program =|program arguments|path =|last exit' | head -n 60 || true

echo "== ports =="
lsof -nP -iTCP:5455 -sTCP:LISTEN || echo "5455 free"
lsof -nP -iTCP:5460 -sTCP:LISTEN || echo "5460 free"
