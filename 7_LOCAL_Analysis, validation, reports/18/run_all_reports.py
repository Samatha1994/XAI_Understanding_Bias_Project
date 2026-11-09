"""
run_all_reports.py
==================
Runs generate_report.py logic for every dataset x patch combination.

Paths:
  - filter_dir          : OneDrive neuron_activations_{patch} folder (has filt_* subfolders)
  - master_analysis_csv : D:\BeoCat Results\{dataset}\neuron_activations_{patch}\master_analysis_results.csv
  - master_validation_csv: D:\BeoCat Results\{dataset}\validation_results_{patch}\master_validation_results.csv
  - output_csv          : D:\BeoCat Results\{dataset}\validation_results_{patch}\pipeline_summary_report_{dataset}_{patch}.csv

USAGE:
    python run_all_reports.py

    # Run only specific datasets:
    python run_all_reports.py --datasets WeedCrop OpenSprayer

    # Run only specific patches:
    python run_all_reports.py --patches bottom_left top_right

    # Skip a dataset:
    python run_all_reports.py --skip Oxford
"""

import os
import sys
import argparse
import traceback
import pandas as pd
import numpy as np
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
                        "run_all_reports_log.txt")
tee = Tee(log_path)
sys.stdout = tee
sys.stderr = tee

# ── Paths ─────────────────────────────────────────────────────
BEOCAT_ROOT   = r"D:\BeoCat Results"
ONEDRIVE_ROOT = r"C:\Users\Dell-PC\OneDrive - Kansas State University\Desktop\XAI-Low Level Features\understanding Bias in CNN"

# Dataset folder names on disk
DATASETS = {
    "WeedCrop":    {"beocat": "patches_weedCrop",    "onedrive": r"\patch_data\patches_weedCrop"},
    "OpenSprayer": {"beocat": "patches_openSprayer", "onedrive": r"\patch_data\patches_openSprayer"},
    "Sugarcane":   {"beocat": "patches_sugarcane",   "onedrive": r"\patch_data\patches_sugarcane"},
    "Oxford":      {"beocat": "patches_oxford",      "onedrive": r"\patch_data\patches_oxford"},
    "Cassava":      {"beocat": "patches_cassava",      "onedrive": r"\patch_data\patches_cassava"},
}

ALL_PATCHES = ["bottom_left", "bottom_right", "center", "top_left", "top_right"]

# ── Argument parsing ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Run report generation for all dataset/patch combos")
parser.add_argument("--datasets", nargs="+", default=None)
parser.add_argument("--patches",  nargs="+", default=None)
parser.add_argument("--skip",     nargs="+", default=[])
args = parser.parse_args()

datasets_to_run = args.datasets if args.datasets else list(DATASETS.keys())
patches_to_run  = args.patches  if args.patches  else ALL_PATCHES
datasets_to_run = [d for d in datasets_to_run if d not in args.skip]

# ── Timestamp ─────────────────────────────────────────────────
def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Layer maps (from generate_report.py) ─────────────────────
LAYER_MAP = {
    "ResNet50V2_mid2_conv3_block4":  {"model": "ResNet50V2",  "layer": "mid2",     "layer_name": "conv3_block4_out"},
    "ResNet50V2_mid_deep_conv4":     {"model": "ResNet50V2",  "layer": "mid_deep", "layer_name": "conv4_block6_out"},
    "ResNet50V2_deep_conv5_block3":  {"model": "ResNet50V2",  "layer": "deep",     "layer_name": "conv5_block3_out"},
    "DenseNet121_mid_conv3_block12": {"model": "DenseNet121", "layer": "mid",      "layer_name": "conv3_block12_concat"},
    "DenseNet121_mid_deep_conv4":    {"model": "DenseNet121", "layer": "mid_deep", "layer_name": "conv4_block24_concat"},
    "DenseNet121_deep_relu":         {"model": "DenseNet121", "layer": "deep",     "layer_name": "relu"},
    "InceptionV3_mid_mixed5":        {"model": "InceptionV3", "layer": "mid",      "layer_name": "mixed5"},
    "InceptionV3_mid_deep_mixed7":   {"model": "InceptionV3", "layer": "mid_deep", "layer_name": "mixed7"},
    "InceptionV3_deep_mixed10":      {"model": "InceptionV3", "layer": "deep",     "layer_name": "mixed10"},
    "VGG16_mid_block3_conv3":        {"model": "VGG16",       "layer": "mid",      "layer_name": "block3_conv3"},
    "VGG16_mid_deep_block4":         {"model": "VGG16",       "layer": "mid_deep", "layer_name": "block4_conv3"},
    "VGG16_deep_block5_conv3":       {"model": "VGG16",       "layer": "deep",     "layer_name": "block5_conv3"},
}

