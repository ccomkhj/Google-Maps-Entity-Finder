#!/bin/bash

# Example script for using Google Maps Entity Finder
# This example searches for "erdbeer" (strawberry) places between Berlin and Munich

# Run the search
python main.py \
  --lat1 49.49607309173976 \
  --lng1 11.0552694512119 \
  --lat2 49.48592739050204 \
  --lng2 11.075283833840167 \
  --keyword "erdbeer" \
  --type "food" \
  --output "erdbeer_places.json"

echo "Search complete! Results saved to erdbeer_places.json"