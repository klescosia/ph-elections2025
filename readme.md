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

## Raising Issues

Thanks for checking out the repository. If you run into bugs, missing data, or have feature requests, please let me know by opening an issue. To make it easier for me to reproduce and fix the problem, please follow these guidelines:

---

### 1 – Choose the Right Category  
- **Bug** – Something isn’t working as expected (errors, missing files, wrong CSV fields).  
- **Enhancement** – A new feature or improvement (new output format, logging tweaks, performance).  
- **Question** – Clarifications about usage, configuration, or internals.

When you click **New Issue**, select the matching label above.

---

### 2 – Write a Clear Title  
Use a short, descriptive title that summarizes the problem:

Bug: precinct fetch fails for barangay code 3901000
Enhancement: allow setting custom output directory

---

### 3 – Describe the Problem  
- **What you expected** – e.g. “I expected `main.py` to skip already-downloaded precincts.”  
- **What actually happened** – e.g. “It fetched the same precinct again and overwrote the CSV.”  

Please include logs, errors codes, stack traces, and other information as it will help me and others identify the issue that you are encountering.

---

### 4 – Provide Steps to Reproduce  
List the exact steps you took. For example:  
1. Clone the repo at `commit abc123`  
2. Create a venv, install `httpx`  
3. Run `python main.py`  
4. Observe that `output/NCR/.../123456.csv` is not written  

---

### 5 – Include Environment Details  
- Operating system & version (macOS 12, Ubuntu 22.04, Windows 11)  
- Python version (`python --version`)  
- HTTPX version (`pip show httpx`)  
- Any special flags or config you used  

---

### 6 – Attach Logs or Screenshots  
If you saw error messages or stack traces, please please paste them in a code block:  
```txt
2025-05-30 10:15:20 ERROR Failed to fetch https://…/123.json: 404 Client Error
```

It will greatly help me and others debug your code.

---

### ✅ Good Issue Example

```
Title - Bug when fetching precinct data

Description -  
When fetching precinct data for barangay code R001000 the script fails with a 404 error instead of skipping that precinct and continuing.

Steps to Reproduce -  
1 Create and activate a virtual environment  
2 Install dependencies with pip install -r requirements.txt  
3 Run python main.py  
4 Observe that precinct 3901000 triggers a 404 and stops the crawler

Expected Behavior -  
The script should log the 404, skip that precinct, update the checkpoint, and continue with the next precinct

Actual Behavior -  
The crawler stops execution on the 404 error and does not process any further precincts

Environment -  
- Python version - 3.10.4  
- OS - Ubuntu 22.04  
- httpx version - 0.23.3  

Logs or Screenshots -  
2025-06-01 12-00-00 ERROR Failed to fetch https---2025electionresults.comelec.gov.ph/data/er/390/3901000.json 404 Client Error


Additional Context -
This happens consistently for any precinct code under that barangay and prevents completion of the crawl
```

### ❌ Bad Issue Example

```
Title - It does not work

Description -

The script fails

Steps to Reproduce -

Run the code

Expected Behavior -

It should work

Actual Behavior -

It does not

Environment -

Not sure

Logs or Screenshots -

No logs available
```

--- 

