#!/bin/bash
# Monitor router latency in real-time

ROUTER_URL="${ROUTER_URL:-http://127.0.0.1:5455}"
AUTH_TOKEN="${ROUTER_AUTH_TOKEN:-9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic}"

echo "=== Router Latency Monitor ==="
echo "Press Ctrl+C to stop"
echo ""

while true; do
    clear
    echo "=== Router Latency Monitor ==="
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    curl -s -H "Authorization: Bearer $AUTH_TOKEN" "$ROUTER_URL/metrics" | python3 -c "
import sys, json
from datetime import datetime
try:
    data = json.load(sys.stdin)
    recent = data.get('recent_requests', [])[:10]
    
    if not recent:
        print('No recent requests')
    else:
        print('Recent Requests (last 10):')
        print('')
        print(f\"{'Status':<8} {'Latency':<12} {'Model':<25} {'Time'}\")
        print('-' * 70)
        
        for r in recent:
            elapsed = r.get('elapsed_ms', 0) / 1000
            status = r.get('status_code', 0)
            success = '✓ OK' if r.get('success') else '✗ ERR'
            model = r.get('model', 'unknown')[:24]
            ts = datetime.fromtimestamp(r.get('timestamp', 0))
            time_str = ts.strftime('%H:%M:%S')
            
            # Color code latency
            if elapsed > 60:
                latency_str = f\"{elapsed:6.1f}s ⚠\"
            elif elapsed > 30:
                latency_str = f\"{elapsed:6.1f}s ⚡\"
            else:
                latency_str = f\"{elapsed:6.1f}s\"
            
            print(f\"{success:<8} {latency_str:<12} {model:<25} {time_str}\")
        
        print('')
        usage = data.get('usage', {}).get('total', {})
        print(f\"Total Requests: {usage.get('requests', 0)}\")
        print(f\"Total Tokens: {usage.get('total_tokens', 0):,}\")
        print(f\"Total Cost: \${usage.get('cost_usd', 0):.4f}\")
except Exception as e:
    print(f'Error: {e}')
"
    
    sleep 2
done















