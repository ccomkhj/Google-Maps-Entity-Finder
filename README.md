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
- Phone numbers are now included in output if available

## Code Structure Change

- The main backend logic file has been renamed from `mcp_integration.py` to `place_search.py` to better reflect its purpose. Update any imports or references accordingly.

## Prerequisites

- Python 3.6+
- Google Maps API key with **Places API** enabled
  - You need to enable the Places API in your Google Cloud Console
  - This project specifically uses the Places API to search for entities matching keywords

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/ccomkhj/Google-Maps-Entity-Finder.git
   cd Google-Maps-Entity-Finder
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
python main.py --lat1 <latitude1> --lng1 <longitude1> --lat2 <latitude2> --lng2 <longitude2> --keyword <search_keyword> [--output <output_file>] [--api-key <api_key>] [--type <place_type>]
```

#### Type Filtering
- `--type <place_type>`: Restricts results to a single place type (e.g., `hospital`).
    - If multiple types are provided with a pipe (`|`), only the first is used (e.g., `hospital|pharmacy|doctor` becomes `hospital`).
    - If a comma (`,`) is present, the type is ignored entirely.
    - Only one type is supported by the API.

#### Phone Numbers in Output
- If available, each place result will now include a `phone_number` field in the output JSON. This requires an additional API call per place and may slow down searches for large result sets.

#### Arguments:
- `--lat1` (float, required): Latitude of the first point
- `--lng1` (float, required): Longitude of the first point
- `--lat2` (float, required): Latitude of the second point
- `--lng2` (float, required): Longitude of the second point
- `--keyword` (str, required): Keyword to search for (e.g., "erdbeer", "coffee", "restaurant")
- `--type` (str, optional): Restrict results to a single place type (see above for details)
- `--output` (str, required): Path to save the results as a JSON file
- `--api-key` (str, optional): Google Maps API key (if not provided in .env file)
- `--radius` (float, optional): Maximum search radius in kilometers (default: 50.0)
- `--max-results` (int, optional): Maximum number of results to return (default: 200)
- `--buffer` (float, optional): Width tolerance around path in kilometers (default: 5.0)
- `--verbose` (flag, optional): Show detailed search information

### Example

```bash
# Search for "erdbeer" (strawberry) places between two points with a type filter
python main.py \
  --lat1 49.49607309173976 \
  --lng1 11.0552694512119 \
  --lat2 49.48592739050204 \
  --lng2 11.075283833840167 \
  --keyword "erdbeer" \
  --type "food" \
  --output "erdbeer_places.json"
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

## Example

```bash
bash example.bash
```

## Logging

```
2025-05-01 14:44:45.776 | INFO     | __main__:main:106 - Type filter set to: 'food' (valid)
2025-05-01 14:44:45.783 | INFO     | __main__:main:153 - Searching for 'erdbeer' between points...
2025-05-01 14:44:45.783 | INFO     | place_search:_direct_api_search:122 - Search radius: 0.92 km
2025-05-01 14:47:27.429 | INFO     | place_search:_direct_api_search:142 - Initial search: 161.65s
2025-05-01 14:47:27.430 | DEBUG    | place_search:_direct_api_search:150 - Processing 1 results
2025-05-01 14:47:27.535 | INFO     | place_search:_direct_api_search:195 - Found 1 results in 161.75s
2025-05-01 14:47:27.536 | INFO     | __main__:main:168 - Results saved to erdbeer_places.json
2025-05-01 14:47:27.537 | INFO     | __main__:main:173 - Found 1 matching places
Search complete! Results saved to erdbeer_places.json
```


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
