# ============================================================
# validate_config.py
# Configuration for validate_concepts.py
#
# HOW TO USE:
#   1. Set ACTIVE_DATASET to the dataset you want to validate
#   2. Set ACTIVE_PATCH to the patch position you want to validate
#   3. Run: python validate_concepts.py
#   OR: Run run_all_validation.py to process all datasets/patches
# ============================================================

# ── What to run ──────────────────────────────────────────────
ACTIVE_DATASET = "WeedCrop"       # WeedCrop | OpenSprayer | Sugarcane | Oxford | Cassava
ACTIVE_PATCH   = "bottom_left"    # bottom_left | bottom_right | center | top_left | top_right

# ── Base paths ───────────────────────────────────────────────
# OneDrive root: holdout files, activation CSVs
ONEDRIVE_ROOT = r"C:\Users\Dell-PC\OneDrive - Kansas State University\Desktop\XAI-Low Level Features\understanding Bias in CNN"

# BeoCat Results root: neuron_activations folders (synced from cluster),DL-Learner results
BEOCAT_ROOT = r"D:\BeoCat Results"

# ── Dataset-specific settings ────────────────────────────────
DATASETS = {
    "WeedCrop": {
        "db_name":       "Identifying_bias_WeedCrop",
        "patch_root":    ONEDRIVE_ROOT + r"\patch_data\patches_weedCrop",
        "beocat_folder": "patches_weedCrop",        # folder name under BEOCAT_ROOT
        "patch_folder_map": {
            "bottom_left":  "bottom-left",
            "bottom_right": "bottom-right",
            "center":       "center",
            "top_left":     "top-left",
            "top_right":    "top-right",
        },
        "features_table_map": {
            "bottom_left":  "udat_features_bottom_left",
            "bottom_right": "udat_features_bottom_right",
            "center":       "udat_features_center",
            "top_left":     "udat_features_top_left",
            "top_right":    "udat_features_top_right",
        },
        "ranges_table_map": {
            "bottom_left":  "udat_feature_ranges_bottom_left",
            "bottom_right": "udat_feature_ranges_bottom_right",
            "center":       "udat_feature_ranges_center",
            "top_left":     "udat_feature_ranges_top_left",
            "top_right":    "udat_feature_ranges_top_right",
        },
        # ── Activation CSVs: still on OneDrive ──────────────
        "activations_dir_map": {
            "bottom_left":  r"\patch_data\patches_weedCrop\neuron_activations_bottom_left",
            "bottom_right": r"\patch_data\patches_weedCrop\neuron_activations_bottom_right",
            "center":       r"\patch_data\patches_weedCrop\neuron_activations_center",
            "top_left":     r"\patch_data\patches_weedCrop\neuron_activations_top_left",
            "top_right":    r"\patch_data\patches_weedCrop\neuron_activations_top_right",
        },
        "output_dir_map": {
            "bottom_left":  BEOCAT_ROOT+ r"\patches_weedCrop\validation_results_bottom_left",
            "bottom_right": BEOCAT_ROOT+ r"\patches_weedCrop\validation_results_bottom_right",
            "center":       BEOCAT_ROOT+ r"\patches_weedCrop\validation_results_center",
            "top_left":     BEOCAT_ROOT+ r"\patches_weedCrop\validation_results_top_left",
            "top_right":    BEOCAT_ROOT+ r"\patches_weedCrop\validation_results_top_right",
        },
    },

    "OpenSprayer": {
        "db_name":       "Identifying_bias_OpenSprayer",
        "patch_root":    ONEDRIVE_ROOT + r"\patch_data\patches_openSprayer",
        "beocat_folder": "patches_openSprayer",
        "patch_folder_map": {
            "bottom_left":  "bottom-left",
            "bottom_right": "bottom-right",
            "center":       "center",
            "top_left":     "top-left",
            "top_right":    "top-right",
        },
        "features_table_map": {
            "bottom_left":  "udat_features_bottom_left",
            "bottom_right": "udat_features_bottom_right",
            "center":       "udat_features_center",
            "top_left":     "udat_features_top_left",
            "top_right":    "udat_features_top_right",
        },
        "ranges_table_map": {
            "bottom_left":  "udat_feature_ranges_bottom_left",
            "bottom_right": "udat_feature_ranges_bottom_right",
            "center":       "udat_feature_ranges_center",
            "top_left":     "udat_feature_ranges_top_left",
            "top_right":    "udat_feature_ranges_top_right",
        },
        # ── Activation CSVs: still on OneDrive ──────────────
        "activations_dir_map": {
            "bottom_left":  r"\patch_data\patches_openSprayer\neuron_activations_bottom_left",
            "bottom_right": r"\patch_data\patches_openSprayer\neuron_activations_bottom_right",
            "center":       r"\patch_data\patches_openSprayer\neuron_activations_center",
            "top_left":     r"\patch_data\patches_openSprayer\neuron_activations_top_left",
            "top_right":    r"\patch_data\patches_openSprayer\neuron_activations_top_right",
        },                                
        "output_dir_map": {
            "bottom_left":  BEOCAT_ROOT+ r"\patches_openSprayer\validation_results_bottom_left",
            "bottom_right": BEOCAT_ROOT+ r"\patches_openSprayer\validation_results_bottom_right",
            "center":       BEOCAT_ROOT+ r"\patches_openSprayer\validation_results_center",
            "top_left":     BEOCAT_ROOT+ r"\patches_openSprayer\validation_results_top_left",
            "top_right":    BEOCAT_ROOT+ r"\patches_openSprayer\validation_results_top_right",
        },
    },

    "Sugarcane": {
        "db_name":       "Identifying_bias_Sugarcane",
        "patch_root":    ONEDRIVE_ROOT + r"\patch_data\patches_sugarcane",
        "beocat_folder": "patches_sugarcane",
        "image_name_format": "class/filename",
        "patch_folder_map": {
            "bottom_left":  "bottom-left",
            "bottom_right": "bottom-right",
            "center":       "center",
            "top_left":     "top-left",
            "top_right":    "top-right",
        },
        "features_table_map": {
            "bottom_left":  "udat_features_bottom_left",
            "bottom_right": "udat_features_bottom_right",
            "center":       "udat_features_center",
            "top_left":     "udat_features_top_left",
            "top_right":    "udat_features_top_right",
        },
        "ranges_table_map": {
            "bottom_left":  "udat_feature_ranges_bottom_left",
            "bottom_right": "udat_feature_ranges_bottom_right",
            "center":       "udat_feature_ranges_center",
            "top_left":     "udat_feature_ranges_top_left",
            "top_right":    "udat_feature_ranges_top_right",
        },
        # ── Activation CSVs: still on OneDrive ──────────────
        "activations_dir_map": {
            "bottom_left":  r"\patch_data\patches_sugarcane\neuron_activations_bottom_left",
            "bottom_right": r"\patch_data\patches_sugarcane\neuron_activations_bottom_right",
            "center":       r"\patch_data\patches_sugarcane\neuron_activations_center",
            "top_left":     r"\patch_data\patches_sugarcane\neuron_activations_top_left",
            "top_right":    r"\patch_data\patches_sugarcane\neuron_activations_top_right",
        },                                        
        "output_dir_map": {
            "bottom_left":  BEOCAT_ROOT+ r"\patches_sugarcane\validation_results_bottom_left",
            "bottom_right": BEOCAT_ROOT+ r"\patches_sugarcane\validation_results_bottom_right",
            "center":       BEOCAT_ROOT+ r"\patches_sugarcane\validation_results_center",
            "top_left":     BEOCAT_ROOT+ r"\patches_sugarcane\validation_results_top_left",
            "top_right":    BEOCAT_ROOT+ r"\patches_sugarcane\validation_results_top_right",
        },
    },

    # ── Oxford: add your db_name and OneDrive subfolder once confirmed ──
    "Oxford": {
        "db_name":       "Identifying_bias_Oxford",      # <-- confirm this DB name
        "patch_root":    ONEDRIVE_ROOT + r"\patch_data\patches_oxford",
        "beocat_folder": "patches_oxford",
        "patch_folder_map": {
            "bottom_left":  "bottom-left",
            "bottom_right": "bottom-right",
            "center":       "center",
            "top_left":     "top-left",
            "top_right":    "top-right",
        },
        "features_table_map": {
            "bottom_left":  "udat_features_bottom_left",
            "bottom_right": "udat_features_bottom_right",
            "center":       "udat_features_center",
            "top_left":     "udat_features_top_left",
            "top_right":    "udat_features_top_right",
        },
        "ranges_table_map": {
            "bottom_left":  "udat_feature_ranges_bottom_left",
            "bottom_right": "udat_feature_ranges_bottom_right",
            "center":       "udat_feature_ranges_center",
            "top_left":     "udat_feature_ranges_top_left",
            "top_right":    "udat_feature_ranges_top_right",
        },
        # ── Activation CSVs: still on OneDrive ──────────────
        "activations_dir_map": {
            "bottom_left":  r"\patch_data\patches_oxford\neuron_activations_bottom_left",
            "bottom_right": r"\patch_data\patches_oxford\neuron_activations_bottom_right",
            "center":       r"\patch_data\patches_oxford\neuron_activations_center",
            "top_left":     r"\patch_data\patches_oxford\neuron_activations_top_left",
            "top_right":    r"\patch_data\patches_oxford\neuron_activations_top_right",
        },                                        
        "output_dir_map": {
            "bottom_left":  BEOCAT_ROOT+ r"\patches_oxford\validation_results_bottom_left",
            "bottom_right": BEOCAT_ROOT+ r"\patches_oxford\validation_results_bottom_right",
            "center":       BEOCAT_ROOT+ r"\patches_oxford\validation_results_center",
            "top_left":     BEOCAT_ROOT+ r"\patches_oxford\validation_results_top_left",
            "top_right":    BEOCAT_ROOT+ r"\patches_oxford\validation_results_top_right",
        },
    },

    "Cassava": {
        "db_name":       "Identifying_bias_Cassava",      # <-- confirm this DB name
        "patch_root":    ONEDRIVE_ROOT + r"\patch_data\patches_cassava",
        "beocat_folder": "patches_cassava",
        "patch_folder_map": {
            "bottom_left":  "bottom-left",
            "bottom_right": "bottom-right",
            "center":       "center",
            "top_left":     "top-left",
            "top_right":    "top-right",
        },
        "features_table_map": {
            "bottom_left":  "udat_features_bottom_left",
            "bottom_right": "udat_features_bottom_right",
            "center":       "udat_features_center",
            "top_left":     "udat_features_top_left",
            "top_right":    "udat_features_top_right",
        },
        "ranges_table_map": {
            "bottom_left":  "udat_feature_ranges_bottom_left",
            "bottom_right": "udat_feature_ranges_bottom_right",
            "center":       "udat_feature_ranges_center",
            "top_left":     "udat_feature_ranges_top_left",
            "top_right":    "udat_feature_ranges_top_right",
        },
        # ── Activation CSVs: still on OneDrive ──────────────
        "activations_dir_map": {
            "bottom_left":  r"\patch_data\patches_cassava\neuron_activations_bottom_left",
            "bottom_right": r"\patch_data\patches_cassava\neuron_activations_bottom_right",
            "center":       r"\patch_data\patches_cassava\neuron_activations_center",
            "top_left":     r"\patch_data\patches_cassava\neuron_activations_top_left",
            "top_right":    r"\patch_data\patches_cassava\neuron_activations_top_right",
        },                                        
        "output_dir_map": {
            "bottom_left":  BEOCAT_ROOT+ r"\patches_cassava\validation_results_bottom_left",
            "bottom_right": BEOCAT_ROOT+ r"\patches_cassava\validation_results_bottom_right",
            "center":       BEOCAT_ROOT+ r"\patches_cassava\validation_results_center",
            "top_left":     BEOCAT_ROOT+ r"\patches_cassava\validation_results_top_left",
            "top_right":    BEOCAT_ROOT+ r"\patches_cassava\validation_results_top_right",
        },
    },
}

