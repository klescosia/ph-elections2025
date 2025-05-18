import os
import shutil

OUTPUT_DIR  = "output"      # where the data is stored
ARCHIVE_DIR = "data"    # output folder of the gzipped file
ARCHIVE_FMT = "gztar"       # 'gztar' for .tar.gz


os.makedirs(ARCHIVE_DIR, exist_ok=True)

for region in os.listdir(OUTPUT_DIR):
    region_path = os.path.join(OUTPUT_DIR, region)
    if not os.path.isdir(region_path):
        continue
    
    archive_name = os.path.join(ARCHIVE_DIR, f"{region}")

    archive_path = shutil.make_archive(archive_name, ARCHIVE_FMT, root_dir=region_path)
    print(f"Created archive for region {region}: {archive_path}")