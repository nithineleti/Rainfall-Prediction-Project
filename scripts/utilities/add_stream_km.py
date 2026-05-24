import pandas as pd

# Read the cleaned CSV
df = pd.read_csv("data/processed/stage4/watersheds_characterized.csv")

print(f"Current columns: {list(df.columns)}")

# Add stream_km if not exists
if 'stream_km' not in df.columns:
    df['stream_km'] = df['drain_dens'] * df['area_km2']
    print(f"\n✓ Added stream_km column")
    print(f"  Range: {df['stream_km'].min():.3f} - {df['stream_km'].max():.3f} km")
    print(f"  Mean: {df['stream_km'].mean():.3f} km")
    
    # Save
    df.to_csv("data/processed/stage4/watersheds_characterized.csv", index=False)
    print(f"✓ Saved updated CSV")
else:
    print("stream_km already exists")
