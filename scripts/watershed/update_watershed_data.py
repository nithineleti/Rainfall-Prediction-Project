"""
Reprocess watershed characterization with corrected slope data

This script automates the complete workflow after fixing the slope raster:
1. Clean up old outputs
2. Note: QGIS characterization must be run manually in QGIS Python console
3. Extract DBF to CSV
4. Clean column names
5. Run prioritization
6. Generate reports
"""
import os
import subprocess
import sys

print("=" * 60)
print(" WATERSHED CHARACTERIZATION UPDATE WORKFLOW")
print("=" * 60)

# Step 1: Clean old outputs
print("\n[1/5] Cleaning old characterization files...")
old_files = [
    "data/processed/stage4/watersheds_characterized.shp",
    "data/processed/stage4/watersheds_characterized.dbf",
    "data/processed/stage4/watersheds_characterized.shx",
    "data/processed/stage4/watersheds_characterized.prj",
    "data/processed/stage4/watersheds_characterized.cpg",
    "data/processed/stage4/watersheds_characterized.csv",
]

for f in old_files:
    if os.path.exists(f):
        os.remove(f)
        print(f"  ✓ Removed: {f}")

# Step 2: QGIS instruction (must be manual)
print("\n[2/5] QGIS Characterization (MANUAL STEP)")
print("  ⚠️  Open QGIS and run this in the Python Console:")
print("  " + "-" * 55)
print("  exec(open('G:/PROJECTS/watershed-up/qgis_characterize_watersheds.py').read())")
print("  " + "-" * 55)
print("\n  Then press ENTER here to continue...")
input()

# Check if QGIS created the DBF file
dbf_file = "data/processed/stage4/watersheds_characterized.dbf"
if not os.path.exists(dbf_file):
    print(f"  ❌ DBF file not found: {dbf_file}")
    print("     Please run the QGIS script first!")
    sys.exit(1)

print(f"  ✓ DBF file found ({os.path.getsize(dbf_file):,} bytes)")

# Step 3: Extract DBF to CSV
print("\n[3/5] Extracting DBF to CSV...")
result = subprocess.run(["python", "extract_dbf_to_csv.py"], 
                       capture_output=True, text=True)
if result.returncode != 0:
    print(f"  ❌ Error: {result.stderr}")
    sys.exit(1)
print(result.stdout)

# Step 4: Clean column names
print("\n[4/5] Cleaning column names...")
result = subprocess.run(["python", "clean_qgis_output.py"], 
                       capture_output=True, text=True)
if result.returncode != 0:
    print(f"  ❌ Error: {result.stderr}")
    sys.exit(1)
print(result.stdout)

# Step 5: Run prioritization
print("\n[5/5] Running prioritization with corrected data...")
result = subprocess.run(["python", "src/prioritize_watersheds.py"], 
                       capture_output=True, text=True)
if result.returncode != 0:
    print(f"  ❌ Error: {result.stderr}")
    sys.exit(1)
print(result.stdout)

# Generate reports
print("\n[BONUS] Generating reports...")
result = subprocess.run(["python", "src/generate_watershed_reports.py"], 
                       capture_output=True, text=True)
if result.returncode != 0:
    print(f"  ❌ Error: {result.stderr}")
    sys.exit(1)
print(result.stdout)

print("\n" + "=" * 60)
print(" ✅ WORKFLOW COMPLETE!")
print("=" * 60)
print("\n📊 Next steps:")
print("  1. Refresh Streamlit dashboard (Ctrl+R in browser)")
print("  2. Navigate to 'Watershed Management' page")
print("  3. Review updated priority rankings with real slope data")
print("  4. Check reports: outputs/Executive_Summary.pdf")
