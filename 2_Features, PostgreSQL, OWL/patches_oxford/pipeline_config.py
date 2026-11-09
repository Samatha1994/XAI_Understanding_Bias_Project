# ============================================================
# pipeline_config.py
# Central configuration for the XAI Low-Level Feature Pipeline
#
# HOW TO USE:
#   1. Select an active dataset by setting ACTIVE_DATASET below
#   2. Add new datasets by copying any entry in DATASETS and filling in your values
#   3. All 4 pipeline scripts import this file — you only edit here
# ============================================================

# ── Which dataset to run right now ──────────────────────────
ACTIVE_DATASET = "oxford_top_right"   # change this to switch datasets
# oxford_bottom_left  | oxford_bottom_right   |   oxford_center   |   oxford_top_left |   oxford_top_right

# ── Dataset-specific settings ────────────────────────────────
# Each entry contains every parameter used by scripts 3, 4, 5, and 6.
# Keys are explained below the dict.

DATASETS = {

    "oxford_bottom_left": {
        # --- Paths ---
        "csv_path": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/bottom-left/sig_features_output_patches_oxford_bottom_left.csv",
        "owl_output_dir": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/bottom-left/output_dynamic_owl_structure_all_features",
        "combined_owl_output": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/bottom-left/combined_all_features.owl",

        # --- Database ---
        "db_name": "Identifying_bias_Oxford",
        "db_user": "postgres",
        "db_password": "Rakshith123$",
        "db_host": "localhost",
        "db_port": "5432",

        # --- Table names ---
        "features_table": "udat_features_bottom_left",
        "ranges_table": "udat_feature_ranges_bottom_left",

        # --- Binning ---
        "num_bins": 5,

        # --- OWL / ontology ---
        "base_uri": "http://daselab.org/ontologies/ADE20k/combined.owl",
        "owl_namespace": "http://daselab.org/ontologies/ADE20k/",

        # --- Algorithm filter for script 5 (empty list = ALL algorithms) ---
        # "filter_algorithms": ["tamura texture"],  
        # "filter_algorithms": ["haarlick texture"],  
        # "filter_algorithms": ["gabor filters"], 
        # "filter_algorithms": ["combfirstfourmoments"], 
        # "filter_algorithms": ["multiscale histogram"], 
        # "filter_algorithms": ["chebishev fourier transform"],
#         "filter_algorithms": ["edge area", "edge diffdirechist", "edge direction histogram", "edge direction homogeneity", "edge direction mean", "edge direction median", "edge direction variance", "edge magnitude histogram",
#  "edge magnitude mean", "edge magnitude median", "edge magnitude variance"], 
#  "filter_algorithms": ["feature area histogram", "feature areamax", "feature areamean", "feature areamedian", "feature areamin", "feature areavar", "feature count", "feature dist histogram",
#  "feature distmax", "feature distmean", "feature distmedian", "feature distmin", "feature distvar", "feature euler", "feature x centroid", "feature y centroid"], 
        # "filter_algorithms": ["zernike"], 
        # "filter_algorithms": ["radon"], 
        # "filter_algorithms": ["color histogram"], 
        # "filter_algorithms": ["fractal"], 
        # "filter_algorithms": ["intensity statistics"], 
        # "filter_algorithms": ["tamura texture","haarlick texture","gabor filters","combfirstfourmoments","multiscale histogram","chebishev fourier transform","zernike","radon","color histogram", "fractal", "intensity statistics",
        #              "feature area histogram","feature areamax","feature areamean","feature areamedian","feature areamin","feature areavar","feature count","feature dist histogram","feature distmax","feature distmean",
        #             "feature distmedian","feature distmin","feature distvar","feature euler","feature x centroid","feature y centroid","edge area","edge diffdirechist","edge direction histogram","edge direction homogeneity","edge direction mean",
        #             "edge direction median","edge direction variance","edge magnitude histogram","edge magnitude mean","edge magnitude median","edge magnitude variance"], 
    },

    "oxford_bottom_right": {
        "csv_path": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/bottom-right/sig_features_output_patches_oxford_bottom_right.csv",
        "owl_output_dir": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/bottom-right/output_dynamic_owl_structure_all_features",
        "combined_owl_output": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/bottom-right/combined_all_features.owl",

        "db_name": "Identifying_bias_Oxford",
        "db_user": "postgres",
        "db_password": "Rakshith123$",
        "db_host": "localhost",
        "db_port": "5432",

        "features_table": "udat_features_bottom_right",
        "ranges_table": "udat_feature_ranges_bottom_right",

        "num_bins": 5,

        "base_uri": "http://daselab.org/ontologies/ADE20k/combined.owl",
        "owl_namespace": "http://daselab.org/ontologies/ADE20k/",

        # "filter_algorithms": ["tamura texture"],  
        # "filter_algorithms": ["haarlick texture"],  
        # "filter_algorithms": ["gabor filters"], 
        # "filter_algorithms": ["combfirstfourmoments"], 
        # "filter_algorithms": ["multiscale histogram"], 
        # "filter_algorithms": ["chebishev fourier transform"],
#         "filter_algorithms": ["edge area", "edge diffdirechist", "edge direction histogram", "edge direction homogeneity", "edge direction mean", "edge direction median", "edge direction variance", "edge magnitude histogram",
#  "edge magnitude mean", "edge magnitude median", "edge magnitude variance"], 
#  "filter_algorithms": ["feature area histogram", "feature areamax", "feature areamean", "feature areamedian", "feature areamin", "feature areavar", "feature count", "feature dist histogram",
#  "feature distmax", "feature distmean", "feature distmedian", "feature distmin", "feature distvar", "feature euler", "feature x centroid", "feature y centroid"], 
# "filter_algorithms": ["zernike"], 
# "filter_algorithms": ["radon"], 
# "filter_algorithms": ["color histogram"], 
# "filter_algorithms": ["fractal"], 
# "filter_algorithms": ["intensity statistics"], 
# "filter_algorithms": ["tamura texture","haarlick texture","gabor filters","combfirstfourmoments","multiscale histogram","chebishev fourier transform","zernike","radon","color histogram", "fractal", "intensity statistics",
#                      "feature area histogram","feature areamax","feature areamean","feature areamedian","feature areamin","feature areavar","feature count","feature dist histogram","feature distmax","feature distmean",
# "feature distmedian","feature distmin","feature distvar","feature euler","feature x centroid","feature y centroid","edge area","edge diffdirechist","edge direction histogram","edge direction homogeneity","edge direction mean",
# "edge direction median","edge direction variance","edge magnitude histogram","edge magnitude mean","edge magnitude median","edge magnitude variance"], 
    },

    "oxford_center": {
        "csv_path": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/center/sig_features_output_patches_oxford_center.csv",
        "owl_output_dir": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/center/output_dynamic_owl_structure_all_features",
        "combined_owl_output": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/center/combined_all_features.owl",
        
        "db_name": "Identifying_bias_Oxford",
        "db_user": "postgres",
        "db_password": "Rakshith123$",
        "db_host": "localhost",
        "db_port": "5432",

        "features_table": "udat_features_center",
        "ranges_table": "udat_feature_ranges_center",

        "num_bins": 5,

        "base_uri": "http://daselab.org/ontologies/ADE20k/combined.owl",
        "owl_namespace": "http://daselab.org/ontologies/ADE20k/",

        # "filter_algorithms": ["tamura texture"],  
        # "filter_algorithms": ["haarlick texture"],  
        # "filter_algorithms": ["gabor filters"], 
        # "filter_algorithms": ["combfirstfourmoments"], 
        # "filter_algorithms": ["multiscale histogram"], 
        # "filter_algorithms": ["chebishev fourier transform"],
#         "filter_algorithms": ["edge area", "edge diffdirechist", "edge direction histogram", "edge direction homogeneity", "edge direction mean", "edge direction median", "edge direction variance", "edge magnitude histogram",
#  "edge magnitude mean", "edge magnitude median", "edge magnitude variance"], 
#  "filter_algorithms": ["feature area histogram", "feature areamax", "feature areamean", "feature areamedian", "feature areamin", "feature areavar", "feature count", "feature dist histogram",
#  "feature distmax", "feature distmean", "feature distmedian", "feature distmin", "feature distvar", "feature euler", "feature x centroid", "feature y centroid"], 
        # "filter_algorithms": ["zernike"], 
        # "filter_algorithms": ["radon"], 
        # "filter_algorithms": ["color histogram"], 
        # "filter_algorithms": ["fractal"], 
        # "filter_algorithms": ["intensity statistics"], 
        # "filter_algorithms": ["tamura texture","haarlick texture","gabor filters","combfirstfourmoments","multiscale histogram","chebishev fourier transform","zernike","radon","color histogram", "fractal", "intensity statistics",
        #              "feature area histogram","feature areamax","feature areamean","feature areamedian","feature areamin","feature areavar","feature count","feature dist histogram","feature distmax","feature distmean",
        #             "feature distmedian","feature distmin","feature distvar","feature euler","feature x centroid","feature y centroid","edge area","edge diffdirechist","edge direction histogram","edge direction homogeneity","edge direction mean",
        #             "edge direction median","edge direction variance","edge magnitude histogram","edge magnitude mean","edge magnitude median","edge magnitude variance"], 
    },

    "oxford_top_left": {
        "csv_path": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/top-left/sig_features_output_patches_oxford_top_left.csv",
        "owl_output_dir": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/top-left/output_dynamic_owl_structure_all_features",
        "combined_owl_output": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/top-left/combined_all_features.owl",
		
        "db_name": "Identifying_bias_Oxford",
        "db_user": "postgres",
        "db_password": "Rakshith123$",
        "db_host": "localhost",
        "db_port": "5432",

        "features_table": "udat_features_top_left",
        "ranges_table": "udat_feature_ranges_top_left",

        "num_bins": 5,

        "base_uri": "http://daselab.org/ontologies/ADE20k/combined.owl",
        "owl_namespace": "http://daselab.org/ontologies/ADE20k/",

        # "filter_algorithms": ["tamura texture"],  
        # "filter_algorithms": ["haarlick texture"],  
        # "filter_algorithms": ["gabor filters"], 
        # "filter_algorithms": ["combfirstfourmoments"], 
        # "filter_algorithms": ["multiscale histogram"], 
        # "filter_algorithms": ["chebishev fourier transform"],
#         "filter_algorithms": ["edge area", "edge diffdirechist", "edge direction histogram", "edge direction homogeneity", "edge direction mean", "edge direction median", "edge direction variance", "edge magnitude histogram",
#  "edge magnitude mean", "edge magnitude median", "edge magnitude variance"], 
#  "filter_algorithms": ["feature area histogram", "feature areamax", "feature areamean", "feature areamedian", "feature areamin", "feature areavar", "feature count", "feature dist histogram",
#  "feature distmax", "feature distmean", "feature distmedian", "feature distmin", "feature distvar", "feature euler", "feature x centroid", "feature y centroid"], 
        # "filter_algorithms": ["zernike"], 
        # "filter_algorithms": ["radon"], 
        # "filter_algorithms": ["color histogram"], 
        # "filter_algorithms": ["fractal"], 
        # "filter_algorithms": ["intensity statistics"], 
        # "filter_algorithms": ["tamura texture","haarlick texture","gabor filters","combfirstfourmoments","multiscale histogram","chebishev fourier transform","zernike","radon","color histogram", "fractal", "intensity statistics",
        #              "feature area histogram","feature areamax","feature areamean","feature areamedian","feature areamin","feature areavar","feature count","feature dist histogram","feature distmax","feature distmean",
        #             "feature distmedian","feature distmin","feature distvar","feature euler","feature x centroid","feature y centroid","edge area","edge diffdirechist","edge direction histogram","edge direction homogeneity","edge direction mean",
        #             "edge direction median","edge direction variance","edge magnitude histogram","edge magnitude mean","edge magnitude median","edge magnitude variance"], 
    },

    "oxford_top_right": {
        "csv_path": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/top-right/sig_features_output_patches_oxford_top_right.csv",
        "owl_output_dir": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/top-right/output_dynamic_owl_structure_all_features",
        "combined_owl_output": r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_oxford/top-right/combined_all_features.owl",

        "db_name": "Identifying_bias_Oxford",
        "db_user": "postgres",
        "db_password": "Rakshith123$",
        "db_host": "localhost",
        "db_port": "5432",

        "features_table": "udat_features_top_right",
        "ranges_table": "udat_feature_ranges_top_right",

        "num_bins": 5,

        "base_uri": "http://daselab.org/ontologies/ADE20k/combined.owl",
        "owl_namespace": "http://daselab.org/ontologies/ADE20k/",

        # "filter_algorithms": ["tamura texture"],  
        # "filter_algorithms": ["haarlick texture"],  
        # "filter_algorithms": ["gabor filters"], 
        # "filter_algorithms": ["combfirstfourmoments"], 
        # "filter_algorithms": ["multiscale histogram"], 
        # "filter_algorithms": ["chebishev fourier transform"],
#         "filter_algorithms": ["edge area", "edge diffdirechist", "edge direction histogram", "edge direction homogeneity", "edge direction mean", "edge direction median", "edge direction variance", "edge magnitude histogram",
#  "edge magnitude mean", "edge magnitude median", "edge magnitude variance"], 
#  "filter_algorithms": ["feature area histogram", "feature areamax", "feature areamean", "feature areamedian", "feature areamin", "feature areavar", "feature count", "feature dist histogram",
#  "feature distmax", "feature distmean", "feature distmedian", "feature distmin", "feature distvar", "feature euler", "feature x centroid", "feature y centroid"], 
        # "filter_algorithms": ["zernike"], 
        # "filter_algorithms": ["radon"], 
        # "filter_algorithms": ["color histogram"], 
        # "filter_algorithms": ["fractal"], 
        # "filter_algorithms": ["intensity statistics"], 
        "filter_algorithms": ["tamura texture","haarlick texture","gabor filters","combfirstfourmoments","multiscale histogram","chebishev fourier transform","zernike","radon","color histogram", "fractal", "intensity statistics",
                     "feature area histogram","feature areamax","feature areamean","feature areamedian","feature areamin","feature areavar","feature count","feature dist histogram","feature distmax","feature distmean",
                    "feature distmedian","feature distmin","feature distvar","feature euler","feature x centroid","feature y centroid","edge area","edge diffdirechist","edge direction histogram","edge direction homogeneity","edge direction mean",
                    "edge direction median","edge direction variance","edge magnitude histogram","edge magnitude mean","edge magnitude median","edge magnitude variance"], 
    },

    # ── Add more datasets here by copying the block above ──
}


