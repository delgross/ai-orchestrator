#!/bin/bash
set -e

# Ensure you are in the project root
cd "$(dirname "$0")"

# Stage all changes (new, modified, deleted)
git add -A

# Show status for review
git status

# Commit with a generic message (edit as needed)
git commit -m "Force complete update: add, modify, and delete all tracked files"

# Push to the main branch
git push origin main