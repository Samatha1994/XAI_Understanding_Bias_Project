import psycopg2
import numpy as np

from pipeline_config import get_config

# ============================================================
# Load config
# ============================================================
cfg = get_config()

DB_CONFIG      = cfg["db_config"]
FEATURES_TABLE = cfg["features_table"]
RANGES_TABLE   = cfg["ranges_table"]
NUM_BINS       = cfg["num_bins"]

print(f"▶ Active dataset : {cfg['active_dataset']}")
print(f"▶ Database       : {cfg['db_name']}")
print(f"▶ Features table : {FEATURES_TABLE}")
print(f"▶ Ranges table   : {RANGES_TABLE}")
print(f"▶ Number of bins : {NUM_BINS}")

# ============================================================
# Connect and rebuild ranges table
# ============================================================
conn = psycopg2.connect(**DB_CONFIG)
cur  = conn.cursor()

cur.execute(f"""
DROP TABLE IF EXISTS {RANGES_TABLE};
CREATE TABLE {RANGES_TABLE} (
    id           SERIAL PRIMARY KEY,
    algorithm    TEXT,
    feature_name TEXT,
    bin_label    TEXT,
    bin_start    FLOAT,
    bin_end      FLOAT,
    bin_index    INTEGER,
    min_value    FLOAT,
    max_value    FLOAT
)
""")

# Get min/max per (algorithm, feature_name)
cur.execute(f"""
SELECT algorithm, feature_name, MIN(feature_value), MAX(feature_value)
FROM {FEATURES_TABLE}
GROUP BY algorithm, feature_name
""")
results = cur.fetchall()

for algorithm, feature_name, min_value, max_value in results:
    if min_value == max_value:
        bin_label = (
            f"{algorithm} with {feature_name} "
            f"in {min_value:.5f} to {max_value:.5f}"
        )
        cur.execute(f"""
            INSERT INTO {RANGES_TABLE}
                (algorithm, feature_name, bin_label, bin_start, bin_end,
                 bin_index, min_value, max_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            algorithm, feature_name, bin_label,
            float(min_value), float(max_value),
            0, float(min_value), float(max_value)
        ))
    else:
        bin_edges = np.linspace(min_value, max_value, NUM_BINS + 1)
        for bin_index in range(NUM_BINS):
            bin_start = bin_edges[bin_index]
            bin_end   = bin_edges[bin_index + 1]
            bin_label = (
                f"{algorithm} with {feature_name} "
                f"in {bin_start:.5f} to {bin_end:.5f}"
            )
            cur.execute(f"""
                INSERT INTO {RANGES_TABLE}
                    (algorithm, feature_name, bin_label, bin_start, bin_end,
                     bin_index, min_value, max_value)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                algorithm, feature_name, bin_label,
                float(bin_start), float(bin_end),
                bin_index, float(min_value), float(max_value)
            ))

conn.commit()
cur.close()
conn.close()

print(f"✅ Bin ranges stored in '{RANGES_TABLE}' with min/max included.")
