import logging

BASE_URL = "https://2025electionresults.comelec.gov.ph/data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def fetch_json(client, url):
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.warning(f"Failed to fetch {url}: {e}")
        return None

async def fetch_regions(client):
    return await fetch_json(client, f"{BASE_URL}/regions/local/0.json")

async def fetch_provinces(client, region_code):
    return await fetch_json(client, f"{BASE_URL}/regions/local/{region_code}.json")

async def fetch_cities(client, province_code):
    return await fetch_json(client, f"{BASE_URL}/regions/local/{province_code}.json")

async def fetch_barangays(client, city_code):
    return await fetch_json(client, f"{BASE_URL}/regions/local/{city_code}.json")

async def fetch_precincts(client, barangay_code):
    prefix = barangay_code[:2]
    return await fetch_json(client, f"{BASE_URL}/regions/precinct/{prefix}/{barangay_code}.json")

async def fetch_precinct_result(client, precinct_code):
    prefix = precinct_code[:3]
    return await fetch_json(client, f"{BASE_URL}/er/{prefix}/{precinct_code}.json")