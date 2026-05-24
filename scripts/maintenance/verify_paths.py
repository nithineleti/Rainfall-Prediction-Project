"""Quick verification that all critical paths exist after reorganization."""

from path_config import *
import os

print("\n" + "="*50)
print("PATH VERIFICATION AFTER REORGANIZATION")
print("="*50 + "\n")

# Critical paths to verify
paths_to_check = [
    ("Input Data", [
        ("DEM", DEM),
        ("SLOPE", SLOPE),
        ("LULC", LULC),
        ("RAINFALL", RAINFALL),
        ("NDVI", NDVI),
    ]),
    ("Raw Data", [
        ("RAW_DEM", RAW_DEM),
        ("RAW_LULC", RAW_LULC),
        ("RAW_RAINFALL", RAW_RAINFALL),
        ("RAW_NDVI", RAW_NDVI),
        ("RAW_DISTRICT_SHP", RAW_DISTRICT_SHP),
    ]),
    ("Derived Rasters", [
        ("FLOW_ACC", FLOW_ACC),
        ("STREAM_NETWORK", STREAM_NETWORK),
        ("DRAINAGE_DENSITY", DRAINAGE_DENSITY),
        ("TWI", TWI),
    ]),
    ("Feature Stack", [
        ("FEATURES_STACK", FEATURES_STACK),
        ("FEATURES_BANDS_CSV", FEATURES_BANDS_CSV),
    ]),
    ("Vectors", [
        ("WATERSHEDS_CHARACTERIZED", WATERSHEDS_CHARACTERIZED),
        ("WATERSHEDS_PRIORITIZED", WATERSHEDS_PRIORITIZED),
    ]),
    ("Tables", [
        ("TRAIN_SAMPLES_CSV", TRAIN_SAMPLES_CSV),
        ("FEATURE_IMPORTANCE_CSV", FEATURE_IMPORTANCE_CSV),
        ("CV_RESULTS_CSV", CV_RESULTS_CSV),
    ]),
    ("Outputs", [
        ("EXECUTIVE_SUMMARY_PDF", EXECUTIVE_SUMMARY_PDF),
        ("ACTION_PLANS_XLSX", ACTION_PLANS_XLSX),
        ("ML_PREDICTION_CLASS", ML_PREDICTION_CLASS),
    ]),
]

total_paths = 0
existing_paths = 0

for category, paths in paths_to_check:
    print(f"\n{category}:")
    print("-" * 50)
    for name, path in paths:
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        total_paths += 1
        if exists:
            existing_paths += 1
        print(f"  {status} {name}")
        if not exists:
            print(f"    Path: {path}")

print("\n" + "="*50)
print(f"SUMMARY: {existing_paths}/{total_paths} paths verified")
print("="*50 + "\n")

if existing_paths == total_paths:
    print("✅ ALL PATHS VERIFIED - Reorganization successful!")
else:
    print(f"⚠️  {total_paths - existing_paths} paths not found - May need attention")
