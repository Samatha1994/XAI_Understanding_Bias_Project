"""
run_all_analysis.py
===================
Runs analyze_all_outputs.py logic for every dataset x patch combination.
Reads neuron_X_output_file.txt files from D:\BeoCat Results and saves
master_analysis_results.csv inside each neuron_activations_{patch} folder.

USAGE:
    python run_all_analysis.py

    # Run only specific datasets:
    python run_all_analysis.py --datasets WeedCrop OpenSprayer

    # Run only specific patches:
    python run_all_analysis.py --patches bottom_left top_right

    # Combine:
    python run_all_analysis.py --datasets WeedCrop --patches center

    # Skip a dataset:
    python run_all_analysis.py --skip Oxford
"""

import os
import re
import sys
import argparse
import traceback
import pandas as pd
from datetime import datetime

# ── Tee: captures ALL output to terminal + log file ──────────
class Tee:
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

# ── Log file ─────────────────────────────────────────────────
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "run_all_analysis_log.txt")
tee = Tee(log_path)
sys.stdout = tee
sys.stderr = tee

# ── Paths (from validate_config.py) ──────────────────────────
BEOCAT_ROOT = r"D:\BeoCat Results"

DATASETS = {
    "WeedCrop":    "patches_weedCrop",
    "OpenSprayer": "patches_openSprayer",
    "Sugarcane":   "patches_sugarcane",
    "Oxford":      "patches_oxford",
    "Cassava":      "patches_cassava",
}

ALL_PATCHES = ["bottom_left", "bottom_right", "center", "top_left", "top_right"]

# ── Argument parsing ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Run analysis for all dataset/patch combos")
parser.add_argument("--datasets", nargs="+", default=None)
parser.add_argument("--patches",  nargs="+", default=None)
parser.add_argument("--skip",     nargs="+", default=[])
args = parser.parse_args()

datasets_to_run = args.datasets if args.datasets else list(DATASETS.keys())
patches_to_run  = args.patches  if args.patches  else ALL_PATCHES
datasets_to_run = [d for d in datasets_to_run if d not in args.skip]

# ── Timestamp ────────────────────────────────────────────────
def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Solution extractor ────────────────────────────────────────
def extract_solutions(content):
    solutions = []
    solutions_pattern1 = r'solutions \(at most \d+ are shown\):(.*?)(?=\n\n|\nCompleted|\nError|\Z)'
    solutions_pattern2 = r'solutions:(.*?)(?=\n\n|\nCompleted|\nError|\nLearning|\nAlgorithm|\Z)'

    match = re.search(solutions_pattern1, content, re.DOTALL | re.IGNORECASE) or \
            re.search(solutions_pattern2, content, re.DOTALL | re.IGNORECASE)

    if match:
        lines = match.group(1).strip().split('\n')
        current_solution = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.match(r'^\d+:', line):
                if current_solution:
                    solutions.append(current_solution.strip())
                current_solution = line
            else:
                if current_solution:
                    current_solution += " " + line
        if current_solution:
            solutions.append(current_solution.strip())

    return solutions


# ── Error extractor ───────────────────────────────────────────
def extract_error_message(content):
    error_patterns = [
        r'(Error:.*?)(?=\n|$)',
        r'(Exception:.*?)(?=\n|$)',
        r'(Failed:.*?)(?=\n|$)',
        r'(SEVERE:.*?)(?=\n|$)',
        r'(java\.lang\..*?)(?=\n|$)',
        r'(No solution found.*?)(?=\n|$)',
        r'(Learning failed.*?)(?=\n|$)',
        r'(Timeout.*?)(?=\n|$)'
    ]
    for pattern in error_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        if matches:
            return '; '.join(matches[:3])
    for line in content.split('\n'):
        line_lower = line.lower().strip()
        if any(k in line_lower for k in ['error', 'exception', 'failed', 'timeout', 'severe']) and line.strip():
            return line.strip()
    return 'No specific error message found'