DL_LAYER_MAP = {
    "resnet_conv3_block4_out":       "ResNet50V2_mid2_conv3_block4",
    "resnet_conv4_block6_out":       "ResNet50V2_mid_deep_conv4",
    "resnet_conv5_block3_out":       "ResNet50V2_deep_conv5_block3",
    "densenet_conv3_block12_concat": "DenseNet121_mid_conv3_block12",
    "densenet_conv4_block24_concat": "DenseNet121_mid_deep_conv4",
    "densenet_deep_relu":            "DenseNet121_deep_relu",
    "InceptionV3_mixed5":            "InceptionV3_mid_mixed5",
    "InceptionV3_mixed7":            "InceptionV3_mid_deep_mixed7",
    "InceptionV3_mixed10":           "InceptionV3_deep_mixed10",
    "VGG16_block3_conv3":            "VGG16_mid_block3_conv3",
    "VGG16_block4_conv3":            "VGG16_mid_deep_block4",
    "VGG16_block5_conv3":            "VGG16_deep_block5_conv3",
}


# ── Step 1: Load filter stats ─────────────────────────────────
def load_filter_stats(filter_dir):
    stats = {}
    if not os.path.isdir(filter_dir):
        print(f"  [WARN] filter_dir not found: {filter_dir}")
        return stats

    for folder in sorted(os.listdir(filter_dir)):
        if not folder.startswith("filt_"):
            continue
        folder_path = os.path.join(filter_dir, folder)
        short_stem  = folder.replace("filt_", "")

        csv_files = [f for f in os.listdir(folder_path)
                     if f.startswith("results_") and f.endswith(".csv")]
        if not csv_files:
            print(f"  [WARN] No results CSV in {folder}")
            continue

        df     = pd.read_csv(os.path.join(folder_path, csv_files[0]))
        counts = df["decision"].value_counts().to_dict()

        total           = len(df)
        n_drop_var      = counts.get("DROP_variance", 0)
        n_after_var     = total - n_drop_var
        n_after_pearson = counts.get("KEEP", 0) + counts.get("DROP_topN", 0)
        n_final_keep    = counts.get("KEEP", 0)

        stats[short_stem] = {
            "total_neurons":         total,
            "after_variance_filter": n_after_var,
            "after_pearson_filter":  n_after_pearson,
            "final_kept_topk":       n_final_keep,
        }

    print(f"  Filter stats loaded for {len(stats)} layer folders")
    return stats


# ── Step 2: Load DL-Learner stats ────────────────────────────
def load_dl_stats(master_analysis_csv):
    df    = pd.read_csv(master_analysis_csv)
    stats = {}

    for (layer, feature), grp in df.groupby(["Layer", "Feature"]):
        n_total = len(grp)
        n_found = (grp["Status"] == "Solutions Found").sum()
        n_none  = (grp["Status"] == "No Solutions").sum()
        n_error = grp["Status"].str.contains("Error", na=False).sum()

        stats[(layer, feature)] = {
            "dl_neurons_run":      n_total,
            "dl_concepts_found":   int(n_found),
            "dl_no_solution":      int(n_none),
            "dl_errors":           int(n_error),
            "dl_concept_rate_pct": round(n_found / n_total * 100, 1) if n_total > 0 else 0,
        }

    print(f"  DL-Learner stats loaded: {len(stats)} layer x feature combinations")
    return stats