# ── DB credentials (same across all datasets) ────────────────
DB_USER     = "postgres"
DB_PASSWORD = "Rakshith123$"
DB_HOST     = "localhost"
DB_PORT     = "5432"

# ── Validation parameters (never change) ────────────────────
ALPHA          = 0.05
MIN_GROUP_SIZE = 3

# ============================================================
# Internal: resolve active config — don't edit below this line
# ============================================================

def get_validate_config():
    if ACTIVE_DATASET not in DATASETS:
        raise ValueError(
            f"ACTIVE_DATASET='{ACTIVE_DATASET}' not found.\n"
            f"Available: {list(DATASETS.keys())}"
        )
    if ACTIVE_PATCH not in ["bottom_left", "bottom_right", "center", "top_left", "top_right"]:
        raise ValueError(
            f"ACTIVE_PATCH='{ACTIVE_PATCH}' not valid.\n"
            f"Choose from: bottom_left, bottom_right, center, top_left, top_right"
        )

    ds           = DATASETS[ACTIVE_DATASET]
    patch_folder = ds["patch_folder_map"][ACTIVE_PATCH]

    # Neuron output .txt files are in BeoCat Results (D:\)
    # beocat_activations = (
    #     BEOCAT_ROOT + "\\" + ds["beocat_folder"]
    #     + "\\neuron_activations_" + ACTIVE_PATCH
    # )
    beocat_activations = (
    BEOCAT_ROOT + "\\" + ds["beocat_folder"]
    + "\\neuron_activations_" + ACTIVE_PATCH
    )

    return {
        "active_dataset":   ACTIVE_DATASET,
        "active_patch":     ACTIVE_PATCH,
        "base_path":        beocat_activations,          # neuron_X_output_file.txt lives here
        "holdout_file":     ds["patch_root"] + f"\\{patch_folder}\\holdout_images.txt",
        "activations_dir":  ONEDRIVE_ROOT + ds["activations_dir_map"][ACTIVE_PATCH],  # activation CSVs
        # "output_dir":       ONEDRIVE_ROOT + ds["output_dir_map"][ACTIVE_PATCH],
        "output_dir": ds["output_dir_map"][ACTIVE_PATCH],
        "features_table":   ds["features_table_map"][ACTIVE_PATCH],
        "ranges_table":     ds["ranges_table_map"][ACTIVE_PATCH],
        "db_config": {
            "dbname":   ds["db_name"],
            "user":     DB_USER,
            "password": DB_PASSWORD,
            "host":     DB_HOST,
            "port":     DB_PORT,
        },
        "alpha":            ALPHA,
        "min_group_size":   MIN_GROUP_SIZE,
        "image_name_format": ds.get("image_name_format", "filename"),
    }


