#!/bin/bash

# Example script for using Google Maps Entity Finder with MCP integration
# This example searches for "restaurant" between Hamburg and Frankfurt

# Run the search with MCP integration
python main.py \
  --lat1 53.5511 \
  --lng1 9.9937 \
  --lat2 50.1109 \
  --lng2 8.6821 \
  --keyword "restaurant" \
  --use-mcp \
  --mcp-server "http://localhost:8080" \
  --output "restaurants.json"

echo "MCP-enhanced search complete! Results saved to restaurants.json"