# import pandas as pd

# df = pd.read_csv(r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_sugarcane/bottom-left/sig_features_output_patches_sugarcane_bottom_left.csv")

# tamura_cols = [c for c in df.columns if c.startswith("Tamura Texture") and c.endswith("()")]
# print(f"Base tamura cols: {tamura_cols}")

# # Images where ALL base tamura columns are NaN
# missing_tamura = df[df[tamura_cols].isnull().all(axis=1)]
# print(f"Images with no tamura values: {len(missing_tamura)}")
# print(missing_tamura[["Path", "Class"]].to_string())

import pandas as pd, os

df = pd.read_csv(r"C:/Users/Dell-PC/OneDrive - Kansas State University/Desktop/XAI-Low Level Features/patches_code/patches_openSprayer/bottom-left/sig_features_output_patches_openSprayer_bottom_left.csv")

basenames = df["Path"].apply(os.path.basename)
print(f"Total images     : {len(df)}")
print(f"Unique full paths: {df['Path'].nunique()}")
print(f"Unique basenames : {basenames.nunique()}")

dupes = basenames[basenames.duplicated(keep=False)]
print(f"\nDuplicate basenames ({len(dupes)}):")
print(df.loc[dupes.index, "Path"].to_string())