#!/bin/bash
# Update librechat.yaml in the librechat_data volume
# This file will be copied to /app/librechat.yaml by the entrypoint

VOLUME_NAME="librechat_librechat_data"
SOURCE_FILE="/Users/bee/Sync/Antigravity/ai/librechat.yaml"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file not found: $SOURCE_FILE"
    exit 1
fi

echo "Updating librechat.yaml in volume: $VOLUME_NAME"
docker run --rm -v $VOLUME_NAME:/data -v "$(dirname $SOURCE_FILE):/source" alpine sh -c "cp /source/$(basename $SOURCE_FILE) /data/librechat.yaml && ls -la /data/librechat.yaml && echo 'File updated successfully'"

echo ""
echo "Next steps:"
echo "1. Update your Portainer stack with the new docker-compose file"
echo "2. The entrypoint will copy the file from /app/librechat_data/librechat.yaml to /app/librechat.yaml on startup"
echo "3. Restart the librechat-api container"





