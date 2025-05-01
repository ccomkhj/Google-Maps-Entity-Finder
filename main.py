#!/usr/bin/env python3
"""
Google Maps Entity Finder

This script finds entities matching a keyword between two geographic points
using the Google Maps API with optional MCP integration.
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv

# Import MCP integration
from mcp_integration import MCPGoogleMapsClient

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to parse arguments and execute the search"""
    parser = argparse.ArgumentParser(description='Find entities matching a keyword between two geographic points')
    parser.add_argument('--lat1', type=float, required=True, help='Latitude of first point')
    parser.add_argument('--lng1', type=float, required=True, help='Longitude of first point')
    parser.add_argument('--lat2', type=float, required=True, help='Latitude of second point')
    parser.add_argument('--lng2', type=float, required=True, help='Longitude of second point')
    parser.add_argument('--keyword', type=str, required=True, help='Keyword to search for')
    parser.add_argument('--api-key', type=str, help='Google Maps API key (or set GOOGLE_MAPS_API_KEY env var)')
    parser.add_argument('--output', type=str, help='Output file path (JSON format)')
    parser.add_argument('--use-mcp', action='store_true', help='Use MCP integration if available')
    parser.add_argument('--mcp-server', type=str, help='MCP server URL (or set MCP_SERVER_URL env var)')
    parser.add_argument('--radius', type=float, default=50.0, help='Search radius in kilometers (default: 50)')
    parser.add_argument('--max-results', type=int, default=100, help='Maximum number of results (default: 100)')
    
    args = parser.parse_args()
    
    # Get API key from args or environment variable
    api_key = args.api_key or os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("Error: Google Maps API key is required. Provide it via --api-key or set GOOGLE_MAPS_API_KEY environment variable.")
        sys.exit(1)

    # Define the two points
    point1 = (args.lat1, args.lng1)
    point2 = (args.lat2, args.lng2)
    
    # Get MCP server URL if use-mcp is specified
    mcp_server_url = None
    if args.use_mcp:
        mcp_server_url = args.mcp_server or os.getenv('MCP_SERVER_URL')
    
    try:
        # Initialize the client
        client = MCPGoogleMapsClient(api_key, mcp_server_url)
        
        # Search for places
        print(f"Searching for '{args.keyword}' between points {point1} and {point2}...")
        if mcp_server_url:
            print(f"Using MCP server at {mcp_server_url}")
        else:
            print("Using direct Google Maps API")
        
        results = client.search_places_between_points(
            args.keyword,
            point1,
            point2,
            args.radius,
            args.max_results
        )
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=2))
        
        print(f"Found {len(results)} places matching '{args.keyword}' between the specified points.")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()