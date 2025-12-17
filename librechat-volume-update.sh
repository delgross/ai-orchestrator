#!/bin/bash
# Script to update the librechat.yaml file in the Docker volume

VOLUME_NAME="librechat-config"
SOURCE_FILE="/Users/bee/Sync/Antigravity/ai/librechat.yaml"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file not found: $SOURCE_FILE"
    exit 1
fi

echo "Updating librechat.yaml in Docker volume: $VOLUME_NAME"
docker run --rm -v $VOLUME_NAME:/data -v "$(dirname $SOURCE_FILE):/source" alpine sh -c "cp /source/$(basename $SOURCE_FILE) /data/librechat.yaml && ls -la /data/librechat.yaml && echo 'File updated successfully'"

echo ""
echo "To apply changes, restart the librechat-api container in Portainer"