# ── Step 3: Load validation stats ────────────────────────────
def load_validation_stats(master_validation_csv):
    df    = pd.read_csv(master_validation_csv)
    stats = {}

    for (layer, feature), grp in df.groupby(["layer", "feature"]):
        has_concept  = grp["concept"].notna() & (grp["concept"] != "")
        no_parse     = (grp["notes"] == "Could not parse constraints")
        processable  = grp[has_concept & ~no_parse]

        n_no_concept  = int((~has_concept).sum())
        n_no_parse    = int(no_parse.sum())
        n_processable = len(processable)
        n_validated   = int(grp["validated"].sum())
        n_too_few_pos = int(grp["notes"].str.contains("Too few positives", na=False).sum())
        n_too_few_neg = int(grp["notes"].str.contains("Too few negatives", na=False).sum())

        validated_grp = grp[grp["validated"] == True]
        es_counts     = validated_grp["effect_size"].value_counts().to_dict()

        # ran_stats  = processable[processable["mw_statistic"].notna()]
        # n_not_sig  = int(ran_stats["significant"].eq(False).sum()) if len(ran_stats) > 0 else 0

        # stats[(layer, feature)] = {
        #     "val_no_concept":       n_no_concept,
        #     "val_could_not_parse":  n_no_parse,
        #     "val_processable":      n_processable,
        #     "val_too_few_pos":      n_too_few_pos,
        #     "val_too_few_neg":      n_too_few_neg,
        #     "val_not_significant":  n_not_sig,
        #     "val_validated":        n_validated,
        #     "val_rate_pct":         round(n_validated / n_processable * 100, 1) if n_processable > 0 else 0,
        #     "val_effect_medium":    es_counts.get("medium", 0),
        #     "val_effect_large":     es_counts.get("large",  0),
        #     "avg_pvalue":           round(ran_stats["p_value"].mean(), 4) if len(ran_stats) > 0 else None,
        #     "avg_cliffs_delta_abs": round(ran_stats["cliffs_delta"].abs().mean(), 4) if len(ran_stats) > 0 else None,
        #     "avg_celoe_accuracy":   round(processable["celoe_accuracy"].mean(), 2) if len(processable) > 0 else None,
        #     "avg_coverage":         round(processable["coverage"].mean(), 4) if len(processable) > 0 else None,
        # }
        ran_stats  = processable[processable["mw_statistic"].notna()]
        n_not_sig  = int(ran_stats["significant"].eq(False).sum()) if len(ran_stats) > 0 else 0
        n_significant   = int(ran_stats["significant"].eq(True).sum()) if len(ran_stats) > 0 else 0
        n_negated       = int(grp["notes"].str.startswith("negated", na=False).sum())
        avg_pos         = round(processable["n_concept_positive"].mean(), 2) if len(processable) > 0 else None

        stats[(layer, feature)] = {
            "val_no_concept":           n_no_concept,
            "val_could_not_parse":      n_no_parse,
            "val_processable":          n_processable,
            "val_negated_concepts":     n_negated,
            "val_too_few_pos":          n_too_few_pos,
            "val_too_few_neg":          n_too_few_neg,
            "val_significant":          n_significant,
            "val_not_significant":      n_not_sig,
            "val_validated":            n_validated,
            "val_rate_pct":             round(n_validated / n_processable * 100, 1) if n_processable > 0 else 0,
            "val_effect_medium":        es_counts.get("medium", 0),
            "val_effect_large":         es_counts.get("large",  0),
            "avg_pvalue":               round(ran_stats["p_value"].mean(), 4) if len(ran_stats) > 0 else None,
            "avg_cliffs_delta_abs":     round(ran_stats["cliffs_delta"].abs().mean(), 4) if len(ran_stats) > 0 else None,
            "avg_celoe_accuracy":       round(processable["celoe_accuracy"].mean(), 2) if len(processable) > 0 else None,
            "avg_coverage":             round(processable["coverage"].mean(), 4) if len(processable) > 0 else None,
            "avg_n_concept_positive":   avg_pos,
        }

    print(f"  Validation stats loaded: {len(stats)} layer x feature combinations")
    return stats


