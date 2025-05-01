# Google Maps Entity Finder

**Geo-targeted prospecting for sales and business development!**

This Python project helps you find businesses or points of interest matching a keyword between two geographic points using the Google Maps API. It is especially useful for sales professionals, business developers, or anyone who needs to search for leads or opportunities along a travel route or within a specific geographic corridor.

## Why Use This Module?
- **Sales prospecting:** Identify potential clients or partners along your planned travel route or within a target region.
- **Territory planning:** Optimize your sales routes by focusing on relevant businesses between destinations.
- **Market research:** Quickly analyze the distribution of business types (e.g., coffee shops, gas stations, clinics) between two points.

## Use Cases
- A field sales rep wants to find all potential clients (e.g., bakeries, clinics, retailers) between two cities for efficient trip planning.
- A business analyst needs to map out competitors or partners along a highway or transit corridor.
- Logistics and delivery teams want to identify useful stops or service providers en route.


## Features

- Search for places matching a specific keyword (e.g., "erdbeer", "coffee", "gas station")
- Filter results to only include places located between two geographic points
- Output results in JSON format (either to stdout or to a file)
- Configurable search radius and buffer distance

## Prerequisites

- Python 3.6+
- Google Maps API key with **Places API** enabled
  - You need to enable the Places API in your Google Cloud Console
  - This project specifically uses the Places API to search for entities matching keywords

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd google_maps_finder
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Google Maps API key:
   - Copy the `.env.example` file to `.env`:
     ```
     cp .env.example .env
     ```
   - Edit the `.env` file and replace `your_api_key_here` with your actual Google Maps API key

## Usage

### Command Line Interface

```bash
python main.py --lat1 <latitude1> --lng1 <longitude1> --lat2 <latitude2> --lng2 <longitude2> --keyword <search_keyword> [--output <output_file>] [--api-key <api_key>]
```

#### Required Arguments:
- `--lat1`: Latitude of the first point
- `--lng1`: Longitude of the first point
- `--lat2`: Latitude of the second point
- `--lng2`: Longitude of the second point
- `--keyword`: Keyword to search for (e.g., "erdbeer", "coffee", "restaurant")

#### Optional Arguments:
- `--output`: Path to save the results as a JSON file
- `--api-key`: Google Maps API key (if not provided in .env file)

### Example

```bash
# Search for "erdbeer" (strawberry) places between Berlin and Munich
python main.py --lat1 52.5200 --lng1 13.4050 --lat2 48.1351 --lng2 11.5820 --keyword "erdbeer" --output results.json
```

## How It Works

1. The script calculates the midpoint between the two specified geographic points
2. It determines an appropriate search radius based on the distance between the points
3. It queries the Google Maps Places API for entities matching the keyword
4. It filters the results to only include places that are between or near the path between the two points
5. The filtered results are returned in JSON format

## MCP Integration

This project can be extended to use the Model Context Protocol (MCP) for Google Maps if needed. The MCP integration would allow for more advanced context-aware searches and improved result filtering.

For MCP integration, refer to the [Google Maps MCP repository](https://github.com/modelcontextprotocol/servers/tree/main/src/google-maps).

## Output Format

The output is a JSON array of places, with each place containing:
- `name`: The name of the place
- `place_id`: Google Maps place ID
- `address`: Address or vicinity
- `location`: Geographic coordinates (latitude and longitude)
- `rating`: User rating (if available)
- `types`: Categories/types of the place

## License

This project is licensed under the MIT License - see the LICENSE file for details.
