#!/bin/bash

# Requires numpy to be installed globally

# Step 0: Remove old files
echo "Step 0: Remove old files"
rm -f ./data.json{,.offset}
rm -f data-1k.json

# Step 1: Generate new data
echo "Step 1: Generate new data"
python3 generate_json.py

# Step 2: Replace metadata
echo "Step 2: Replace metadata"
COUNT=$(wc -l data.json | awk '{print $1}')
echo "Step 2.1: document-count: $COUNT"
sed -i 's/"document-count": [0-9]\+/"document-count": '"$COUNT"'/' track.json

UNCOMPRESSED_BYTES=$(stat -c %s data.json)
echo "Step 2.2: uncompressed-bytes: $UNCOMPRESSED_BYTES"
sed -i 's/"uncompressed-bytes": [0-9]\+/"uncompressed-bytes": '"$UNCOMPRESSED_BYTES"'/' track.json

# Step 3: Support --test-mode
echo "Step 3: Support --test-mode"
head -n 1000 data.json > data-1k.json

echo "Feel free to use!"
