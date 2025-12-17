#!/usr/bin/env bash
set +e  # do not exit early

cd "$HOME/ai" || exit 1

# Run whatever command was passed in
"$@"
ec=$?

echo
echo "Command exit status: $ec"
echo "You are now in an interactive shell. Type: exit  (to close)"

# Keep the session alive permanently
exec "$SHELL" -l
