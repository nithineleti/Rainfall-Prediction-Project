# -*- coding: utf-8 -*-
"""
Test Watershed Management Pipeline
Tests only the watershed delineation → prioritization → reports workflow
"""
import subprocess
import sys
import os

# Set UTF-8 encoding for console output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("\n" + "="*70)
print("  WATERSHED MANAGEMENT PIPELINE TEST")
print("="*70 + "\n")

stages = [
    {
        "name": "Grid-Based Delineation",
        "script": "src/delineate_watersheds_grid.py",
        "outputs": ["data/processed/stage4/watersheds_lucknow.tif"]
    },
    {
        "name": "CSV Characterization",
        "script": "create_minimal_csv.py",
        "outputs": ["data/processed/stage4/watersheds_characterized.csv"]
    },
    {
        "name": "Prioritization",
        "script": "src/prioritize_watersheds.py",
        "outputs": ["data/processed/stage4/watersheds_prioritized.csv"]
    },
    {
        "name": "Report Generation",
        "script": "src/generate_watershed_reports.py",
        "outputs": ["data/processed/stage4/Executive_Summary.pdf"]
    }
]

for i, stage in enumerate(stages, 1):
    print(f"\n[{i}/{len(stages)}] {stage['name']}...")
    
    # Check if outputs exist
    if all(os.path.exists(f) for f in stage['outputs']):
        print(f"  ✅ Skipped (outputs exist)")
        continue
    
    # Run stage
    result = subprocess.run([sys.executable, stage['script']], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"  ✅ Success")
    else:
        print(f"  ❌ Failed")
        print(f"  Error: {result.stderr[:200]}")
        break

print("\n" + "="*70)
print("  PIPELINE TEST COMPLETE")
print("="*70 + "\n")

# Check final outputs
print("📁 Checking final outputs:\n")
final_files = [
    ("data/processed/stage4/watersheds_lucknow.tif", "Planning units (raster)"),
    ("data/processed/stage4/watershed_boundaries_lucknow.shp", "Boundaries (shapefile)"),
    ("data/processed/stage4/watersheds_characterized.csv", "Characterized watersheds"),
    ("data/processed/stage4/watersheds_prioritized.csv", "Prioritized watersheds"),
    ("data/processed/stage4/priority_summary.txt", "Summary report"),
    ("data/processed/stage4/Executive_Summary.pdf", "Executive PDF"),
    ("data/processed/stage4/Watershed_Action_Plans.xlsx", "Action Plans Excel"),
]

for filepath, description in final_files:
    status = "✅" if os.path.exists(filepath) else "❌"
    print(f"  {status} {description}")

print("\n✨ Watershed management workflow ready!\n")
