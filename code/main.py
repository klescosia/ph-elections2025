import asyncio
import logging
import os
import json
import concurrent.futures

import httpx

from crawler import (
    fetch_regions,
    fetch_provinces,
    fetch_cities,
    fetch_barangays,
    fetch_precincts,
    fetch_precinct_result,
)
from write_utils import (
    save_precinct_result_to_csv,
    get_completed_precincts,
    organize_existing_csvs,
    write_checkpoint,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=16)

def load_checkpoint(path="checkpoint.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def build_output_path(metadata, precinct_code, base_dir="output"):
    return os.path.join(
        base_dir,
        metadata["region"].replace(" ", "_"),
        metadata["province"].replace(" ", "_"),
        metadata["city"].replace(" ", "_"),
        metadata["barangay"].replace(" ", "_"),
        f"{precinct_code}.csv",
    )

async def process_precinct(client, precinct_code, metadata, completed, sem, base_dir="output"):
    if precinct_code in completed:
        # even if skipping, bump the checkpoint so we know we passed it
        await asyncio.get_running_loop().run_in_executor(
            executor,
            write_checkpoint,
            metadata,
            precinct_code
        )
        logging.info(f"⏭️ Skipping {precinct_code} (already done)")
        return

    async with sem:
        result = await fetch_precinct_result(client, precinct_code)
        if not result:
            logging.warning(f"❌ No data for {precinct_code}")
            return

        out_path = build_output_path(metadata, precinct_code, base_dir)
        loop = asyncio.get_running_loop()

        # offload CSV write
        await loop.run_in_executor(
            executor,
            save_precinct_result_to_csv,
            result,
            out_path
        )
        logging.info(f"✅ Saved {precinct_code} → {out_path}")

        # offload checkpoint write
        await loop.run_in_executor(
            executor,
            write_checkpoint,
            metadata,
            precinct_code
        )

async def main():
    sem = asyncio.Semaphore(50)
    completed = get_completed_precincts("output")
    logging.info(f"🔄 {len(completed)} precincts already in output/")
    checkpoint = load_checkpoint()

    # flags for hierarchy resume
    resumed_region = resumed_province = resumed_city = resumed_barangay = resumed_precinct = False

    async with httpx.AsyncClient(timeout=30) as client:
        regions = await fetch_regions(client)
        if not regions:
            return

        for region in regions["regions"]:
            if checkpoint and not resumed_region:
                if region["code"] != checkpoint["region"]["code"]:
                    continue
                resumed_region = True

            provs = await fetch_provinces(client, region["code"])
            if not provs:
                continue

            for prov in provs["regions"]:
                if checkpoint and not resumed_province:
                    if prov["code"] != checkpoint["province"]["code"]:
                        continue
                    resumed_province = True

                cities = await fetch_cities(client, prov["code"])
                if not cities:
                    continue

                for city in cities["regions"]:
                    if checkpoint and not resumed_city:
                        if city["code"] != checkpoint["city"]["code"]:
                            continue
                        resumed_city = True

                    bars = await fetch_barangays(client, city["code"])
                    if not bars:
                        continue

                    for bar in bars["regions"]:
                        if checkpoint and not resumed_barangay:
                            if bar["code"] != checkpoint["barangay"]["code"]:
                                continue
                            resumed_barangay = True

                        precs = await fetch_precincts(client, bar["code"])
                        if not precs:
                            continue

                        meta = {
                            "region_code":   region["code"],
                            "region":        region["name"],
                            "province_code": prov["code"],
                            "province":      prov["name"],
                            "city_code":     city["code"],
                            "city":          city["name"],
                            "barangay_code": bar["code"],
                            "barangay":      bar["name"],
                        }

                        for p in precs["regions"]:
                            if checkpoint and not resumed_precinct:
                                if p["code"] != checkpoint["precinct"]["code"]:
                                    continue
                                resumed_precinct = True
                                # don’t re-process that last checkpointed precinct
                                continue

                            await process_precinct(
                                client,
                                p["code"],
                                meta,
                                completed,
                                sem,
                            )

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    organize_existing_csvs("output")
    asyncio.run(main())