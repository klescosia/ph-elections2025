import csv
import os
import shutil
import logging
import json
from datetime import datetime

def save_precinct_result_to_csv(precinct_json, output_path):
    """
    Write a single precinct’s JSON result into a CSV at output_path
    """
    if not precinct_json or "information" not in precinct_json:
        logging.warning(f"Skipped writing due to missing information in JSON for {output_path}")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rows = []

    for scope in ("national", "local"):
        for contest in precinct_json.get(scope, []):
            cname = contest.get("contestName", "")
            for cand in contest.get("candidates", {}).get("candidates", []):
                rows.append({
                    "precinct_code": precinct_json["information"].get("precinctId", ""),
                    "location": precinct_json["information"].get("location", ""),
                    "voting_center": precinct_json["information"].get("votingCenter", ""),
                    "scope": scope,
                    "contest_name": cname,
                    "candidate_name": cand.get("name", "").strip(),
                    "votes": cand.get("votes", 0),
                    "percentage": cand.get("percentage", 0.0),
                })

    if not rows:
        return

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def get_completed_precincts(base_dir="output"):
    """
    Walk output/ and collect all precinct_codes for which a CSV already exists.
    """
    completed = set()
    for root, _, files in os.walk(base_dir):
        for fname in files:
            if fname.endswith(".csv"):
                completed.add(os.path.splitext(fname)[0])
    return completed

def organize_existing_csvs(output_dir="output"):
    """
    Moves any loose CSVs (depth <4) into the proper nested folders based on their location metadata.
    """
    logging.info(f"Starting CSV reorganization in {output_dir}")
    for root, _, files in os.walk(output_dir):
        for f in files:
            if not f.endswith(".csv"):
                continue
            rel = os.path.relpath(root, output_dir)
            if rel != "." and len(rel.split(os.sep)) >= 4:
                continue

            src = os.path.join(root, f)
            try:
                with open(src, encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    first = next(reader, None)
                if not first or "location" not in first:
                    continue

                parts = [p.strip().replace(" ", "_") for p in first["location"].split(",")]
                if len(parts) < 4:
                    continue

                region, province, city, barangay = parts[:4]
                dest_dir = os.path.join(output_dir, region, province, city, barangay)
                os.makedirs(dest_dir, exist_ok=True)
                dest = os.path.join(dest_dir, f)
                if src != dest:
                    shutil.move(src, dest)
                    logging.info(f"Organized {f} → {dest}")
            except Exception as e:
                logging.warning(f"Could not organize {f}: {e}")
    logging.info("CSV reorganization complete")

def write_checkpoint(metadata: dict, precinct_code: str, checkpoint_file: str = "checkpoint.json"):
    """
    Overwrite checkpoint_file with the latest processed location hierarchy and precinct.
    """
    checkpoint = {
        "region":   {"code": metadata.get("region_code"),   "name": metadata.get("region")},
        "province": {"code": metadata.get("province_code"), "name": metadata.get("province")},
        "city":     {"code": metadata.get("city_code"),     "name": metadata.get("city")},
        "barangay": {"code": metadata.get("barangay_code"), "name": metadata.get("barangay")},
        "precinct": {"code": precinct_code},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    try:
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2)
        logging.info(f"Checkpoint updated: {checkpoint_file}")
    except Exception as e:
        logging.warning(f"Failed to write checkpoint: {e}")