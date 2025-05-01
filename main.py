#!/usr/bin/env python3
"""
Google Maps Entity Finder (Optimized)

This script finds entities matching a keyword between two geographic points
using the Google Maps API with optional MCP integration.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv
from loguru import logger

# Import the optimized search class
from place_search import GoogleMapsPlaceSearch

# Load environment variables from .env file
load_dotenv()

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate latitude and longitude values."""
    return -90 <= lat <= 90 and -180 <= lng <= 180

def format_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found"
    
    output = []
    for idx, place in enumerate(results, 1):
        output.append(
            f"{idx}. {place.get('name', 'Unknown')}\n"
            f"   Location: {place['location']['lat']:.6f}, {place['location']['lng']:.6f}\n"
            f"   Address: {place.get('address', 'N/A')}\n"
            f"   Rating: {place.get('rating', 'N/A')}\n"
            f"   Types: {', '.join(place.get('types', []))}"
        )
    return "\n\n".join(output)

def main():
    """Main function to parse arguments and execute the search."""
    parser = argparse.ArgumentParser(
        description='Find entities between two geographic points',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument('--keyword', type=str, help='Search term (e.g. "coffee")')
    parser.add_argument('--lat1', type=float, help='Latitude of first point (-90 to 90)')
    parser.add_argument('--lng1', type=float, help='Longitude of first point (-180 to 180)')
    parser.add_argument('--lat2', type=float, help='Latitude of second point (-90 to 90)')
    parser.add_argument('--lng2', type=float, help='Longitude of second point (-180 to 180)')

    # Optional arguments
    parser.add_argument('--api-key', type=str, 
                      help='Google Maps API key (or set GOOGLE_MAPS_API_KEY env var)')
    parser.add_argument('--output', type=str, 
                      help='Output file path (JSON format)')
    parser.add_argument('--use-mcp', action='store_true', 
                      help='Use MCP integration if available')
    parser.add_argument('--mcp-server', type=str, 
                      help='MCP server URL (or set MCP_SERVER_URL env var)')
    parser.add_argument('--radius', type=float, default=50.0,
                      help='Maximum search radius in kilometers')
    parser.add_argument('--max-results', type=int, default=200,
                      help='Maximum number of results to return')
    parser.add_argument('--buffer', type=float, default=5.0,
                      help='Width tolerance around path in kilometers')
    parser.add_argument('--verbose', action='store_true',
                      help='Show detailed search information')
    parser.add_argument('--type', type=str, default=None,
                      help='Restrict results to a single place type (e.g. hospital, pharmacy). Only one type allowed. If multiple types provided with |, only the first is used. Comma-separated types are ignored.')

    args = parser.parse_args()

    # Import valid place types from config
    from config import VALID_PLACE_TYPES

    # Validate type argument
    place_type = None
    input_type_valid = True
    if args.type:
        if ',' in args.type:
            logger.info("Error: Comma-separated types are not allowed. Only a single type or pipe-separated list is accepted. Ignoring type filter.")
            place_type = None
            input_type_valid = False
        elif '|' in args.type:
            place_type = args.type.split('|')[0].strip()
            if not place_type:
                place_type = None
                input_type_valid = False
        else:
            place_type = args.type.strip()
            if not place_type:
                place_type = None
                input_type_valid = False
        # Validate against known types (case-insensitive)
        if place_type and place_type.lower() not in [t.lower() for t in VALID_PLACE_TYPES]:
            logger.info(f"Warning: '{place_type}' is not a recognized Google Maps Place Type. Results may be empty or API may error.")
            logger.info(f"Some valid types: {', '.join(VALID_PLACE_TYPES[:10])} ... (see Google Maps docs for full list)")
            input_type_valid = False
        elif place_type:
            logger.info(f"Type filter set to: '{place_type}' (valid)")
        else:
            logger.info("No valid type filter applied.")
    else:
        logger.info("No type filter applied.")
    if args.type and not input_type_valid:
        logger.info("See https://developers.google.com/maps/documentation/places/web-service/supported_types for all valid types.")

    # Validate coordinates
    if not all(validate_coordinates(*coord) for coord in [(args.lat1, args.lng1), (args.lat2, args.lng2)]):
        logger.info("Error: Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180.")
        sys.exit(1)

    # Get API key
    api_key = args.api_key or os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        logger.info("Error: API key required. Set GOOGLE_MAPS_API_KEY or use --api-key")
        sys.exit(1)

    # Configure MCP
    mcp_server_url = None
    if args.use_mcp:
        mcp_server_url = args.mcp_server or os.getenv('MCP_SERVER_URL')
        if not mcp_server_url and args.verbose:
            logger.info("Warning: MCP requested but no server URL provided")

    # Show type in verbose output
    if args.verbose and args.type:
        logger.info(f"  Type filter: {place_type if place_type else 'None (invalid or ignored)'}")

    try:
        # Initialize client
        client = GoogleMapsPlaceSearch(api_key, mcp_server_url)
        point1 = (args.lat1, args.lng1)
        point2 = (args.lat2, args.lng2)

        if args.verbose:
            logger.info(f"\nSearch Configuration:")
            logger.info(f"  Keyword: {args.keyword}")
            logger.info(f"  Point A: {point1}")
            logger.info(f"  Point B: {point2}")
            logger.info(f"  Max radius: {args.radius} km")
            logger.info(f"  Path buffer: {args.buffer} km")
            logger.info(f"  Max results: {args.max_results}")
            logger.info(f"  Using MCP: {'Yes' if mcp_server_url else 'No'}")

        # Execute search
        logger.info(f"\nSearching for '{args.keyword}' between points...")
        results = client.search_between_points(
            keyword=args.keyword,
            point1=point1,
            point2=point2,
            radius_km=args.radius,
            max_results=args.max_results,
            buffer_km=args.buffer,
            place_type=place_type
        )

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"\nResults saved to {args.output}")
        
        if args.verbose or not args.output:
            logger.info(f"\n{format_results(results)}")
        
        logger.info(f"\nFound {len(results)} matching places")

    except Exception as e:
        logger.info(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()