# ── Parse one feature folder ──────────────────────────────────
def parse_feature_folder(feature_path, layer_name, feature_name):
    # Matches neuron_X_output_file.txt
    output_files = sorted(
        [f for f in os.listdir(feature_path)
         if re.match(r'neuron_\d+_output_file\.txt', f)],
        key=lambda f: int(re.search(r'neuron_(\d+)_output_file\.txt', f).group(1))
    )

    if not output_files:
        print(f"    [SKIP] No output files in: {feature_path}")
        return []

    neuron_ids = [int(re.search(r'neuron_(\d+)_output_file\.txt', f).group(1))
                  for f in output_files]
    print(f"    Found {len(neuron_ids)} output files "
          f"(IDs: {neuron_ids[0]}-{neuron_ids[-1]})")

    results = []

    for fname in output_files:
        neuron_id = int(re.search(r'neuron_(\d+)_output_file\.txt', fname).group(1))
        filepath  = os.path.join(feature_path, fname)

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if "solutions:" in content.lower() or "solutions (at most" in content.lower():
                solutions = extract_solutions(content)
                if solutions:
                    results.append({
                        'Layer':         layer_name,
                        'Feature':       feature_name,
                        'Neuron_ID':     neuron_id,
                        'Status':        'Solutions Found',
                        'Solutions':     '\n'.join(solutions),
                        'Error_Message': ''
                    })
                else:
                    results.append({
                        'Layer':         layer_name,
                        'Feature':       feature_name,
                        'Neuron_ID':     neuron_id,
                        'Status':        'No Solutions Extracted',
                        'Solutions':     '',
                        'Error_Message': 'Solutions section found but could not extract'
                    })
            else:
                results.append({
                    'Layer':         layer_name,
                    'Feature':       feature_name,
                    'Neuron_ID':     neuron_id,
                    'Status':        'No Solutions',
                    'Solutions':     '',
                    'Error_Message': extract_error_message(content)
                })

        except Exception as e:
            results.append({
                'Layer':         layer_name,
                'Feature':       feature_name,
                'Neuron_ID':     neuron_id,
                'Status':        'Processing Error',
                'Solutions':     '',
                'Error_Message': f'Error reading file: {str(e)}'
            })

    return results


# ── Save per-feature results ──────────────────────────────────
def save_feature_results(results, feature_path, layer_name, feature_name):
    if not results:
        return

    df = pd.DataFrame(results)
    df.to_csv(os.path.join(feature_path, 'neuron_analysis_results.csv'), index=False)

    solutions_found = [r for r in results if r['Status'] == 'Solutions Found']
    no_solutions    = [r for r in results if r['Status'] == 'No Solutions']
    errors          = [r for r in results if 'Error' in r['Status']]

    # Detailed txt
    with open(os.path.join(feature_path, 'neuron_analysis_detailed.txt'), 'w', encoding='utf-8') as f:
        f.write(f"NEURON OUTPUT ANALYSIS - {layer_name} / {feature_name}\n")
        f.write("=" * 60 + "\n\n")
        for r in results:
            f.write(f"NEURON {r['Neuron_ID']}\n")
            f.write("-" * 20 + "\n")
            f.write(f"Status: {r['Status']}\n")
            if r['Solutions']:
                f.write("Solutions:\n" + r['Solutions'] + "\n")
            if r['Error_Message']:
                f.write(f"Error: {r['Error_Message']}\n")
            f.write("\n" + "=" * 60 + "\n\n")

    # Summary txt
    with open(os.path.join(feature_path, 'neuron_analysis_summary.txt'), 'w', encoding='utf-8') as f:
        f.write(f"SUMMARY - {layer_name} / {feature_name}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total files processed : {len(results)}\n")
        f.write(f"Solutions Found       : {len(solutions_found)}\n")
        f.write(f"No Solutions          : {len(no_solutions)}\n")
        f.write(f"Errors                : {len(errors)}\n\n")
        f.write(f"Neurons WITH solutions ({len(solutions_found)}):\n")
        for r in solutions_found:
            f.write(f"  - Neuron {r['Neuron_ID']}\n")
        f.write(f"\nNeurons with NO solutions ({len(no_solutions)}):\n")
        for r in no_solutions:
            f.write(f"  - Neuron {r['Neuron_ID']}: {r['Error_Message']}\n")
        f.write(f"\nNeurons with ERRORS ({len(errors)}):\n")
        for r in errors:
            f.write(f"  - Neuron {r['Neuron_ID']} [{r['Status']}]: {r['Error_Message']}\n")


