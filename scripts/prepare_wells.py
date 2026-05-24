# scripts/prepare_wells.py
import pandas as pd
import os
from path_config import RAW_WELLS_WDC, RAW_WELLS_DIR

IN = str(RAW_WELLS_WDC)
OUT_DIR = str(RAW_WELLS_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(IN)

# 1) Version A: rows that already have Rise/Fall (exactly what you got)
if 'Rise/Fall' in df.columns:
    df_v1 = df.dropna(subset=['Rise/Fall']).copy()
    df_v1_clean = df_v1.rename(columns={"X":"lon", "Y":"lat", "WELL_ID":"id"})
    df_v1_clean = df_v1_clean[['id','lon','lat','Rise/Fall']].rename(columns={'Rise/Fall':'target'})
    out1 = os.path.join(OUT_DIR, "wells_cgwb.csv")
    df_v1_clean.to_csv(out1, index=False)
    print(f"Wrote {len(df_v1_clean)} rows to {out1}")
else:
    print("Column 'Rise/Fall' not found in input file.")

# 2) Version B: infer missing Rise/Fall from PRM_Trend sign when possible
df2 = df.copy()
# create 'target' column from existing Rise/Fall where present
if 'Rise/Fall' in df2.columns:
    df2['target'] = df2['Rise/Fall'].astype(object)
else:
    df2['target'] = pd.NA

# infer from PRM_Trend if target missing (positive -> Rise, negative or zero -> Fall)
if 'PRM_Trend' in df2.columns:
    mask = df2['target'].isna() & df2['PRM_Trend'].notna()
    df2.loc[mask, 'target'] = df2.loc[mask, 'PRM_Trend'].apply(lambda x: 'Rise' if x > 0 else 'Fall')
else:
    print("Column 'PRM_Trend' not found; cannot infer labels.")

# keep only rows with id, coords and target
df2_clean = df2.rename(columns={"X":"lon", "Y":"lat", "WELL_ID":"id"})
cols_needed = ['id','lon','lat','target']
df2_clean = df2_clean[[c for c in cols_needed if c in df2_clean.columns]].dropna(subset=['lon','lat','target'])
out2 = os.path.join(OUT_DIR, "wells_cgwb_inferred.csv")
df2_clean.to_csv(out2, index=False)
print(f"Wrote {len(df2_clean)} rows to {out2} (inferred labels used where Rise/Fall was missing)")

# Print quick summary
print("\nSummary:")
print(" Original rows:", len(df))
if 'Rise/Fall' in df.columns:
    print(" Rows with Rise/Fall present:", df['Rise/Fall'].notna().sum())
if 'PRM_Trend' in df.columns:
    print(" Rows with PRM_Trend present:", df['PRM_Trend'].notna().sum())
print(" V1 rows (explicit Rise/Fall):", len(df_v1_clean) if 'df_v1_clean' in locals() else 0)
print(" V2 rows (inferred):", len(df2_clean))
