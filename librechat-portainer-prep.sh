#!/usr/bin/env bash
# Prepare docker-compose.yaml for Portainer deployment with secrets filled in

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Preparing LibreChat Compose for Portainer ==="
echo ""

# Generate secrets if they don't exist
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
else
  source .librechat-secrets
fi

# Create Portainer-ready compose file
if [ -f librechat-docker-compose.yaml ]; then
  sed \
    -e "s|your_jwt_secret_change_this_to_random_string|$JWT_SECRET|g" \
    -e "s|your_refresh_secret_change_this_to_random_string|$JWT_REFRESH_SECRET|g" \
    -e "s|your_master_key_change_this|$MEILI_MASTER_KEY|g" \
    librechat-docker-compose.yaml > librechat-docker-compose-portainer.yaml
  
  echo "✓ Created: librechat-docker-compose-portainer.yaml"
  echo ""
  echo "This file is ready to paste into Portainer's stack editor."
  echo ""
  echo "Secrets used:"
  echo "  JWT_SECRET: ${JWT_SECRET:0:20}..."
  echo "  JWT_REFRESH_SECRET: ${JWT_REFRESH_SECRET:0:20}..."
  echo "  MEILI_MASTER_KEY: ${MEILI_MASTER_KEY:0:20}..."
  echo ""
  echo "Next steps:"
  echo "  1. Open Portainer → Stacks → Add stack"
  echo "  2. Name: librechat"
  echo "  3. Build method: Web editor"
  echo "  4. Copy contents of librechat-docker-compose-portainer.yaml"
  echo "  5. Deploy!"
else
  echo "Error: librechat-docker-compose.yaml not found"
  exit 1
fi






