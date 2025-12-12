mkdir -p ~/ai/scripts
cat > ~/ai/scripts/run_gateway.sh <<'EOF'
#!/bin/zsh
set -euo pipefail

AI_DIR="$HOME/ai"
cd "$AI_DIR"

source "$AI_DIR/.venv/bin/activate"
source "$AI_DIR/configs/providers.env"

exec "$AI_DIR/.venv/bin/uvicorn" router.router:app --host 127.0.0.1 --port 5455
EOF

chmod +x ~/ai/scripts/run_gateway.sh
