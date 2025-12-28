#!/bin/bash
# Play a system sound to alert the user
# Useful for when the Agent needs manual approval/intervention

# Check if we are on macOS
if [[ "$(uname)" == "Darwin" ]]; then
    afplay /System/Library/Sounds/Tink.aiff
else
    echo -e "\a" # Fallback to system bell
fi
