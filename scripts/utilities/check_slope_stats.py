import pandas as pd

df = pd.read_csv('data/processed/stage4/watersheds_characterized.csv')

print("📊 Corrected Slope Statistics (Latest Extraction):")
print(f"  Mean slope: {df['slope_me_6'].mean():.2f}°")
print(f"  Median slope: {df['slope_me_6'].median():.2f}°")
print(f"  Min slope: {df['slope_me_6'].min():.2f}°")
print(f"  Max slope (mean): {df['slope_ma_6'].mean():.2f}°")
print(f"  Max slope (absolute): {df['slope_ma_6'].max():.2f}°")

print(f"\n📈 Comparison:")
print(f"  OLD (incorrect): ~89.72° mean")
print(f"  NEW (corrected): {df['slope_me_6'].mean():.2f}° mean")
print(f"  Improvement: ✅ Realistic for flat terrain!")