# ── Step 4: Build report ──────────────────────────────────────
def build_report(filter_stats, dl_stats, val_stats, dataset, patch):
    rows     = []
    all_keys = set(dl_stats.keys()) | set(val_stats.keys())

    for (dl_layer, feature) in sorted(all_keys):
        filter_stem = DL_LAYER_MAP.get(dl_layer)
        layer_info  = LAYER_MAP.get(filter_stem, {}) if filter_stem else {}

        model       = layer_info.get("model",      dl_layer)
        layer_alias = layer_info.get("layer",      "unknown")
        layer_name  = layer_info.get("layer_name", dl_layer)

        filt = filter_stats.get(filter_stem, {}) if filter_stem else {}
        dl   = dl_stats.get((dl_layer, feature), {})
        val  = val_stats.get((dl_layer, feature), {})

        rows.append({
            "dataset":               dataset,
            "patch_position":        patch,
            "model":                 model,
            "layer_alias":           layer_alias,
            "layer_name":            layer_name,
            "feature_family":        feature,
            # "total_neurons":         filt.get("total_neurons",         "N/A"),
            # "after_variance_filter": filt.get("after_variance_filter", "N/A"),
            # "after_pearson_filter":  filt.get("after_pearson_filter",  "N/A"),
            # "final_kept_topk":       filt.get("final_kept_topk",       "N/A"),
            # "dl_neurons_run":        dl.get("dl_neurons_run",      0),
            # "dl_concepts_found":     dl.get("dl_concepts_found",   0),
            # "dl_no_solution":        dl.get("dl_no_solution",      0),
            # "dl_concept_rate_pct":   dl.get("dl_concept_rate_pct", 0),
            # "val_no_concept":        val.get("val_no_concept",       0),
            # "val_could_not_parse":   val.get("val_could_not_parse",  0),
            # "val_processable":       val.get("val_processable",      0),
            # "val_too_few_pos":       val.get("val_too_few_pos",      0),
            # "val_too_few_neg":       val.get("val_too_few_neg",      0),
            # "val_not_significant":   val.get("val_not_significant",  0),
            # "val_validated":         val.get("val_validated",        0),
            # "val_rate_pct":          val.get("val_rate_pct",         0),
            # "val_effect_medium":     val.get("val_effect_medium",    0),
            # "val_effect_large":      val.get("val_effect_large",     0),
            # "avg_pvalue":            val.get("avg_pvalue"),
            # "avg_cliffs_delta_abs":  val.get("avg_cliffs_delta_abs"),
            # "avg_celoe_accuracy":    val.get("avg_celoe_accuracy"),
            # "avg_coverage":          val.get("avg_coverage"),
            "total_neurons":             filt.get("total_neurons",         "N/A"),
            "after_variance_filter":     filt.get("after_variance_filter", "N/A"),
            "after_pearson_filter":      filt.get("after_pearson_filter",  "N/A"),
            "final_kept_topk":           filt.get("final_kept_topk",       "N/A"),
            "dl_neurons_run":            dl.get("dl_neurons_run",      0),
            "dl_concepts_found":         dl.get("dl_concepts_found",   0),
            "dl_no_solution":            dl.get("dl_no_solution",      0),
            "dl_errors":                 dl.get("dl_errors",           0),
            "dl_concept_rate_pct":       dl.get("dl_concept_rate_pct", 0),
            "val_no_concept":            val.get("val_no_concept",           0),
            "val_could_not_parse":       val.get("val_could_not_parse",      0),
            "val_processable":           val.get("val_processable",          0),
            "val_negated_concepts":      val.get("val_negated_concepts",     0),
            "val_too_few_pos":           val.get("val_too_few_pos",          0),
            "val_too_few_neg":           val.get("val_too_few_neg",          0),
            "val_significant":           val.get("val_significant",          0),
            "val_not_significant":       val.get("val_not_significant",      0),
            "val_validated":             val.get("val_validated",            0),
            "val_rate_pct":              val.get("val_rate_pct",             0),
            "val_effect_medium":         val.get("val_effect_medium",        0),
            "val_effect_large":          val.get("val_effect_large",         0),
            "avg_pvalue":                val.get("avg_pvalue"),
            "avg_cliffs_delta_abs":      val.get("avg_cliffs_delta_abs"),
            "avg_celoe_accuracy":        val.get("avg_celoe_accuracy"),
            "avg_coverage":              val.get("avg_coverage"),
            "avg_n_concept_positive":    val.get("avg_n_concept_positive"),
        })

    return pd.DataFrame(rows)


