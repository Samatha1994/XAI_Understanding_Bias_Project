"""
validate_concepts.py
=====================
Validates DL-Learner CELOE concepts against holdout images using PostgreSQL.

PIPELINE:
  For each neuron_X_output.txt (layer/feature/neuron):
    1. Parse best CELOE concept -> extract feature constraints
    2. For each holdout image, check concept satisfaction using DB feature values
       - Uses FULL FEATURE RANGE (min_value to max_value from udat_feature_ranges)
         instead of specific bin range.
    3. Split holdout into concept-positive / concept-negative
    4. One-sided Mann-Whitney U test on neuron activations (positive > negative)
       - Minimum 5 images required in both positive and negative groups
    5. Cliff's delta effect size
    6. Save per-feature CSV + master CSV

CHANGES FROM PREVIOUS VERSION:
    1. All paths/settings moved to validate_config.py
    2. Bin check replaced with full feature range check (min_value to max_value)
    3. Minimum sample size increased from 3 to 5

USAGE:
    1. Set ACTIVE_DATASET and ACTIVE_PATCH in validate_config.py
    2. Run: python validate_concepts.py
"""

import os
import re
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
import psycopg2
import psycopg2.extras
import warnings
warnings.filterwarnings('ignore')

from validate_config import get_validate_config

# ── Load config ───────────────────────────────────────────────
cfg = get_validate_config()

BASE_PATH       = cfg["base_path"]
HOLDOUT_FILE    = cfg["holdout_file"]
ACTIVATIONS_DIR = cfg["activations_dir"]
OUTPUT_DIR      = cfg["output_dir"]
FEATURES_TABLE  = cfg["features_table"]
RANGES_TABLE    = cfg["ranges_table"]
DB_CONFIG       = cfg["db_config"]
ALPHA           = cfg["alpha"]
MIN_GROUP_SIZE  = cfg["min_group_size"]
IMAGE_NAME_FORMAT = cfg["image_name_format"]   # "filename" or "class/filename"

CLIFFS_THRESHOLDS = [
    (0.147, "negligible"),
    (0.330, "small"),
    (0.474, "medium"),
    (1.001, "large"),
]

# ─── LAYER -> ACTIVATION CSV MAP ─────────────────────────────────────────────

ARCH_CSV_MAP = {
    "resnet_conv3_block4_out":       "ResNet50V2_mid2_conv3_block4_out_activations.csv",
    "resnet_conv4_block6_out":       "ResNet50V2_mid_deep_conv4_block6_out_activations.csv",
    "resnet_conv5_block3_out":       "ResNet50V2_deep_conv5_block3_out_activations.csv",
    "densenet_conv3_block12_concat": "DenseNet121_mid_conv3_block12_concat_activations.csv",
    "densenet_conv4_block24_concat": "DenseNet121_mid_deep_conv4_block24_concat_activations.csv",
    "densenet_deep_relu":            "DenseNet121_deep_relu_activations.csv",
    "InceptionV3_mixed5":            "InceptionV3_mid_mixed5_activations.csv",
    "InceptionV3_mixed7":            "InceptionV3_mid_deep_mixed7_activations.csv",
    "InceptionV3_mixed10":           "InceptionV3_deep_mixed10_activations.csv",
    "VGG16_block3_conv3":            "VGG16_mid_block3_conv3_activations.csv",
    "VGG16_block4_conv3":            "VGG16_mid_deep_block4_conv3_activations.csv",
    "VGG16_block5_conv3":            "VGG16_deep_block5_conv3_activations.csv",
}

# ─── DL-LEARNER FAMILY -> DB ALGORITHM NAME ──────────────────────────────────

