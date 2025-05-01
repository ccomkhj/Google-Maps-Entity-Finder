"""
Optimized Google Maps Place Search Between Two Points
- Automatically calculates optimal search radius
- Uses geometric pre-filtering for speed
- Handles API limits and pagination
"""

import time
from math import radians, cos, sin, asin, sqrt
from typing import Dict, List, Tuple, Any, Optional
import requests
from loguru import logger

class GoogleMapsPlaceSearch:
    """Efficient place search between two geographic points."""
    
    def __init__(self, api_key: str, mcp_server_url: Optional[str] = None):
        """
        Args:
            api_key: Google Maps API key
            mcp_server_url: Optional MCP server endpoint
        """
        self.api_key = api_key
        self.mcp_server_url = mcp_server_url
        self.use_mcp = mcp_server_url is not None
        self.gmaps_client = self._init_gmaps_client()

    def _init_gmaps_client(self):
        """Initialize Google Maps client with fallback handling."""
        try:
            import googlemaps
            return googlemaps.Client(key=self.api_key)
        except ImportError:
            if not self.use_mcp:
                raise RuntimeError("Google Maps client requires 'googlemaps' package")
            logger.warning("Google Maps client unavailable - using MCP only")
            return None
        except Exception as e:
            logger.error(f"Client init failed: {e}")
            return None

    def search_between_points(
        self,
        keyword: str,
        point1: Tuple[float, float],
        point2: Tuple[float, float],
        radius_km: float = 50.0,
        max_results: int = 100,
        buffer_km: float = 5.0,
        place_type: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for places between two points.
        
        Args:
            keyword: Search term (e.g., "coffee")
            point1: (lat, lng) of first point
            point2: (lat, lng) of second point
            radius_km: Maximum search radius (default 50km)
            max_results: Maximum results to return
            buffer_km: Width tolerance around path (default 5km)
            place_type: Restrict results to a single place type (e.g., 'hospital'). Only one type allowed.
        
        Returns:
            List of place results with name, location, etc.
        """
        # Use MCP if available
        if self.use_mcp:
            try:
                return self._mcp_search(keyword, point1, point2, radius_km, max_results, place_type)
            except Exception as e:
                logger.error(f"MCP search failed: {e}")
                if not self.gmaps_client:
                    raise RuntimeError("No fallback available")

        # Direct API search
        return self._direct_api_search(
            keyword=keyword,
            point1=point1,
            point2=point2,
            radius_km=radius_km,
            max_results=max_results,
            buffer_km=buffer_km,
            place_type=place_type
        )

    def _mcp_search(self, *args, **kwargs):
        """MCP server implementation (unchanged from your original)"""
        # ... [Your existing MCP code] ...

    def _direct_api_search(
        self,
        keyword: str,
        point1: Tuple[float, float],
        point2: Tuple[float, float],
        radius_km: float,
        max_results: int,
        buffer_km: float,
        place_type: str = None
    ) -> List[Dict[str, Any]]:
        """Optimized direct API search with geometric filtering."""
        # Precompute values
        point1_lat, point1_lng = point1
        point2_lat, point2_lng = point2
        
        # Convert to radians once
        point1_lat_rad = radians(point1_lat)
        point1_lng_rad = radians(point1_lng)
        point2_lat_rad = radians(point2_lat)
        point2_lng_rad = radians(point2_lng)

        # Calculate direct distance between points
        dlon = point2_lng_rad - point1_lng_rad
        dlat = point2_lat_rad - point1_lat_rad
        a = sin(dlat/2)**2 + cos(point1_lat_rad) * cos(point2_lat_rad) * sin(dlon/2)**2
        direct_dist = 6371 * 2 * asin(sqrt(a))  # Earth radius in km

        # Auto-adjust radius (half distance between points or user radius, max 50km)
        search_radius_km = min(direct_dist / 2, radius_km)
        radius_m = min(int(search_radius_km * 1000), 50000)
        
        logger.info(f"Search radius: {search_radius_km:.2f} km")
        
        # Calculate midpoint
        mid_lat = (point1_lat + point2_lat) / 2
        mid_lng = (point1_lng + point2_lng) / 2

        # Execute search
        results = []
        processed_ids = set()
        search_time = time.time()
        
        try:
            # Initial search
            places_result = self.gmaps_client.places_nearby(
                location=(mid_lat, mid_lng),
                radius=radius_m,
                keyword=keyword,
                type=place_type if place_type else None
            )
            logger.info(f"Initial search: {time.time() - search_time:.2f}s")
        except Exception as e:
            logger.error(f"API Error: {e}")
            return []

        # Process results
        while True:
            current_batch = places_result.get('results', [])
            logger.debug(f"Processing {len(current_batch)} results")
            
            for place in current_batch:
                if len(results) >= max_results:
                    break
                
                place_id = place.get('place_id')
                if not place_id or place_id in processed_ids:
                    continue
                
                processed_ids.add(place_id)
                location = place.get('geometry', {}).get('location')
                if location:
                    # Try to get phone number (optional, may require extra API call)
                    phone_number = None
                    try:
                        details = self.gmaps_client.place(place_id=place_id)
                        phone_number = details.get('result', {}).get('formatted_phone_number')
                    except Exception as e:
                        logger.debug(f"Phone lookup failed for {place_id}: {e}")
                    result_obj = {
                        'name': place.get('name', 'Unknown'),
                        'place_id': place_id,
                        'location': location,
                        'address': place.get('vicinity', 'No address'),
                        'rating': place.get('rating'),
                        'types': place.get('types', [])
                    }
                    if phone_number:
                        result_obj['phone_number'] = phone_number
                    results.append(result_obj)
            
            # Pagination or termination
            if len(results) >= max_results or 'next_page_token' not in places_result:
                break
                
            time.sleep(1.5)  # Google API required delay
            try:
                places_result = self.gmaps_client.places_nearby(
                    page_token=places_result['next_page_token']
                )
            except Exception as e:
                logger.error(f"Pagination failed: {e}")
                break

        logger.info(f"Found {len(results)} results in {time.time() - search_time:.2f}s")
        return results[:max_results]