# ── Run report for one dataset/patch ─────────────────────────
def run_report(dataset, patch):
    ds = DATASETS[dataset]

    # Paths
    filter_dir            = ONEDRIVE_ROOT + ds["onedrive"] + f"\\neuron_activations_{patch}"
    master_analysis_csv   = os.path.join(BEOCAT_ROOT, ds["beocat"], f"neuron_activations_{patch}", "master_analysis_results.csv")
    master_validation_csv = os.path.join(BEOCAT_ROOT, ds["beocat"], f"validation_results_{patch}", "master_validation_results.csv")
    output_dir            = os.path.join(BEOCAT_ROOT, ds["beocat"], f"validation_results_{patch}")
    output_csv            = os.path.join(output_dir, f"pipeline_summary_report_{dataset}_{patch}.csv")

    print(f"  filter_dir            : {filter_dir}")
    print(f"  master_analysis_csv   : {master_analysis_csv}")
    print(f"  master_validation_csv : {master_validation_csv}")
    print(f"  output_csv            : {output_csv}")

    # Check required files exist
    if not os.path.isfile(master_analysis_csv):
        raise FileNotFoundError(f"master_analysis_results.csv not found: {master_analysis_csv}")
    if not os.path.isfile(master_validation_csv):
        raise FileNotFoundError(f"master_validation_results.csv not found: {master_validation_csv}")

    print("\n  [1] Loading filter stats...")
    filter_stats = load_filter_stats(filter_dir)

    print("  [2] Loading DL-Learner stats...")
    dl_stats = load_dl_stats(master_analysis_csv)

    print("  [3] Loading validation stats...")
    val_stats = load_validation_stats(master_validation_csv)

    print("  [4] Building report...")
    report_df = build_report(filter_stats, dl_stats, val_stats, dataset, patch)

    os.makedirs(output_dir, exist_ok=True)
    report_df.to_csv(output_csv, index=False)

    print(f"\n  Report saved -> {output_csv}")
    print(f"  Rows    : {len(report_df)}  (model x layer x feature)")
    print(f"  Columns : {len(report_df.columns)}")
    print(f"  Total DL neurons run    : {report_df['dl_neurons_run'].sum()}")
    print(f"  Total concepts found    : {report_df['dl_concepts_found'].sum()}")
    print(f"  Total validated         : {report_df['val_validated'].sum()}")
    processable = report_df['val_processable'].sum()
    validated   = report_df['val_validated'].sum()
    rate        = validated / max(processable, 1) * 100
    print(f"  Overall validation rate : {rate:.1f}%")


# ── Main loop ─────────────────────────────────────────────────
total     = len(datasets_to_run) * len(patches_to_run)
done      = 0
successes = []
failures  = []

print(f"\n[{ts()}] " + "=" * 60)
print(f"[{ts()}]   run_all_reports.py  -  START")
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
            run_report(dataset, patch)
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