FAMILY_TO_ALGORITHM = {
    "chebishevfouriertransform":        "chebishev fourier transform",
    "chebishevstatistics":              "chebishev fourier transform",
    "chebishev":                        "chebishev fourier transform",
    "tamuratexture":                    "tamura texture",
    "tamura":                           "tamura texture",
    "haarlicktexture":                  "haarlick texture",
    "haarlick":                         "haarlick texture",
    "haralick":                         "haarlick texture",
    "combfirstfourmoments":             "combfirstfourmoments",
    "combinefirstfourmoments":          "combfirstfourmoments",
    "multiscalehistogram":              "multiscale histogram",
    "multiscale":                       "multiscale histogram",
    "zernike":                          "zernike",
    "radon":                            "radon",
    "gaborfilters":                     "gabor filters",
    "gabor":                            "gabor filters",
    "fractal":                          "fractal",
    "edgediffdirechist":                "edge diffdirechist",
    "edgedirectionhistogram":           "edge direction histogram",
    "edgedirectionhomogeneity":         "edge direction homogeneity",
    "edgedirectionmean":                "edge direction mean",
    "edgedirectionmedian":              "edge direction median",
    "edgedirectionvariance":            "edge direction variance",
    "edgemagnitudehistogram":           "edge magnitude histogram",
    "edgemagnitudemean":                "edge magnitude mean",
    "edgemagnitudemedian":              "edge magnitude median",
    "edgemagnitudevariance":            "edge magnitude variance",
    "edgearea":                         "edge area",
    "edge":                             "edge area",
    "featureareahistogram":             "feature area histogram",
    "featureareamax":                   "feature areamax",
    "featureareamean":                  "feature areamean",
    "featureareamedian":                "feature areamedian",
    "featureareamin":                   "feature areamin",
    "featureareavar":                   "feature areavar",
    "featurecount":                     "feature count",
    "featuredisthistogram":             "feature dist histogram",
    "featuredistmax":                   "feature distmax",
    "featuredistmean":                  "feature distmean",
    "featuredistmedian":                "feature distmedian",
    "featuredistmin":                   "feature distmin",
    "featuredistvar":                   "feature distvar",
    "featureeuler":                     "feature euler",
    "featurexcentroid":                 "feature x centroid",
    "featureycentroid":                 "feature y centroid",
    "feature":                          "feature count",
    "intensitystatistics":              "intensity statistics",
    "intensity":                        "intensity statistics",
    "colorhistogram":                   "color histogram",
    "color":                            "color histogram",
}


# ─── UTILITIES ────────────────────────────────────────────────────────────────

def stem_from_path(path_str):
    return os.path.splitext(os.path.basename(str(path_str)))[0]


def cliffs_delta(pos, neg):
    nx, ny = len(pos), len(neg)
    if nx == 0 or ny == 0:
        return 0.0
    dom = sum(1 if xi > yj else (-1 if xi < yj else 0)
              for xi in pos for yj in neg)
    return dom / (nx * ny)


def cliffs_magnitude(d):
    abs_d = abs(d)
    for threshold, label in CLIFFS_THRESHOLDS:
        if abs_d < threshold:
            return label
    return "large"


def map_family(dl_family):
    dl_family = dl_family.lower()
    if dl_family in FAMILY_TO_ALGORITHM:
        return FAMILY_TO_ALGORITHM[dl_family]
    best, best_len = None, 0
    for key, val in FAMILY_TO_ALGORITHM.items():
        if dl_family.startswith(key) and len(key) > best_len:
            best, best_len = val, len(key)
    return best


def bin_str_to_float(s):
    s = s.strip()
    negative = s.startswith('neg')
    if negative:
        s = s[3:]
    parts = s.split('_', 1)
    val = float(parts[0] + '.' + parts[1]) if len(parts) == 2 else float(parts[0])
    return -val if negative else val


# ─── DATA LOADING ─────────────────────────────────────────────────────────────