# ── Run analysis for one dataset/patch ───────────────────────
def run_analysis(base_path):
    all_results = []

    layer_folders = sorted([
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d))
    ])

    if not layer_folders:
        print("  [WARN] No layer folders found!")
        return

    print(f"  Found {len(layer_folders)} layer folders")

    for layer_name in layer_folders:
        layer_path = os.path.join(base_path, layer_name)
        print(f"\n  >>> Layer: {layer_name}")

        feature_folders = sorted([
            d for d in os.listdir(layer_path)
            if os.path.isdir(os.path.join(layer_path, d))
        ])

        if not feature_folders:
            print(f"    [SKIP] No feature folders in {layer_name}")
            continue

        for feature_name in feature_folders:
            feature_path = os.path.join(layer_path, feature_name)
            print(f"    >> Feature: {feature_name}")

            results = parse_feature_folder(feature_path, layer_name, feature_name)
            if results:
                save_feature_results(results, feature_path, layer_name, feature_name)
                all_results.extend(results)

    # Save master CSV inside the patch folder
    if all_results:
        master_csv = os.path.join(base_path, 'master_analysis_results.csv')
        pd.DataFrame(all_results).to_csv(master_csv, index=False)

        n_found  = len([r for r in all_results if r['Status'] == 'Solutions Found'])
        n_none   = len([r for r in all_results if r['Status'] == 'No Solutions'])
        n_errors = len([r for r in all_results if 'Error' in r['Status']])

        print(f"\n  Master CSV saved -> {master_csv}")
        print(f"  Total processed : {len(all_results)}")
        print(f"  Solutions Found : {n_found}")
        print(f"  No Solutions    : {n_none}")
        print(f"  Errors          : {n_errors}")
    else:
        print("  [WARN] No results found - master CSV not saved")


# ── Main loop ─────────────────────────────────────────────────
total     = len(datasets_to_run) * len(patches_to_run)
done      = 0
successes = []
failures  = []

print(f"\n[{ts()}] " + "=" * 60)
print(f"[{ts()}]   run_all_analysis.py  -  START")
print(f"[{ts()}]   Datasets : {datasets_to_run}")
print(f"[{ts()}]   Patches  : {patches_to_run}")
print(f"[{ts()}]   Total    : {total} runs")
print(f"[{ts()}] " + "=" * 60)

for dataset in datasets_to_run:
    for patch in patches_to_run:
        done += 1
        label         = f"{dataset} / {patch}  [{done}/{total}]"
        beocat_folder = DATASETS[dataset]
        base_path     = os.path.join(BEOCAT_ROOT, beocat_folder,
                                     f"neuron_activations_{patch}")

        print(f"\n[{ts()}] >>> {label}")
        print(f"[{ts()}]     base_path : {base_path}")

        try:
            if not os.path.isdir(base_path):
                raise FileNotFoundError(f"Folder not found: {base_path}")

            run_analysis(base_path)
            print(f"[{ts()}]     [OK] {label}")
            successes.append(label)

        except FileNotFoundError as e:
            print(f"[{ts()}]     [SKIP] {label} - {e}")
            failures.append((label, str(e)))

        except Exception as e:
            print(f"[{ts()}]     [FAILED] {label} - {type(e).__name__}: {e}")
            print(traceback.format_exc())
            failures.append((label, str(e)))

# ── Final summary ─────────────────────────────────────────────
print(f"\n[{ts()}] " + "=" * 60)
print(f"[{ts()}]   FINISHED - {len(successes)}/{total} succeeded")
if failures:
    print(f"[{ts()}]   FAILURES / SKIPS ({len(failures)}):")
    for label, reason in failures:
        print(f"[{ts()}]     x  {label}")
        print(f"[{ts()}]        {reason}")
print(f"[{ts()}] " + "=" * 60)
print(f"[{ts()}]   Full log saved to: {log_path}")

sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
tee.close()