# ============================================================
# Report-specific settings (used by generate_report.py)
# ============================================================

REPORT_FILTER_PARAMS = {
    "variance_remove_pct": 25,
    "pearson_top_n":        100,
    "top_k_selected":       50,
}

def get_report_config():
    cfg = get_validate_config()
    ds  = DATASETS[ACTIVE_DATASET]

    filter_dir = ONEDRIVE_ROOT + ds["activations_dir_map"][ACTIVE_PATCH]

    master_analysis_csv = (
        BEOCAT_ROOT + "\\" + ds["beocat_folder"]
        + "\\neuron_activations_" + ACTIVE_PATCH
        + "\\master_analysis_results.csv"
    )

    master_validation_csv = (
        ONEDRIVE_ROOT
        + ds["output_dir_map"][ACTIVE_PATCH]
        + "\\master_validation_results.csv"
    )

    output_csv = (
        ONEDRIVE_ROOT
        + ds["output_dir_map"][ACTIVE_PATCH]
        + f"\\pipeline_summary_report_{ACTIVE_DATASET}_{ACTIVE_PATCH}.csv"
    )

    return {
        "dataset":               ACTIVE_DATASET,
        "patch_position":        ACTIVE_PATCH,
        "filter_dir":            filter_dir,
        "master_analysis_csv":   master_analysis_csv,
        "master_validation_csv": master_validation_csv,
        "output_csv":            output_csv,
        **REPORT_FILTER_PARAMS,
    }
