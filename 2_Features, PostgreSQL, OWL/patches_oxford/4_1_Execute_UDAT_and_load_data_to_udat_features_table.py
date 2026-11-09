import pandas as pd
import psycopg2
import os
import re

from pipeline_config import get_config

# ============================================================
# Feature column parser — transform context included in algorithm
# ============================================================

STANDALONE_STATS = {
    "image entropy", "gini coefficient", "entropy",
    "mean", "median", "stddev", "min", "max"
}

def parse_feature_column(raw_col):
    """
    Parse a raw UDAT column name into (algorithm, feature_name).
    See original script for full logic documentation.
    """
    suffix_match = re.search(r'\(([^)]*)\)\s*$', raw_col)
    if suffix_match:
        context = suffix_match.group(1).strip()
        core    = raw_col[:suffix_match.start()].strip()
    else:
        context = ""
        core    = raw_col.strip()

    core_norm    = re.sub(r'\s+', ' ', core).lower().strip()
    context_norm = re.sub(r'\s+', ' ', context).lower().strip()

    def with_context(alg):
        return f"{alg} {context_norm}".strip() if context_norm else alg

    if core_norm in STANDALONE_STATS:
        return with_context("intensity statistics"), core_norm

    match = re.match(r'^(.*?)\s*(?:bin\s*)?(\d+)$', core_norm)
    if match:
        algorithm    = match.group(1).strip().rstrip('_').strip()
        feature_name = f"bin{match.group(2)}"
        return with_context(algorithm), feature_name

    return with_context(core_norm), core_norm


# ============================================================
# Load config
# ============================================================
cfg = get_config()

CSV_PATH       = cfg["csv_path"]
DB_CONFIG      = cfg["db_config"]
FEATURES_TABLE = cfg["features_table"]

print(f"▶ Active dataset : {cfg['active_dataset']}")
print(f"▶ CSV path       : {CSV_PATH}")
print(f"▶ Database       : {cfg['db_name']}")
print(f"▶ Features table : {FEATURES_TABLE}")

# ============================================================
# Step 1: Load CSV
# ============================================================
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ CSV not found at: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)
print(f"✅ Loaded CSV — shape: {df.shape}")

assert df.columns[0] == "Path",  f"Expected col 0 = 'Path', got '{df.columns[0]}'"
assert df.columns[1] == "Class", f"Expected col 1 = 'Class', got '{df.columns[1]}'"

# ============================================================
# Step 2: Create table and insert features
# ============================================================
conn = psycopg2.connect(**DB_CONFIG)
cur  = conn.cursor()

cur.execute(f"""
CREATE TABLE IF NOT EXISTS {FEATURES_TABLE} (
    id            SERIAL PRIMARY KEY,
    image_name    TEXT,
    image_path    TEXT,
    algorithm     TEXT,
    feature_name  TEXT,
    feature_value FLOAT,
    class_name    TEXT
)
""")
conn.commit()

inserted = 0
skipped  = 0

for _, row in df.iterrows():
    image_path = row["Path"].strip()
    image_name = os.path.basename(image_path)
    class_name = row["Class"].strip()

    for col_name, feature_value in row.iloc[2:].items():
        try:
            feature_value = float(feature_value)
            algorithm_part, feature_part = parse_feature_column(col_name)

            cur.execute(f"""
                INSERT INTO {FEATURES_TABLE}
                    (image_name, image_path, algorithm, feature_name, feature_value, class_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (image_name, image_path, algorithm_part, feature_part, feature_value, class_name))
            inserted += 1

        except (ValueError, TypeError):
            skipped += 1
            continue

conn.commit()
cur.close()
conn.close()

print(f"✅ Done! Inserted: {inserted} rows | Skipped (non-numeric): {skipped} rows")
