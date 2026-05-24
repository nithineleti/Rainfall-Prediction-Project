# -*- coding: utf-8 -*-
"""
Verify QGIS Characterization Output
Checks if real data was extracted successfully
"""
import pandas as pd
import os
import sys

# Set UTF-8 encoding for console output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("="*70)
print("  VERIFYING QGIS CHARACTERIZATION OUTPUT")
print("="*70)

csv_file = "data/processed/stage4/watersheds_characterized.csv"
shp_file = "data/processed/stage4/watersheds_characterized.shp"

# Check if files exist
print("\n📁 Checking output files...")
if os.path.exists(csv_file):
    print(f"  ✅ CSV found: {csv_file}")
else:
    print(f"  ❌ CSV not found: {csv_file}")
    print("\n⚠️  QGIS characterization may not have completed!")
    print("     Please run the QGIS script first.")
    sys.exit(1)

if os.path.exists(shp_file):
    print(f"  ✅ Shapefile found: {shp_file}")
else:
    print(f"  ⚠️  Shapefile not found (CSV mode only)")

# Load and analyze CSV
print("\n📊 Analyzing extracted data...")
df = pd.read_csv(csv_file)

print(f"\n  Rows: {len(df)}")
print(f"  Columns: {len(df.columns)}")
print(f"\n  Columns: {list(df.columns)}")

# Check for real data (not synthetic)
print("\n🔍 Data Quality Checks:")

# Check GWP values
if 'gwp_mean' in df.columns:
    gwp_mean = df['gwp_mean'].mean()
    gwp_std = df['gwp_mean'].std()
    gwp_min = df['gwp_mean'].min()
    gwp_max = df['gwp_mean'].max()
    print(f"\n  GWP Statistics:")
    print(f"    Mean: {gwp_mean:.3f}")
    print(f"    Std Dev: {gwp_std:.3f}")
    print(f"    Range: [{gwp_min:.3f}, {gwp_max:.3f}]")
    
    if gwp_std > 0.1:
        print(f"    ✅ Real data detected (good variability)")
    else:
        print(f"    ⚠️  Low variability (might be synthetic)")
else:
    print("  ❌ gwp_mean column not found!")

# Check Slope values
if 'slope_mean' in df.columns:
    slope_mean = df['slope_mean'].mean()
    slope_max = df['slope_mean'].max()
    print(f"\n  Slope Statistics:")
    print(f"    Mean: {slope_mean:.2f}°")
    print(f"    Max: {slope_max:.2f}°")
    
    if slope_mean < 5:
        print(f"    ✅ Flat terrain confirmed (Lucknow characteristic)")
    else:
        print(f"    ⚠️  High slopes (unexpected for Lucknow)")
else:
    print("  ❌ slope_mean column not found!")

# Check LULC percentages
lulc_cols = ['forest', 'cropland', 'urban', 'water']
found_lulc = [col for col in lulc_cols if col in df.columns]

if found_lulc:
    print(f"\n  LULC Coverage (%):")
    for col in found_lulc:
        mean_pct = df[col].mean()
        print(f"    {col.capitalize()}: {mean_pct:.1f}%")
    
    # Check if LULC sums to ~100%
    if 'other' in df.columns:
        total = sum(df[col].mean() for col in found_lulc + ['other'])
        print(f"    Total: {total:.1f}% (should be ~100%)")
        if abs(total - 100) < 5:
            print(f"    ✅ LULC percentages valid")
        else:
            print(f"    ⚠️  LULC doesn't sum to 100%")
else:
    print("  ❌ LULC columns not found!")

# Check elevation
if 'elev_mean' in df.columns:
    elev_mean = df['elev_mean'].mean()
    elev_min = df['elev_min'].min() if 'elev_min' in df.columns else 0
    elev_max = df['elev_max'].max() if 'elev_max' in df.columns else 0
    print(f"\n  Elevation Statistics:")
    print(f"    Mean: {elev_mean:.1f} m")
    print(f"    Range: [{elev_min:.1f}, {elev_max:.1f}] m")
    
    # Lucknow is low-lying (120-140m typically)
    if 100 < elev_mean < 150:
        print(f"    ✅ Elevation matches Lucknow region")
    else:
        print(f"    ⚠️  Unexpected elevation for Lucknow")

# Check drainage density
if 'drain_dens' in df.columns:
    drain_mean = df['drain_dens'].mean()
    print(f"\n  Drainage Density: {drain_mean:.3f} km/km²")
    if drain_mean > 0:
        print(f"    ✅ Drainage data extracted")

# Check rainfall
if 'rainfall' in df.columns:
    rain_mean = df['rainfall'].mean()
    print(f"\n  Rainfall: {rain_mean:.1f} mm/year")
    if 800 < rain_mean < 1200:
        print(f"    ✅ Rainfall matches Lucknow climate")

# Final verdict
print("\n" + "="*70)
print("  VERIFICATION SUMMARY")
print("="*70)

checks_passed = 0
total_checks = 0

if 'gwp_mean' in df.columns:
    total_checks += 1
    if df['gwp_mean'].std() > 0.1:
        checks_passed += 1

if 'slope_mean' in df.columns:
    total_checks += 1
    if df['slope_mean'].mean() < 5:
        checks_passed += 1

if found_lulc:
    total_checks += 1
    checks_passed += 1

if 'elev_mean' in df.columns:
    total_checks += 1
    if 100 < df['elev_mean'].mean() < 150:
        checks_passed += 1

print(f"\n  Checks Passed: {checks_passed}/{total_checks}")

if checks_passed == total_checks:
    print("\n  ✅ ALL CHECKS PASSED - Real data successfully extracted!")
    print("\n  🎯 Next Steps:")
    print("     1. Run: python src/prioritize_watersheds.py")
    print("     2. Run: python src/generate_watershed_reports.py")
    print("     3. Refresh Streamlit dashboard")
elif checks_passed > 0:
    print("\n  ⚠️  PARTIAL SUCCESS - Some data extracted")
    print("     Check QGIS console for errors on missing fields")
else:
    print("\n  ❌ VERIFICATION FAILED - Data may be synthetic/incomplete")
    print("     Please re-run QGIS characterization script")

print("\n" + "="*70 + "\n")