# ============================================================
# Internal: resolve active config — don't edit below this line
# ============================================================
def get_config():
    if ACTIVE_DATASET not in DATASETS:
        raise ValueError(
            f"ACTIVE_DATASET='{ACTIVE_DATASET}' not found in DATASETS.\n"
            f"Available datasets: {list(DATASETS.keys())}"
        )
    cfg = DATASETS[ACTIVE_DATASET].copy()
    cfg["active_dataset"] = ACTIVE_DATASET
    # Build psycopg2-ready DB dict
    cfg["db_config"] = {
        "dbname":   cfg["db_name"],
        "user":     cfg["db_user"],
        "password": cfg["db_password"],
        "host":     cfg["db_host"],
        "port":     cfg["db_port"],
    }
    return cfg



# Load feature data - configurable filter
# FILTER_ALGORITHMS = ['tamura texture']  # TAMURA TEXTURES - conv2_block3_out (256) 
# FILTER_ALGORITHMS = ['haarlick texture']  # HARLIC (co-occurrence matrix) FEATURES - conv2_block3_out (256) "haarlick texture" 
                        # FILTER_ALGORITHMS = [
                        #     'co oc mat and angular second moment',
                        #     'co oc mat and contrast',
                        #     'co oc mat and correlation',
                        #     'co oc mat and difference entropy',
                        #     'co oc mat and difference variance',
                        #     'co oc mat and entropy',
                        #     'co oc mat and first measure of correlation',
                        #     'co oc mat and inverse difference moment',
                        #     'co oc mat and maximal correlation coefficient',
                        #     'co oc mat and second measure of correlation',
                        #     'co oc mat and sum average',
                        #     'co oc mat and sum entropy',
                        #     'co oc mat and sum variance',
                        #     'co oc mat and variance',
                        # ]  # All 14 HARLIC (co-occurrence matrix) FEATURES - conv2_block3_out (256)--remobve this filter. now these come under "haarlick texture"
