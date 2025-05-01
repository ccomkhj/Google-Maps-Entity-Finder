"""
MCP Integration for Google Maps Entity Finder

This module provides integration with the Model Context Protocol (MCP) for Google Maps,
allowing for more advanced context-aware searches and improved result filtering.
"""

import os
import requests
from typing import Dict, List, Tuple, Any, Optional
from loguru import logger

class MCPGoogleMapsClient:
    """Client for interacting with the Google Maps MCP server"""
    
    def __init__(self, api_key: str, mcp_server_url: Optional[str] = None):
        """
        Initialize the MCP Google Maps client
        
        Args:
            api_key: Google Maps API key
            mcp_server_url: URL of the MCP server (default: None, will use direct Google Maps API)
        """
        self.api_key = api_key
        self.mcp_server_url = mcp_server_url
        self.use_mcp = self.mcp_server_url is not None
        self.gmaps_client = None
        
        # Initialize Google Maps client as fallback
        try:
            import googlemaps
            self.gmaps_client = googlemaps.Client(key=api_key)
        except ImportError:
            if not self.use_mcp:
                raise ImportError(
                    "googlemaps package is required when not using MCP. "
                    "Please install it with 'pip install googlemaps'"
                )
            # If using MCP, we'll just warn and handle failures later
            print("Warning: googlemaps package not installed. MCP failures won't have fallback.")
        except Exception as e:
            print(f"Warning: Error initializing Google Maps client: {e}")
    
    def search_places_between_points(
        self, 
        keyword: str, 
        point1: Tuple[float, float], 
        point2: Tuple[float, float],
        radius_km: float = 50.0,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for places matching a keyword between two geographic points using MCP
        
        Args:
            keyword: Keyword to search for
            point1: First point (latitude, longitude)
            point2: Second point (latitude, longitude)
            radius_km: Search radius in kilometers
            max_results: Maximum number of results to return
            
        Returns:
            List of places matching the search criteria
        """
        if self.use_mcp:
            try:
                return self._search_with_mcp(keyword, point1, point2, radius_km, max_results)
            except Exception as e:
                print(f"MCP search failed: {e}")
                if self.gmaps_client is None:
                    raise RuntimeError("MCP search failed and no fallback Google Maps client available")
                print("Falling back to direct Google Maps API...")
        
        if self.gmaps_client is None:
            raise RuntimeError("No Google Maps client available for search")
            
        return self._search_with_direct_api(keyword, point1, point2, radius_km, max_results)
    
    def _search_with_mcp(
        self, 
        keyword: str, 
        point1: Tuple[float, float], 
        point2: Tuple[float, float],
        radius_km: float,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Search using the MCP server
        """
        # Prepare the MCP request
        mcp_request = {
            "query": {
                "type": "places_between_points",
                "keyword": keyword,
                "point1": {
                    "lat": point1[0],
                    "lng": point1[1]
                },
                "point2": {
                    "lat": point2[0],
                    "lng": point2[1]
                },
                "radius_km": radius_km,
                "max_results": max_results
            },
            "api_key": self.api_key
        }
        
        # Send request to MCP server
        try:
            response = requests.post(
                f"{self.mcp_server_url}/query",
                json=mcp_request,
                headers={"Content-Type": "application/json"},
                timeout=30  # Add timeout to prevent hanging indefinitely
            )
            response.raise_for_status()
            
            # Parse and return results
            result_data = response.json()
            if "error" in result_data:
                raise ValueError(f"MCP server error: {result_data['error']}")
                
            return result_data.get("results", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to MCP server: {e}")
            logger.info("Falling back to direct Google Maps API...")
            return self._search_with_direct_api(keyword, point1, point2, radius_km, max_results)
    
    def _search_with_direct_api(
        self, 
        keyword: str, 
        point1: Tuple[float, float], 
        point2: Tuple[float, float],
        radius_km: float,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Search using the direct Google Maps API (fallback method)
        """
        logger.info(f"Starting direct API search for '{keyword}' between points {point1} and {point2}")
        
        # Check if gmaps_client is available and initialize it if needed
        if self.gmaps_client is None:
            try:
                import googlemaps
                logger.debug("Initializing Google Maps client")
                self.gmaps_client = googlemaps.Client(key=self.api_key)
            except ImportError:
                logger.error("Google Maps client not initialized. Make sure the googlemaps package is installed.")
                return []
            except Exception as e:
                logger.error(f"Error initializing Google Maps client: {e}")
                return []
        
        from math import radians, cos, sin, asin, sqrt
        import time
        
        def haversine(lon1, lat1, lon2, lat2):
            """Calculate the great circle distance between two points"""
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1 
            dlat = lat2 - lat1 
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a)) 
            r = 6371  # Radius of earth in kilometers
            return c * r
        
        # Calculate direct distance between points once
        direct_dist = haversine(point1[1], point1[0], point2[1], point2[0])
        logger.info(f"Direct distance between points: {direct_dist:.2f} km")
        
        def is_between_points(point, point1, point2, buffer_km=5.0):
            """Check if a point is between two other points with a buffer"""
            lat, lng = point.get('lat'), point.get('lng')
            if lat is None or lng is None:
                return False
            
            dist_to_point1 = haversine(lng, lat, point1[1], point1[0])
            dist_to_point2 = haversine(lng, lat, point2[1], point2[0])
            
            # Check if point is near the path between point1 and point2
            is_near_path = dist_to_point1 + dist_to_point2 <= direct_dist + buffer_km
            return is_near_path
        
        # For small areas, use a more efficient approach with targeted searches
        results = []
        processed_place_ids = set()  # Track processed places to avoid duplicates
        
        # Calculate search radius based on the distance between points
        distance_km = direct_dist
        logger.info(f"Calculating search radius. Distance between points: {distance_km:.2f} km")
        
        # If distance is very small, use a minimum radius to ensure we get results
        min_radius = 1000  # 1 km in meters
        max_radius = 50000  # 50 km in meters (Google Maps API limit)
        
        # Calculate radius in meters, ensuring it's at least 1 km and at most 50 km
        radius = max(min_radius, min(max_radius, int(min(radius_km, distance_km) * 1000)))
        logger.info(f"Using search radius of {radius} meters")
        
        # For small areas, we'll do a single search at the midpoint
        mid_lat = (point1[0] + point2[0]) / 2
        mid_lng = (point1[1] + point2[1]) / 2
        
        logger.info(f"Performing nearby search at midpoint ({mid_lat}, {mid_lng}) with radius {radius}m")
        search_start_time = time.time()
        
        try:
            # Perform nearby search
            places_result = self.gmaps_client.places_nearby(
                location=(mid_lat, mid_lng),
                radius=radius,
                keyword=keyword
            )
            logger.debug(f"Initial search returned {len(places_result.get('results', []))} results")
        except Exception as e:
            logger.error(f"Error querying Google Maps API: {e}")
            return []
        
        # Process results
        if 'results' in places_result:
            logger.info(f"Processing {len(places_result['results'])} results from initial search")
            for place in places_result['results']:
                if 'geometry' in place and 'location' in place['geometry']:
                    location = place['geometry']['location']
                    place_id = place.get('place_id', '')
                    
                    # Skip if we've already processed this place
                    if place_id in processed_place_ids:
                        continue
                    
                    processed_place_ids.add(place_id)
                    
                    # Check if place is between or near the path between the two points
                    if is_between_points(location, point1, point2):
                        logger.debug(f"Found matching place: {place.get('name', 'Unknown')}")
                        results.append({
                            'name': place.get('name', 'Unknown'),
                            'place_id': place_id,
                            'address': place.get('vicinity', 'No address'),
                            'location': location,
                            'rating': place.get('rating', 'No rating'),
                            'types': place.get('types', [])
                        })
        
        # Handle pagination if there are more results
        page_count = 1
        while 'next_page_token' in places_result and len(results) < max_results:
            page_count += 1
            logger.info(f"Fetching page {page_count} of results using next_page_token")
            
            # Wait for token to be valid - Google requires a delay
            # Start with a shorter wait time and only increase if needed
            wait_time = 1.5  # seconds
            
            try:
                time.sleep(wait_time)
                places_result = self.gmaps_client.places_nearby(
                    page_token=places_result['next_page_token']
                )
                logger.debug(f"Page {page_count} returned {len(places_result.get('results', []))} results")
            except Exception as e:
                logger.error(f"Error fetching page {page_count}: {e}")
                # If we get an error about the token not being ready, wait longer and retry once
                if 'Invalid request' in str(e) and wait_time < 2.5:
                    logger.info("Token may not be ready yet, waiting longer and retrying")
                    time.sleep(1.5)  # Additional wait
                    try:
                        places_result = self.gmaps_client.places_nearby(
                            page_token=places_result['next_page_token']
                        )
                        logger.debug(f"Retry successful, got {len(places_result.get('results', []))} results")
                    except Exception as retry_e:
                        logger.error(f"Retry also failed: {retry_e}")
                        break
                else:
                    break
            
            if 'results' in places_result:
                logger.info(f"Processing {len(places_result['results'])} results from page {page_count}")
                for place in places_result['results']:
                    if 'geometry' in place and 'location' in place['geometry']:
                        location = place['geometry']['location']
                        place_id = place.get('place_id', '')
                        
                        # Skip if we've already processed this place
                        if place_id in processed_place_ids:
                            continue
                        
                        processed_place_ids.add(place_id)
                        
                        if is_between_points(location, point1, point2):
                            logger.debug(f"Found matching place: {place.get('name', 'Unknown')}")
                            results.append({
                                'name': place.get('name', 'Unknown'),
                                'place_id': place_id,
                                'address': place.get('vicinity', 'No address'),
                                'location': location,
                                'rating': place.get('rating', 'No rating'),
                                'types': place.get('types', [])
                            })
                            
                            if len(results) >= max_results:
                                logger.info(f"Reached max_results limit of {max_results}")
                                break
    
        search_duration = time.time() - search_start_time
        logger.info(f"Search completed in {search_duration:.2f} seconds, found {len(results)} matching places")
        return results[:max_results]
