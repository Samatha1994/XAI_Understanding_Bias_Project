"""
copy_final_results.py
=====================
Copies BeoCat results to a clean final folder.

Rules:
  - validation_results_* folders → copied as-is
  - neuron_activations_* folders → copied as-is EXCEPT
    neuron_*_output_file.txt files inside feature subfolders are excluded

USAGE:
    python copy_final_results.py
    python copy_final_results.py --dry-run   # preview without copying
"""

import os
import re
import shutil
import argparse
from datetime import datetime

# ============================================================
# CONFIG — edit these paths only
# ============================================================

SOURCE_ROOT = r"D:\BeoCat Results"
DEST_ROOT   = r"D:\BeoCat_final_Results"

DATASETS = [
    "patches_weedCrop",
    "patches_openSprayer",
    "patches_sugarcane",
    "patches_oxford",
    "patches_cassava",
]

# ============================================================
# HELPERS
# ============================================================

def ts():
    return datetime.now().strftime("%H:%M:%S")

def is_neuron_output_file(filename):
    """Returns True for files like neuron_42_output_file.txt"""
    return bool(re.match(r'^neuron_\d+_output_file\.txt$', filename))

def copy_tree_filtered(src, dst, dry_run=False):
    """
    Recursively copies src to dst.
    Skips neuron_*_output_file.txt files inside feature subfolders.
    """
    os.makedirs(dst, exist_ok=True) if not dry_run else None

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)

        if os.path.isdir(s):
            copy_tree_filtered(s, d, dry_run)
        else:
            # Skip neuron output txt files
            if is_neuron_output_file(item):
                print(f"  [SKIP] {os.path.relpath(s, SOURCE_ROOT)}")
                continue
            if not dry_run:
                shutil.copy2(s, d)
            print(f"  [COPY] {os.path.relpath(s, SOURCE_ROOT)}")

# ============================================================
# MAIN
# ============================================================

def main(dry_run=False):
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"\n{'='*60}")
    print(f"  copy_final_results.py  [{mode}]")
    print(f"  Source : {SOURCE_ROOT}")
    print(f"  Dest   : {DEST_ROOT}")
    print(f"  Datasets: {len(DATASETS)}")
    print(f"{'='*60}\n")

    total_copied  = 0
    total_skipped = 0

    for dataset in DATASETS:
        src_dataset = os.path.join(SOURCE_ROOT, dataset)
        dst_dataset = os.path.join(DEST_ROOT,   dataset)

        if not os.path.isdir(src_dataset):
            print(f"[{ts()}] [SKIP dataset] Not found: {src_dataset}")
            continue

        print(f"[{ts()}] >>> {dataset}")

        for folder in sorted(os.listdir(src_dataset)):
            src_folder = os.path.join(src_dataset, folder)
            dst_folder = os.path.join(dst_dataset, folder)

            if not os.path.isdir(src_folder):
                continue

            # ── validation_results_* → copy as-is ────────────
            if folder.startswith("validation_results_"):
                print(f"  [VAL ] {folder}")
                if not dry_run:
                    if os.path.exists(dst_folder):
                        shutil.rmtree(dst_folder)
                    shutil.copytree(src_folder, dst_folder)
                else:
                    print(f"         → {dst_folder}")

            # ── neuron_activations_* → copy filtered ──────────
            elif folder.startswith("neuron_activations_"):
                print(f"  [ACT ] {folder}")
                copy_tree_filtered(src_folder, dst_folder, dry_run)

            # ── anything else (e.g. master_analysis_results.csv) ──
            else:
                src_item = src_folder
                dst_item = dst_folder
                print(f"  [OTHER] {folder}")
                if not dry_run:
                    if os.path.isdir(src_item):
                        if os.path.exists(dst_item):
                            shutil.rmtree(dst_item)
                        shutil.copytree(src_item, dst_item)

        print()

    print(f"[{ts()}] {'='*60}")
    print(f"[{ts()}]  Done.")
    if dry_run:
        print(f"[{ts()}]  Re-run without --dry-run to actually copy files.")
    print(f"[{ts()}] {'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be copied without doing it")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
