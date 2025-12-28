#!/bin/bash
# Troubleshooting helper script - queries diagnostic endpoints to gather system state
# Usage: ./troubleshoot.sh [--json|-j]  (use --json to export to JSON format)

AGENT_BASE="${AGENT_BASE:-http://127.0.0.1:5460}"
ROUTER_BASE="${ROUTER_BASE:-http://127.0.0.1:5455}"

# Check for JSON export mode first (before any output)
if [ "${1}" = "--json" ] || [ "${1}" = "-j" ]; then
    python3 << 'PYTHON_EOF'
import json
import subprocess
import sys
from datetime import datetime

def get_json(url):
    try:
        result = subprocess.run(['curl', '-s', url], capture_output=True, text=True)
        return json.loads(result.stdout)
    except:
        return None

agent_base = "${AGENT_BASE:-http://127.0.0.1:5460}"
router_base = "${ROUTER_BASE:-http://127.0.0.1:5455}"

report = {
    "timestamp": datetime.now().isoformat(),
    "circuit_breakers": get_json(f"{agent_base}/admin/circuit-breaker/status"),
    "health": get_json(f"{agent_base}/admin/health"),
    "stdio_status": get_json(f"{agent_base}/admin/mcp/stdio/status"),
    "memory": get_json(f"{agent_base}/admin/memory"),
    "performance": get_json(f"{agent_base}/admin/performance"),
    "metrics": get_json(f"{agent_base}/metrics"),
    "router": get_json(f"{router_base}/"),
}

print(json.dumps(report, indent=2))
PYTHON_EOF
    exit 0
fi

echo "🔍 System Troubleshooting Report"
echo "================================="
echo ""

