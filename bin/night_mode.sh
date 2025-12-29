#!/bin/bash

# Night Mode Control (Sleep Prevention)
# Usage: sudo ./bin/night_mode.sh [on|off]

MODE=$1

if [ "$MODE" == "on" ]; then
    echo "🌙 Enabling Night Mode (Sleep Disabled)..."
    pmset -a sleep 0
    pmset -a displaysleep 0
    echo "✅ System will stay awake for Night Shift H100 operations."
elif [ "$MODE" == "off" ]; then
    echo "☀️ Disabling Night Mode (Default Sleep Restored)..."
    pmset -a sleep 15
    pmset -a displaysleep 10
    echo "✅ System sleep restored."
else
    echo "Usage: sudo $0 [on|off]"
    exit 1
fi
