"""
run_all_validation.py
=====================
Runs validate_concepts.py for every dataset × patch combination
by dynamically overriding ACTIVE_DATASET and ACTIVE_PATCH in
validate_config before importing and running validate_concepts.

USAGE:
    python run_all_validation.py

    # Run only specific datasets:
    python run_all_validation.py --datasets WeedCrop OpenSprayer

    # Run only specific patches:
    python run_all_validation.py --patches bottom_left top_right

    # Combine:
    python run_all_validation.py --datasets WeedCrop --patches center

    # Skip Oxford (not ready yet):
    python run_all_validation.py --skip Oxford

NOTES:
    - Place this file in the same folder as validate_concepts.py
      and validate_config.py
    - Output CSVs go to each dataset's validation_results_* folder
      on OneDrive (as configured in validate_config.py)
    - ALL terminal output (including from validate_concepts.py) is
      saved to run_all_validation_log.txt automatically
"""

import sys
import os
import argparse
import traceback
from datetime import datetime

# ── Tee: captures ALL output (print statements from any module) ──
class Tee:
    """Redirects stdout/stderr to both terminal and log file simultaneously."""
    def __init__(self, log_path):
        self.terminal = sys.__stdout__
        self.log_file = open(log_path, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.terminal.flush()
        self.log_file.write(message)
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        self.log_file.close()

# ── Log file path ────────────────────────────────────────────
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "run_all_validation_log.txt")

# ── Activate Tee — from this point ALL print() goes to terminal + log ──
tee = Tee(log_path)
sys.stdout = tee
sys.stderr = tee

# ── All datasets and patches to process ─────────────────────
ALL_DATASETS = ["WeedCrop", "OpenSprayer", "Sugarcane", "Oxford","Cassava"]
# ALL_DATASETS = ["Sugarcane"]
ALL_PATCHES  = ["bottom_left", "bottom_right", "center", "top_left", "top_right"]

# ── Parse command-line arguments ─────────────────────────────
parser = argparse.ArgumentParser(description="Run validation for all dataset/patch combos")
parser.add_argument("--datasets", nargs="+", default=None,
                    help="Datasets to run (default: all)")
parser.add_argument("--patches",  nargs="+", default=None,
                    help="Patches to run (default: all)")
parser.add_argument("--skip",     nargs="+", default=[],
                    help="Datasets to skip")
args = parser.parse_args()

datasets_to_run = args.datasets if args.datasets else ALL_DATASETS
patches_to_run  = args.patches  if args.patches  else ALL_PATCHES
datasets_to_run = [d for d in datasets_to_run if d not in args.skip]

# ── Timestamp helper ─────────────────────────────────────────
def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ── Main loop ────────────────────────────────────────────────
total     = len(datasets_to_run) * len(patches_to_run)
done      = 0
successes = []
failures  = []

print(f"\n[{ts()}] " + "=" * 60)
print(f"[{ts()}]   run_all_validation.py  —  START")
print(f"[{ts()}]   Datasets : {datasets_to_run}")
print(f"[{ts()}]   Patches  : {patches_to_run}")
print(f"[{ts()}]   Total    : {total} runs")
print(f"[{ts()}] " + "=" * 60)

for dataset in datasets_to_run:
    for patch in patches_to_run:
        done += 1
        label = f"{dataset} / {patch}  [{done}/{total}]"

        print(f"\n[{ts()}] >>> {label}")

        try:
            import validate_config as vc
            vc.ACTIVE_DATASET = dataset
            vc.ACTIVE_PATCH   = patch

            cfg = vc.get_validate_config()
            print(f"[{ts()}]     base_path  : {cfg['base_path']}")
            print(f"[{ts()}]     holdout    : {cfg['holdout_file']}")
            print(f"[{ts()}]     output_dir : {cfg['output_dir']}")

            if not os.path.isdir(cfg["base_path"]):
                raise FileNotFoundError(f"base_path not found: {cfg['base_path']}")

            if not os.path.isfile(cfg["holdout_file"]):
                raise FileNotFoundError(f"holdout_images.txt not found: {cfg['holdout_file']}")

            os.makedirs(cfg["output_dir"], exist_ok=True)

            import importlib
            import validate_concepts
            importlib.reload(validate_concepts)
            validate_concepts.main()

            print(f"[{ts()}]     [OK] {label}")
            successes.append(label)

        except FileNotFoundError as e:
            print(f"[{ts()}]     [SKIP] {label} — {e}")
            failures.append((label, str(e)))

        except Exception as e:
            print(f"[{ts()}]     [FAILED] {label} — {type(e).__name__}: {e}")
            print(traceback.format_exc())
            failures.append((label, str(e)))

# ── Final summary ────────────────────────────────────────────
print(f"\n[{ts()}] " + "=" * 60)
print(f"[{ts()}]   FINISHED — {len(successes)}/{total} succeeded")
if failures:
    print(f"[{ts()}]   FAILURES / SKIPS ({len(failures)}):")
    for label, reason in failures:
        print(f"[{ts()}]     ✗  {label}")
        print(f"[{ts()}]        {reason}")
print(f"[{ts()}] " + "=" * 60)
print(f"[{ts()}]   Full log saved to: {log_path}")

# ── Close Tee ────────────────────────────────────────────────
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
tee.close()