# Circuit Breaker Status
echo "📊 Circuit Breaker Status:"
echo "-------------------------"
curl -s "${AGENT_BASE}/admin/circuit-breaker/status" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    summary = data.get('summary', {})
    print(f\"Total: {summary.get('total', 0)}, Healthy: {summary.get('healthy', 0)}, Disabled: {summary.get('disabled', 0)}, Testing: {summary.get('testing', 0)}\")
    print(\"\nDisabled Servers:\")
    for name, info in data.get('circuit_breakers', {}).items():
        if info.get('is_blocked'):
            print(f\"  ⚠️  {name}: {info.get('message', 'Unknown')}\")
    if not any(info.get('is_blocked') for info in data.get('circuit_breakers', {}).values()):
        print(\"  ✅ All servers operational\")
" 2>/dev/null || echo "  ❌ Could not fetch circuit breaker status"
echo ""

# System Health
echo "🏥 System Health:"
echo "-----------------"
curl -s "${AGENT_BASE}/admin/health" | python3 -c "
import sys, json
data = json.load(sys.stdin)
status = data.get('status', 'unknown')
print(f\"Overall Status: {status.upper()}\")
print(\"\nComponents:\")
for name, comp in data.get('components', {}).items():
    comp_status = comp.get('status', 'unknown')
    icon = '✅' if comp_status == 'healthy' else '⚠️' if comp_status == 'degraded' else '❌'
    error = comp.get('error', '')
    print(f\"  {icon} {name}: {comp_status}\" + (f\" - {error}\" if error else \"\"))
" 2>/dev/null || echo "  ❌ Could not fetch health status"
echo ""

# Stdio Process Status
echo "⚙️  Stdio Process Status:"
echo "------------------------"
curl -s "${AGENT_BASE}/admin/mcp/stdio/status" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    processes = data.get('processes', [])
    if processes:
        print(f\"Total Processes: {len(processes)}\")
        for proc in processes:
            server = proc.get('server', 'unknown')
            running = proc.get('running', False)
            initialized = proc.get('initialized', False)
            alive = proc.get('alive', False)
            returncode = proc.get('returncode')
            
            if running and initialized and alive:
                icon = '✅'
                status = 'OK'
            elif running and not initialized:
                icon = '⚠️'
                status = 'Not initialized'
            elif running and returncode is not None:
                icon = '❌'
                status = f'Dead (returncode={returncode})'
            else:
                icon = '❌'
                status = 'Not running'
            
            print(f\"  {icon} {server}: {status}\")
    else:
        print(\"  ℹ️  No stdio processes\")
" 2>/dev/null || echo "  ❌ Could not fetch stdio status"
echo ""

# Memory Server Status
echo "🧠 Memory Server Status:"
echo "-----------------------"
curl -s "${AGENT_BASE}/admin/memory" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    health = data.get('memory_health', {})
    if health.get('ok'):
        print(f\"  ✅ Connected: {health.get('connected', False)}\")
        facts = data.get('facts', [])
        print(f\"  📝 Facts: {len(facts)} available\")
    else:
        error = health.get('error', 'Unknown error')
        print(f\"  ❌ Error: {error}\")
        # Check if it's a circuit breaker issue
        if 'circuit breaker' in error.lower():
            print(f\"  💡 This is a circuit breaker issue - server may recover automatically\")
            print(f\"     Or reset with: curl -X POST ${AGENT_BASE}/admin/circuit-breaker/reset -H 'Content-Type: application/json' -d '{\\\"server\\\": \\\"project-memory\\\"}'\")
else:
    print(f\"  ❌ {data.get('error', 'Unknown error')}\")
" 2>/dev/null || echo "  ❌ Could not fetch memory status"

# Memory Stats (if available)
curl -s "${AGENT_BASE}/admin/memory/stats" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('ok'):
        stats = data.get('stats', {})
        if stats:
            total = stats.get('total_facts', 0)
            print(f\"  📊 Total facts in database: {total}\")
except:
    pass
" 2>/dev/null
echo ""

# Router Status
echo "🌐 Router Status:"
echo "----------------"
curl -s "${ROUTER_BASE}/" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('ok'):
        print(f\"  ✅ Router operational\")
        models = data.get('models', [])
        print(f\"  📊 Models: {len(models)} available\")
        # Show model breakdown
        local = [m for m in models if isinstance(m, dict) and m.get('id', '').startswith('ollama:')]
        remote = [m for m in models if isinstance(m, dict) and (m.get('id', '').startswith('openai:') or m.get('id', '').startswith('claude-'))]
        if local or remote:
            print(f\"     Local: {len(local)}, Remote: {len(remote)}\")
    else:
        print(f\"  ❌ Router error: {data.get('error', 'Unknown')}\")
except Exception as e:
    print(f\"  ❌ Could not connect to router: {e}\")
" 2>/dev/null || echo "  ❌ Could not fetch router status"
echo ""

# System Uptime & Metrics
echo "📈 System Metrics:"
echo "------------------"
curl -s "${AGENT_BASE}/metrics" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    uptime = data.get('uptime_s', 0)
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    print(f\"  Uptime: {hours}h {minutes}m\")
    print(f\"  Tools: {data.get('tools_count', 0)} total ({data.get('mcp_tools_count', 0)} MCP, {data.get('file_tools_count', 0)} file)\")
    print(f\"  MCP Servers: {len(data.get('mcp_servers', []))}\")
" 2>/dev/null || echo "  ⚠️  Metrics unavailable"
echo ""

# Performance Metrics
echo "⚡ Performance Metrics:"
echo "----------------------"
curl -s "${AGENT_BASE}/admin/performance" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    proc = data.get('process', {})
    sys_info = data.get('system', {})
    print(f\"  Memory: {proc.get('memory_mb', 0):.1f} MB ({proc.get('memory_percent', 0):.1f}%)\")
    print(f\"  CPU: {proc.get('cpu_percent', 0):.1f}%\")
    print(f\"  Threads: {proc.get('num_threads', 0)}\")
    print(f\"  System Load: {sys_info.get('load_1min', 0):.2f} ({sys_info.get('load_percent', 0):.1f}% of {sys_info.get('cpu_count', 1)} CPUs)\")
    cache = data.get('cache', {})
    if cache.get('tool_cache_enabled'):
        print(f\"  Tool Cache: {cache.get('tool_cache_size', 0)} entries\")
else:
    print(f\"  ⚠️  {data.get('error', 'Metrics unavailable')}\")
" 2>/dev/null || echo "  ⚠️  Performance metrics unavailable"
echo ""

# Recent Errors Summary (from logs)
echo "📋 Recent Error Summary:"
echo "------------------------"
python3 << 'PYTHON_EOF'
import subprocess
import re
from collections import Counter

log_file = "~/Library/Logs/ai/agent_runner.err.log"
try:
    # Get last 50 lines and look for errors
    result = subprocess.run(['tail', '-50', log_file], capture_output=True, text=True, shell=True)
    lines = result.stdout.split('\n')
    
    errors = []
    for line in lines:
        if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception', 'circuit breaker', 'disabled']):
            # Extract error message
            if 'ERROR' in line or 'CRITICAL' in line or 'WARNING' in line:
                errors.append(line.strip())
    
    if errors:
        print(f"  Found {len(errors)} recent error(s) in logs:")
        for err in errors[-5:]:  # Show last 5
            # Truncate long lines
            if len(err) > 100:
                err = err[:97] + "..."
            print(f"    • {err}")
    else:
        print("  ✅ No recent errors in logs")
except Exception as e:
    print(f"  ⚠️  Could not read logs: {e}")
PYTHON_EOF
echo ""

# Issue Detection & Recommendations
echo "🔧 Issue Detection & Recommendations:"
echo "-------------------------------------"
python3 << 'PYTHON_EOF'
import json
import subprocess
import sys

def get_json(url):
    try:
        result = subprocess.run(['curl', '-s', url], capture_output=True, text=True)
        return json.loads(result.stdout)
    except:
        return None

agent_base = "${AGENT_BASE:-http://127.0.0.1:5460}"
issues = []
recommendations = []

# Check circuit breakers
cb_data = get_json(f"{agent_base}/admin/circuit-breaker/status")
if cb_data and cb_data.get('ok'):
    disabled = [(n, i) for n, i in cb_data.get('circuit_breakers', {}).items() if i.get('is_blocked')]
    if disabled:
        issues.append(f"⚠️  {len(disabled)} server(s) disabled by circuit breaker")
        stdio_disabled = []
        http_disabled = []
        for name, info in disabled:
            # Try to determine transport type from diagnostics
            diag = get_json(f"{agent_base}/admin/diagnostics/mcp/{name}")
            if diag and diag.get('config', {}).get('scheme') == 'stdio':
                stdio_disabled.append(name)
            else:
                http_disabled.append(name)
        
        if len(stdio_disabled) == len(disabled):
            recommendations.append("→ All disabled servers are stdio - likely agent-runner issue")
            recommendations.append("  Action: Check agent-runner logs and process status")
        elif len(stdio_disabled) > 0:
            recommendations.append(f"→ {len(stdio_disabled)} stdio server(s) disabled - check process management")
            recommendations.append("  Action: Review stdio process status and initialization")
        
        if http_disabled:
            recommendations.append(f"→ {len(http_disabled)} remote server(s) disabled - check network connectivity")
            recommendations.append("  Action: Verify network connectivity and remote service status")
        
        # Suggest reset for specific servers
        for name, info in disabled[:3]:  # Limit to first 3
            recommendations.append(f"  Quick fix: curl -X POST {agent_base}/admin/circuit-breaker/reset -H 'Content-Type: application/json' -d '{{\"server\": \"{name}\"}}'")

# Check stdio processes
stdio_data = get_json(f"{agent_base}/admin/mcp/stdio/status")
if stdio_data and stdio_data.get('ok'):
    procs = stdio_data.get('processes', [])
    uninitialized = [p for p in procs if p.get('running') and not p.get('initialized')]
    dead = [p for p in procs if p.get('running') and not p.get('alive')]
    
    if uninitialized:
        issues.append(f"⚠️  {len(uninitialized)} stdio process(es) not initialized")
        recommendations.append("→ MCP handshake may be failing")
        recommendations.append("  Action: Check process stderr and initialization logs")
        for p in uninitialized[:2]:
            recommendations.append(f"  Check: curl {agent_base}/admin/diagnostics/mcp/{p.get('server')}")
    
    if dead:
        issues.append(f"⚠️  {len(dead)} stdio process(es) dead")
        recommendations.append("→ Processes are dying - check for errors")
        recommendations.append("  Action: Review process return codes and error logs")

# Check system health
health_data = get_json(f"{agent_base}/admin/health")
if health_data:
    unhealthy = [(n, c) for n, c in health_data.get('components', {}).items() if c.get('status') == 'unhealthy']
    if unhealthy:
        issues.append(f"🔴 {len(unhealthy)} component(s) unhealthy")
        for name, comp in unhealthy:
            error = comp.get('error', 'Unknown error')
            recommendations.append(f"→ {name}: {error}")

# Check performance
perf_data = get_json(f"{agent_base}/admin/performance")
if perf_data and perf_data.get('ok'):
    sys_info = perf_data.get('system', {})
    load_pct = sys_info.get('load_percent', 0)
    if load_pct > 80:
        issues.append(f"⚠️  High system load: {load_pct:.1f}%")
        recommendations.append("→ System may be resource-constrained")
        recommendations.append("  Action: Check for resource-intensive processes")
    
    proc = perf_data.get('process', {})
    mem_pct = proc.get('memory_percent', 0)
    if mem_pct > 80:
        issues.append(f"⚠️  High memory usage: {mem_pct:.1f}%")
        recommendations.append("→ Agent-runner using high memory")
        recommendations.append("  Action: Consider restarting or checking for memory leaks")

if not issues:
    print("  ✅ No issues detected - system appears healthy")
else:
    print("\n".join(f"  {i}" for i in issues))
    if recommendations:
        print("\n💡 Recommendations:")
        print("\n".join(f"  {r}" for r in recommendations))

PYTHON_EOF
echo ""

# Quick Actions
echo "🚀 Quick Actions:"
echo "----------------"
echo "  Reset all circuit breakers:"
echo "    curl -X POST ${AGENT_BASE}/admin/circuit-breaker/reset -H 'Content-Type: application/json' -d '{\"server\": null}'"
echo ""
echo "  Reload MCP servers:"
echo "    curl -X POST ${AGENT_BASE}/admin/reload-mcp -H 'Content-Type: application/json' -d '{}'"
echo ""
echo "  View detailed server info:"
echo "    curl ${AGENT_BASE}/admin/diagnostics/mcp/{server} | jq"
echo ""

# Summary Score
echo "📊 System Health Score:"
echo "----------------------"
python3 << 'PYTHON_EOF'
import subprocess
import json

def get_json(url):
    try:
        result = subprocess.run(['curl', '-s', url], capture_output=True, text=True)
        return json.loads(result.stdout)
    except:
        return None

agent_base = "${AGENT_BASE:-http://127.0.0.1:5460}"
score = 100
issues = []

# Check circuit breakers
cb_data = get_json(f"{agent_base}/admin/circuit-breaker/status")
if cb_data and cb_data.get('ok'):
    disabled = sum(1 for i in cb_data.get('circuit_breakers', {}).values() if i.get('is_blocked'))
    if disabled > 0:
        score -= disabled * 10
        issues.append(f"{disabled} server(s) disabled")

# Check stdio processes
stdio_data = get_json(f"{agent_base}/admin/mcp/stdio/status")
if stdio_data and stdio_data.get('ok'):
    procs = stdio_data.get('processes', [])
    unhealthy = sum(1 for p in procs if not (p.get('running') and p.get('initialized') and p.get('alive')))
    if unhealthy > 0:
        score -= unhealthy * 5
        issues.append(f"{unhealthy} process(es) unhealthy")

# Check health
health_data = get_json(f"{agent_base}/admin/health")
if health_data:
    unhealthy = sum(1 for c in health_data.get('components', {}).values() if c.get('status') == 'unhealthy')
    if unhealthy > 0:
        score -= unhealthy * 15
        issues.append(f"{unhealthy} component(s) unhealthy")

score = max(0, score)

if score >= 90:
    icon = "✅"
    status = "Excellent"
elif score >= 70:
    icon = "⚠️"
    status = "Good"
elif score >= 50:
    icon = "🔶"
    status = "Degraded"
else:
    icon = "🔴"
    status = "Critical"

print(f"  {icon} Score: {score}/100 ({status})")
if issues:
    print(f"  Issues: {', '.join(issues)}")
else:
    print(f"  ✅ No issues detected")
PYTHON_EOF
echo ""

echo "================================="
echo "💡 Tips:"
echo "  - Export to JSON: $0 --json > diagnostic-report.json"
echo "  - View server details: curl ${AGENT_BASE}/admin/diagnostics/mcp/{server} | jq"
echo "  - Check logs: tail -f ~/Library/Logs/ai/agent_runner.err.log | grep -i 'circuit\|error'"
echo ""