# def load_holdout_stems(holdout_file):
#     with open(holdout_file, 'r') as f:
#         lines = [l.strip() for l in f if l.strip()]
#     stems = set(stem_from_path(l) for l in lines)
#     print(f"  Holdout images: {len(stems)}")
#     return stems
# def load_holdout_stems(holdout_file):
#     with open(holdout_file, 'r') as f:
#         lines = [l.strip() for l in f if l.strip()]
#     if IMAGE_NAME_FORMAT == "class/filename":
#         stems = set(os.path.splitext(l)[0] for l in lines)   # keeps class/imagename
#     else:
#         stems = set(stem_from_path(l) for l in lines)         # just imagename
#     print(f"  Holdout images: {len(stems)}")
#     return stems
def load_holdout_stems(holdout_file):
    with open(holdout_file, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    stems = set(stem_from_path(l) for l in lines)   # always strip to just imagename
    print(f"  Holdout images: {len(stems)}")
    return stems


# def build_feature_cache(conn, holdout_stems):
#     print(f"  Querying DB for {len(holdout_stems)} holdout images...")
#     tiff_names = [s + '.tiff' for s in holdout_stems]
#     query = f"""
#         SELECT image_name, algorithm, feature_name, feature_value
#         FROM {FEATURES_TABLE}
#         WHERE image_name = ANY(%s)
#     """
#     cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#     cur.execute(query, (tiff_names,))
#     rows = cur.fetchall()
#     cur.close()

#     cache = {}
#     for row in rows:
#         stem = stem_from_path(row['image_name'])
#         alg  = row['algorithm'].strip().lower()
#         feat = row['feature_name'].strip().lower()
#         val  = float(row['feature_value'])
#         if stem not in cache:
#             cache[stem] = {}
#         cache[stem][(alg, feat)] = val
#         if feat == alg:
#             cache[stem][(alg, alg)] = val

#     print(f"  Cache built: {len(cache)} images, {len(rows):,} feature rows")
#     return cache

def build_feature_cache(conn, holdout_stems):
    print(f"  Querying DB for {len(holdout_stems)} holdout images...")
    tiff_names = [s + '.tiff' for s in holdout_stems]
    query = f"""
        SELECT image_name, algorithm, feature_name, feature_value
        FROM {FEATURES_TABLE}
        WHERE image_name = ANY(%s)
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query, (tiff_names,))
    rows = cur.fetchall()
    cur.close()

    cache = {}
    # for row in rows:
    #     if IMAGE_NAME_FORMAT == "class/filename":
    #         stem = os.path.splitext(row['image_name'])[0]   # keeps class/imagename
    #     else:
    #         stem = stem_from_path(row['image_name'])          # just imagename
    #     alg  = row['algorithm'].strip().lower()
    #     feat = row['feature_name'].strip().lower()
    #     val  = float(row['feature_value'])
    #     if stem not in cache:
    #         cache[stem] = {}
    #     cache[stem][(alg, feat)] = val
    #     if feat == alg:
    #         cache[stem][(alg, alg)] = val

    for row in rows:
        stem = stem_from_path(row['image_name'])   # always just imagename
        alg  = row['algorithm'].strip().lower()
        feat = row['feature_name'].strip().lower()
        val  = float(row['feature_value'])
        if stem not in cache:
            cache[stem] = {}
        cache[stem][(alg, feat)] = val
        if feat == alg:
            cache[stem][(alg, alg)] = val

    print(f"  Cache built: {len(cache)} images, {len(rows):,} feature rows")
    print(f"  Sample stems in cache: {list(cache.keys())[:5]}")
    return cache


def build_range_cache(conn):
    print(f"  Loading feature ranges from {RANGES_TABLE}...")
    query = f"""
        SELECT algorithm, feature_name, min_value, max_value
        FROM {RANGES_TABLE}
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()

    range_cache = {}
    for row in rows:
        alg  = row['algorithm'].strip().lower()
        feat = row['feature_name'].strip().lower()
        rmin = float(row['min_value'])
        rmax = float(row['max_value'])
        range_cache[(alg, feat)] = (rmin, rmax)
        if feat == alg:
            range_cache[(alg, alg)] = (rmin, rmax)

    print(f"  Range cache built: {len(range_cache)} feature entries")
    return range_cache


def load_activation_csv(layer_name):
    csv_name = ARCH_CSV_MAP.get(layer_name)
    if not csv_name:
        print(f"    [WARN] No activation CSV for layer: {layer_name}")
        return None
    csv_path = os.path.join(ACTIVATIONS_DIR, csv_name)
    if not os.path.exists(csv_path):
        print(f"    [WARN] Activation CSV missing: {csv_path}")
        return None
    df = pd.read_csv(csv_path, header=0)
    df['stem'] = df['filenames'].apply(stem_from_path)
    df = df.set_index('stem').drop(columns=['filenames'], errors='ignore')
    df.columns = [str(c) for c in df.columns]
    return df


# ─── CONCEPT PARSING ──────────────────────────────────────────────────────────

def parse_best_concept(output_text):
    m = re.search(
        r'solutions?[^:]*:\s*\n(1:.*?)(?=\n2:|\Z)',
        output_text, re.DOTALL | re.IGNORECASE
    )
    if not m:
        return None, None
    line = m.group(1).strip()
    acc = re.search(r'pred\. acc\.: ([\d.]+)%', line)
    return line, (float(acc.group(1)) if acc else None)


def parse_concept_constraints(concept_str):
    constraints = []
    bin_ref_pattern = (
        r'(\w+?)Bin_'
        r'(neg\d+(?:_\d+)?|\d+(?:_\d+)?)'
        r'_(neg\d+(?:_\d+)?|\d+(?:_\d+)?)'
    )
    prop_pattern = r'has(\w+)\s+(?:only|some)\s+'

    for prop_match in re.finditer(prop_pattern, concept_str, re.IGNORECASE):
        prop_name   = prop_match.group(1)
        bin_num     = None
        sub_feature = None
        parts       = prop_name.split('_', 1)
        if len(parts) == 2:
            family      = parts[0].lower()
            sub_feature = parts[1].lower()
        else:
            family      = prop_name.lower()
            sub_feature = None

        start     = prop_match.end()
        next_has  = re.search(r'\bhas\w+\s+(?:only|some)', concept_str[start:])
        block_end = start + (next_has.start() if next_has else 400)
        block     = concept_str[start:block_end]

        for bin_match in re.finditer(bin_ref_pattern, block, re.IGNORECASE):
            raw_low    = bin_match.group(2)
            raw_high   = bin_match.group(3)
            pre        = block[max(0, bin_match.start() - 20): bin_match.start()]
            is_negated = bool(re.search(r'\bnot\b\s*\(?\s*$', pre, re.IGNORECASE))

            try:
                bin_low  = bin_str_to_float(raw_low)
                bin_high = bin_str_to_float(raw_high)
            except Exception:
                continue

            if bin_low == bin_high:
                continue

            actual_bin_num = bin_num
            if actual_bin_num is None:
                bin_class = bin_match.group(1).lower()
                bn2 = re.search(r'bin(\d+)$', bin_class)
                if bn2:
                    actual_bin_num = int(bn2.group(1))

            alg = map_family(family)
            if alg is None:
                print(f"    [WARN] Could not map family: '{family}' from property: '{prop_name}'")
                continue

            constraint = {
                'dl_family':   family,
                'sub_feature': sub_feature,
                'bin_number':  actual_bin_num,
                'bin_start':   bin_low,
                'bin_end':     bin_high,
                'algorithm':   alg,
                'negated':     is_negated,
            }
            if constraint not in constraints:
                constraints.append(constraint)

    return constraints


# ─── CONCEPT CHECKING ─────────────────────────────────────────────────────────

def satisfies_concept(stem, constraints, feature_cache, range_cache=None):
    """
    Checks concept satisfaction using SPECIFIC BIN RANGE from the DL-Learner concept.
    (bin_start to bin_end as parsed from the CELOE concept string)

    For each constraint:
      - negated=False: feature value must be INSIDE  [bin_start, bin_end)
      - negated=True:  feature value must be OUTSIDE [bin_start, bin_end)

    Lookup order for feature value:
      1. Histogram key: (algorithm, "binN")
      2. Named sub-feature: (algorithm, sub_feature)
      3. Scalar fallback: (algorithm, algorithm)
    """
    img = feature_cache.get(stem, {})
    if not img:
        return False

    for c in constraints:
        alg = c['algorithm']
        val = None

        if c['bin_number'] is not None:
            val = img.get((alg, f"bin{c['bin_number']}"))
        if val is None and c.get('sub_feature'):
            val = img.get((alg, c['sub_feature']))
        if val is None:
            val = img.get((alg, alg))
        if val is None:
            return False

        in_bin = (c['bin_start'] <= val < c['bin_end'])

        if c['negated']:
            if in_bin:
                return False
        else:
            if not in_bin:
                return False

    return True


# ─── STATISTICAL TESTS ────────────────────────────────────────────────────────

def run_stats(neuron_id, pos_stems, neg_stems, act_df):
    if act_df is None:
        return None, None, None, None, "No activation CSV"

    col = str(neuron_id)
    if col not in act_df.columns:
        return None, None, None, None, f"Neuron {neuron_id} not in CSV"

    if len(pos_stems) < MIN_GROUP_SIZE:
        return None, None, None, None, f"Too few positives ({len(pos_stems)})"
    if len(neg_stems) < MIN_GROUP_SIZE:
        return None, None, None, None, f"Too few negatives ({len(neg_stems)})"

    pos_acts = act_df.loc[act_df.index.isin(pos_stems), col].dropna().values
    neg_acts = act_df.loc[act_df.index.isin(neg_stems), col].dropna().values

    if len(pos_acts) < MIN_GROUP_SIZE or len(neg_acts) < MIN_GROUP_SIZE:
        return None, None, None, None, "Insufficient matched activations"

    try:
        stat, p_val = mannwhitneyu(pos_acts, neg_acts, alternative='greater')
        d   = cliffs_delta(pos_acts.tolist(), neg_acts.tolist())
        mag = cliffs_magnitude(d)
        note = (f"pos_mean={pos_acts.mean():.3f} neg_mean={neg_acts.mean():.3f} "
                f"n_pos={len(pos_acts)} n_neg={len(neg_acts)}")
        return round(stat, 4), round(p_val, 6), round(d, 4), mag, note
    except Exception as e:
        return None, None, None, None, f"Stats error: {e}"


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 65)
    print(f" Concept Validation")
    print(f" Dataset      : {cfg['active_dataset']}")
    print(f" Patch        : {cfg['active_patch']}")
    # print(f" Bin check    : FULL FEATURE RANGE (min_value to max_value)")
    print(f" Bin check    : SPECIFIC BIN RANGE (bin_start to bin_end)")
    print(f" Min group sz : {MIN_GROUP_SIZE}")
    print("=" * 65)

    print("\n[1] Loading holdout images...")
    holdout_stems = load_holdout_stems(HOLDOUT_FILE)
    print(f"  Sample holdout stems: {list(holdout_stems)[:5]}")

    print("\n[2] Loading holdout features and feature ranges from DB...")
    try:
        conn          = psycopg2.connect(**DB_CONFIG)
        feature_cache = build_feature_cache(conn, holdout_stems)
        conn.close()
    except Exception as e:
        print(f"  [ERROR] DB failed: {e}")
        return

    print("\n[3] Processing concepts...")
    all_results = []
    act_cache   = {}

    layer_folders = sorted([
        d for d in os.listdir(BASE_PATH)
        if os.path.isdir(os.path.join(BASE_PATH, d))
    ])

    for layer_name in layer_folders:
        layer_path = os.path.join(BASE_PATH, layer_name)
        print(f"\n>>> Layer: {layer_name}")

        if layer_name not in act_cache:
            act_cache[layer_name] = load_activation_csv(layer_name)
        act_df = act_cache[layer_name]

        feat_dirs = sorted([
            d for d in os.listdir(layer_path)
            if os.path.isdir(os.path.join(layer_path, d))
        ])

        for feature_name in feat_dirs:
            feat_path = os.path.join(layer_path, feature_name)

            output_files = sorted(
                [f for f in os.listdir(feat_path)
                #  if re.match(r'neuron_\d+_output\.txt', f)],
                 if re.match(r'neuron_\d+_output_file\.txt', f)],
                key=lambda f: int(re.search(r'neuron_(\d+)', f).group(1))
            )
            if not output_files:
                continue

            print(f"  >> {feature_name} ({len(output_files)} neurons)")
            feat_results = []

            for fname in output_files:
                neuron_id = int(re.search(r'neuron_(\d+)', fname).group(1))
                with open(os.path.join(feat_path, fname),
                          'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                concept_str, celoe_acc = parse_best_concept(content)

                row = {
                    'layer':              layer_name,
                    'feature':            feature_name,
                    'neuron_id':          neuron_id,
                    'concept':            (concept_str[:300] if concept_str else ''),
                    'celoe_accuracy':     celoe_acc,
                    'n_holdout_total':    len(holdout_stems),
                    'n_concept_positive': 0,
                    'n_concept_negative': 0,
                    'mw_statistic':       None,
                    'p_value':            None,
                    'cliffs_delta':       None,
                    'effect_size':        None,
                    'significant':        None,
                    'validated':          False,
                    'coverage':           None,
                    'ci_precision_proxy': (round(celoe_acc / 100, 4) if celoe_acc else None),
                    'ci_f1_proxy':        None,
                    'notes':              '',
                }

                if not concept_str:
                    row['notes'] = 'No concept found'
                    feat_results.append(row)
                    continue

                constraints = parse_concept_constraints(concept_str)
                if not constraints:
                    row['notes'] = 'Could not parse constraints'
                    feat_results.append(row)
                    continue

                all_negated  = all(c['negated'] for c in constraints)
                row['notes'] = 'negated concept' if all_negated else ''

                pos_stems = [s for s in holdout_stems
                             if satisfies_concept(s, constraints, feature_cache)]
                neg_stems = [s for s in holdout_stems
                             if not satisfies_concept(s, constraints, feature_cache)]

                row['n_concept_positive'] = len(pos_stems)
                row['n_concept_negative'] = len(neg_stems)

                n_total      = len(pos_stems) + len(neg_stems)
                row['coverage'] = round(len(pos_stems) / n_total, 4) if n_total > 0 else 0.0

                prec = row['ci_precision_proxy']
                cov  = row['coverage']
                if prec and cov and (prec + cov) > 0:
                    row['ci_f1_proxy'] = round(2 * prec * cov / (prec + cov), 4)

                stat, p_val, delta, mag, note = run_stats(
                    neuron_id, pos_stems, neg_stems, act_df
                )
                if note:
                    row['notes'] = (row['notes'] + ' | ' + note).strip(' | ')

                row.update({
                    'mw_statistic': stat,
                    'p_value':      p_val,
                    'cliffs_delta': delta,
                    'effect_size':  mag,
                })
                if stat is not None:
                    row['significant'] = p_val < ALPHA
                    row['validated']   = (p_val < ALPHA) and (mag in ('medium', 'large'))

                feat_results.append(row)

            feat_df  = pd.DataFrame(feat_results)
            feat_csv = os.path.join(feat_path, 'validation_results.csv')
            try:
                feat_df.to_csv(feat_csv, index=False)
            except PermissionError:
                fallback = feat_csv.replace('.csv', '_new.csv')
                feat_df.to_csv(fallback, index=False)
                print(f"     [WARN] File locked, saved to: {fallback}")

            n_val      = feat_df['validated'].sum()
            n_negated  = (feat_df['notes'].str.startswith('negated', na=False)).sum()
            n_no_parse = (feat_df['notes'] == 'Could not parse constraints').sum()
            print(f"     Validated: {n_val}/{len(feat_results)} | "
                  f"Negated: {n_negated} | No parse: {n_no_parse}")
            all_results.extend(feat_results)

    print(f"\n[4] Saving master results...")
    master_df  = pd.DataFrame(all_results)
    master_csv = os.path.join(OUTPUT_DIR, 'master_validation_results.csv')
    try:
        master_df.to_csv(master_csv, index=False)
    except PermissionError:
        fallback = os.path.join(OUTPUT_DIR, 'master_validation_results_new.csv')
        master_df.to_csv(fallback, index=False)
        print(f"  [WARN] Master CSV locked, saved to: {fallback}")

    # Summary
    total       = len(master_df)
    no_con      = (master_df['concept'] == '').sum()
    no_parse    = (master_df['notes'] == 'Could not parse constraints').sum()
    negated     = master_df['notes'].str.startswith('negated', na=False).sum()
    sig         = master_df['significant'].sum()
    validated   = master_df['validated'].sum()
    processable = total - no_con - no_parse
    too_few     = master_df['notes'].str.contains('Too few', na=False).sum()
    insuff      = master_df['notes'].str.contains('Insufficient', na=False).sum()
    stats_err   = master_df['notes'].str.contains('Stats error', na=False).sum()
    negated_val = (master_df['validated'] &
                   master_df['notes'].str.startswith('negated', na=False)).sum()
    pos_val     = int(validated) - int(negated_val)
    no_stats    = (master_df['mw_statistic'].isna() &
                   (master_df['notes'] != 'No concept found') &
                   (master_df['notes'] != 'Could not parse constraints')).sum()
    ran_stats   = master_df['mw_statistic'].notna().sum()
    not_sig     = int(ran_stats) - int(sig)
    sig_not_val = int(sig) - int(validated)

    print(f"\n{'='*65}")
    print(f" VALIDATION SUMMARY")
    print(f" Dataset      : {cfg['active_dataset']}  |  Patch: {cfg['active_patch']}")
    print(f" Bin check    : FULL FEATURE RANGE")
    print(f" Min group sz : {MIN_GROUP_SIZE}")
    print(f"{'='*65}")
    print(f" Total neurons                                : {total}")
    print(f" No concept found (Thing/Image only)          : {no_con}")
    print(f" Could not parse constraints                  : {no_parse}")
    print(f" Processable neurons                          : {processable}")
    print(f"   of which negated concepts                  : {negated}")
    print(f"")
    print(f" --- Breakdown of processable neurons ---")
    print(f" Stats could not run                          : {no_stats}")
    print(f"   Too few concept-positive/negative (< {MIN_GROUP_SIZE})   : {too_few}")
    print(f"   Insufficient matched activations           : {insuff}")
    print(f"   Other stats errors                         : {stats_err}")
    print(f" Stats ran but p >= 0.05 (not significant)    : {not_sig}")
    print(f" Significant but effect size too small        : {sig_not_val}")
    print(f" Validated (p<0.05 + medium/large d)          : {validated}")
    print(f"")
    print(f" Validated — positive concepts                : {pos_val}")
    print(f" Validated — negated concepts                 : {negated_val}")
    print(f" Validation rate                              : {100*validated/max(processable,1):.1f}%")
    print(f" Master CSV -> {master_csv}")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
