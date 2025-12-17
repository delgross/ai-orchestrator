#!/usr/bin/env bash
# Setup script for LibreChat with Docker Compose

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== LibreChat Docker Setup ==="
echo ""

# Create data directory
mkdir -p librechat-data/files
chmod 755 librechat-data

# Generate random secrets if they don't exist
if [ ! -f .librechat-secrets ]; then
  echo "Generating random secrets..."
  JWT_SECRET=$(openssl rand -hex 32)
  JWT_REFRESH_SECRET=$(openssl rand -hex 32)
  MEILI_MASTER_KEY=$(openssl rand -hex 32)
  
  cat > .librechat-secrets <<EOF
JWT_SECRET=$JWT_SECRET
JWT_REFRESH_SECRET=$JWT_REFRESH_SECRET
MEILI_MASTER_KEY=$MEILI_MASTER_KEY
EOF
  echo "Secrets saved to .librechat-secrets"
else
  echo "Using existing secrets from .librechat-secrets"
  source .librechat-secrets
fi

# Update docker-compose with secrets
if [ -f librechat-docker-compose.yaml ]; then
  # Replace secrets in docker-compose
  sed -i.bak \
    -e "s|your_jwt_secret_change_this_to_random_string|$JWT_SECRET|g" \
    -e "s|your_refresh_secret_change_this_to_random_string|$JWT_REFRESH_SECRET|g" \
    -e "s|your_master_key_change_this|$MEILI_MASTER_KEY|g" \
    librechat-docker-compose.yaml
  rm -f librechat-docker-compose.yaml.bak
  echo "Updated docker-compose.yaml with secrets"
fi

# Check if orchestrator is running
echo ""
echo "Checking if orchestrator is running..."
if curl -s http://127.0.0.1:5455/ >/dev/null 2>&1; then
  echo "✓ Orchestrator is running on port 5455"
else
  echo "⚠ Warning: Orchestrator not responding on port 5455"
  echo "  Make sure your router is running: ./manage.sh ensure"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start LibreChat:"
echo "  docker compose -f librechat-docker-compose.yaml up -d"
echo ""
echo "To view logs:"
echo "  docker compose -f librechat-docker-compose.yaml logs -f"
echo ""
echo "To stop:"
echo "  docker compose -f librechat-docker-compose.yaml down"
echo ""
echo "Access LibreChat at: http://localhost:3080"
echo ""






