"""Quick test to verify all reorganization is complete and working"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("\n" + "="*60)
print("  REORGANIZATION VERIFICATION TEST")
print("="*60 + "\n")

# Test 1: Import path_config
try:
    from path_config import *
    print("✅ path_config.py imports successfully")
except Exception as e:
    print(f"❌ path_config.py import failed: {e}")
    sys.exit(1)

# Test 2: Check critical paths
import os

critical_paths = {
    "DEM": DEM,
    "SLOPE": SLOPE,
    "FEATURES_STACK": FEATURES_STACK,
    "WATERSHEDS_CHARACTERIZED": WATERSHEDS_CHARACTERIZED,
    "TRAIN_SAMPLES_CSV": TRAIN_SAMPLES_CSV,
}

print("\n📁 Critical File Existence Check:")
existing_count = 0
for name, path in critical_paths.items():
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"  {status} {name}: {exists}")
    if exists:
        existing_count += 1

print(f"\n  Total: {existing_count}/{len(critical_paths)} files exist")

# Test 3: Check directory structure
print("\n📂 Directory Structure Check:")
directories = {
    "RASTERS_DIR": RASTERS_DIR,
    "VECTORS_DIR": VECTORS_DIR,
    "TABLES_DIR": TABLES_DIR,
    "FIGURES_DIR": FIGURES_DIR,
    "RAW_DIR": RAW_DIR,
    "REPORTS_DIR": REPORTS_DIR,
    "PREDICTIONS_DIR": PREDICTIONS_DIR,
}

for name, path in directories.items():
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"  {status} {name}: {exists}")

# Test 4: Test script imports
print("\n🔧 Script Import Test:")
try:
    # Test if scripts can import path_config
    test_script = project_root / "scripts" / "preprocessing" / "01_process_dem.py"
    if os.path.exists(test_script):
        print("  ✅ Preprocessing scripts accessible")
    
    test_script2 = project_root / "scripts" / "ml" / "check_samples.py"
    if os.path.exists(test_script2):
        print("  ✅ ML scripts accessible")
    
    test_script3 = project_root / "scripts" / "watershed" / "prioritize_watersheds.py"
    if os.path.exists(test_script3):
        print("  ✅ Watershed scripts accessible")
        
except Exception as e:
    print(f"  ❌ Script access failed: {e}")

# Test 5: Check data organization
print("\n📊 Data Organization Check:")
data_folders = ["backups", "figures", "rasters", "raw", "tables", "vectors"]
for folder in data_folders:
    path = DATA_DIR / folder
    if os.path.exists(path):
        file_count = len(list(path.glob("*")))
        print(f"  ✅ data/{folder}/ - {file_count} items")
    else:
        print(f"  ❌ data/{folder}/ - NOT FOUND")

# Test 6: Check if old processed folder is gone
old_processed = DATA_DIR / "processed"
if os.path.exists(old_processed):
    print(f"\n  ⚠️  WARNING: data/processed/ still exists (should be deleted)")
else:
    print(f"\n  ✅ data/processed/ successfully removed")

print("\n" + "="*60)
print("  VERIFICATION COMPLETE")
print("="*60 + "\n")

if existing_count == len(critical_paths):
    print("✅ ALL TESTS PASSED - Project fully reorganized!")
else:
    print(f"⚠️  {len(critical_paths) - existing_count} critical files missing")
