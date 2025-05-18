# Elections 2025 Data Crawler

## Overview -
This script gets data from the Comelec website and saves precinct-level election results as CSV files organized by region, province, city, barangay, and precincts.


## Approach -
The crawler steps through the site’s data: it first fetches all regions, then for each region fetches its provinces, then cities, then barangays, and finally precinct IDs. For each precinct it downloads the detailed vote counts and writes them to a CSV in the matching folder path. A small checkpoint file records the last precinct processed so you can stop and restart without losing progress.

## How the API Works -
1. Request `…/regions/local/0.json` to get all region codes.  
2. For each region, request `…/regions/local/{region_code}.json` to list its provinces.  
3. For each province, request `…/regions/local/{province_code}.json` to list its cities.  
4. For each city, request `…/regions/local/{city_code}.json` to list its barangays.  
5. For each barangay, request `…/regions/precinct/{prefix}/{barangay_code}.json` to get precinct IDs.  
6. For each precinct ID, request `…/data/er/{prefix}/{precinct_id}.json` to fetch vote details.

## Requirements -
- Python 3.8 or later

## Installation -
1. Clone the repository  
2. (Recommended) Create and activate a virtual environment  
   ```bash
   python3 -m venv venv
   source venv/bin/activate

## Usage -
Run `python main.py`  
Data will be saved under the `output` folder