# FILTER_ALGORITHMS = ['gabor filters']  # GABOUR TEXTURES - conv2_block3_out (256)

# FILTER_ALGORITHMS = ['combfirstfourmoments']  # FIRST 4 MOMENTS - conv2_block1_out (256)

# FILTER_ALGORITHMS = ['multiscale histogram']  # MULTI-SCALE HISTOGRAMS - conv2_block2_out (256)
# FILTER_ALGORITHMS = ['chebishev fourier transform']  # CHEBYSHEV STATISTICS - conv2_block2_out (256) 

# FILTER_ALGORITHMS = [
# 'edge area',
# 'edge diffdirechist',
# 'edge direction histogram',
# 'edge direction homogeneity',
# 'edge direction mean',
# 'edge direction median',
# 'edge direction variance',
# 'edge magnitude histogram',
# 'edge magnitude mean',
# 'edge magnitude median',
# 'edge magnitude variance']  # EDGE STATISTICS - conv1_conv (64)

# FILTER_ALGORITHMS = [
# 'feature area histogram',
# 'feature areamax',
# 'feature areamean',
# 'feature areamedian',
# 'feature areamin',
# 'feature areavar',
# 'feature count',
# 'feature dist histogram',
# 'feature distmax',
# 'feature distmean',
# 'feature distmedian',
# 'feature distmin',
# 'feature distvar',
# 'feature euler',
# 'feature x centroid',
# 'feature y centroid'             ]  # OBJECT STATISTICS - conv3_block1_out (512)
# FILTER_ALGORITHMS = ['zernike']  # ZERNIKE - conv3_block1_out (512)
# FILTER_ALGORITHMS = ['radon']  # RADON TRANSFORM - conv3_block1_out (512)

# FILTER_ALGORITHMS = ['color histogram']  #  
# FILTER_ALGORITHMS = ['fractal']  # 
# FILTER_ALGORITHMS = ['intensity statistics']  # 
# FILTER_ALGORITHMS = ['tamura texture','haarlick texture','gabor filters','combfirstfourmoments','multiscale histogram','chebishev fourier transform','zernike','radon','color histogram', 'fractal', 'intensity statistics',
#                      'feature area histogram',
# 'feature areamax',
# 'feature areamean',
# 'feature areamedian',
# 'feature areamin',
# 'feature areavar',
# 'feature count',
# 'feature dist histogram',
# 'feature distmax',
# 'feature distmean',
# 'feature distmedian',
# 'feature distmin',
# 'feature distvar',
# 'feature euler',
# 'feature x centroid',
# 'feature y centroid',
# 'edge area',
# 'edge diffdirechist',
# 'edge direction histogram',
# 'edge direction homogeneity',
# 'edge direction mean',
# 'edge direction median',
# 'edge direction variance',
# 'edge magnitude histogram',
# 'edge magnitude mean',
# 'edge magnitude median',
# 'edge magnitude variance'  ]
