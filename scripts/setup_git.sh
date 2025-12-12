#!/bin/zsh

echo "=== Setting up Git ==="

cd "$HOME/ai"

git init
echo ".venv/" > .gitignore
echo "logs/" >> .gitignore
echo "__pycache__/" >> .gitignore

git add .
git commit -m "Initial commit"
