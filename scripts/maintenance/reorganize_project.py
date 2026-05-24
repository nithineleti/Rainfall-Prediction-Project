"""
Project Reorganization Script
Consolidates scattered files into clean structure
"""
import os
import shutil
from pathlib import Path

print("\n" + "="*60)
print("WATERSHED PROJECT REORGANIZATION")
print("="*60 + "\n")

# Create new directory structure
print("[1/8] Creating new directory structure...")
new_dirs = [
    "data/rasters",
    "data/vectors",
    "data/tables",
    "data/figures",
    "outputs/reports",
    "outputs/predictions",
    "scripts/preprocessing",
    "scripts/analysis",
    "scripts/watershed",
    "scripts/ml",
    "scripts/utilities",
    "scripts/qgis",
    "docs/archive",
]

for dir_path in new_dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"  ✓ Created: {dir_path}")

# Move rasters
print("\n[2/8] Consolidating raster files...")
raster_moves = {
    # Stage 3 rasters
    "data/processed/stage3/flow_acc_lucknow.tif": "data/rasters/flow_acc_lucknow.tif",
    "data/processed/stage3/stream_network_lucknow.tif": "data/rasters/stream_network_lucknow.tif",
    "data/processed/stage3/drainage_density_lucknow.tif": "data/rasters/drainage_density_lucknow.tif",
    "data/processed/stage3/twi_lucknow.tif": "data/rasters/twi_lucknow.tif",
    "data/processed/stage3/aspect_lucknow.tif": "data/rasters/aspect_lucknow.tif",
    "data/processed/stage3/plan_curvature_lucknow.tif": "data/rasters/plan_curvature_lucknow.tif",
    "data/processed/stage3/profile_curvature_lucknow.tif": "data/rasters/profile_curvature_lucknow.tif",
    "data/processed/stage3/tpi_lucknow.tif": "data/rasters/tpi_lucknow.tif",
    "data/processed/stage3/distance_to_stream_lucknow.tif": "data/rasters/distance_to_stream_lucknow.tif",
    "data/processed/stage3/ndvi_mean_lucknow.tif": "data/rasters/ndvi_lucknow.tif",
    "data/processed/stage3/features_stack.tif": "data/rasters/features_stack.tif",
    "data/processed/stage3/features_stack_bands.csv": "data/rasters/features_stack_bands.csv",
    
    # Root rasters
    "data/processed/dem_lucknow.tif": "data/rasters/dem_lucknow.tif",
    "data/processed/slope_lucknow.tif": "data/rasters/slope_lucknow.tif",
    "data/processed/hillshade_lucknow.tif": "data/rasters/hillshade_lucknow.tif",
    "data/processed/lulc_lucknow.tif": "data/rasters/lulc_lucknow.tif",
    "data/processed/rain_mean_lucknow.tif": "data/rasters/rainfall_lucknow.tif",
    "data/processed/grp_score_lucknow.tif": "data/rasters/gwp_ahp_lucknow.tif",
    "data/processed/grp_class_lucknow.tif": "data/rasters/gwp_ahp_class_lucknow.tif",
}

for src, dst in raster_moves.items():
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  ✓ Copied: {os.path.basename(dst)}")

# Copy auxiliary files
for aux_file in Path("data/processed").glob("*.tif.aux.xml"):
    dst = Path("data/rasters") / aux_file.name
    shutil.copy2(aux_file, dst)

# Move ML predictions
pred_src = Path("data/processed/predicted_grp_score.tif")
if pred_src.exists():
    for item in pred_src.iterdir():
        shutil.copy2(item, f"outputs/predictions/{item.name}")
    print("  ✓ Moved ML predictions")

# Move vectors
print("\n[3/8] Consolidating vector files...")
vector_files = [
    ("data/processed/stage4/watersheds_grid", "data/vectors/watersheds_grid"),
    ("data/processed/stage4/watersheds_characterized", "data/vectors/watersheds_characterized"),
    ("data/processed/stage4/watersheds_prioritized", "data/vectors/watersheds_prioritized"),
]

for src_base, dst_base in vector_files:
    # Copy all shapefile components (.shp, .dbf, .shx, .prj, etc.)
    src_dir = Path(src_base).parent
    src_name = Path(src_base).name
    
    for ext in ['.shp', '.dbf', '.shx', '.prj', '.cpg', '.qmd']:
        src_file = src_dir / f"{src_name}{ext}"
        if src_file.exists():
            dst_file = Path(f"{dst_base}{ext}")
            shutil.copy2(src_file, dst_file)
    
    if Path(f"{dst_base}.shp").exists():
        print(f"  ✓ Copied: {Path(dst_base).name}.shp")

# Move tables
print("\n[4/8] Consolidating table files...")
table_moves = {
    "data/processed/stage4/watersheds_characterized.csv": "data/tables/watersheds_characterized.csv",
    "data/processed/stage4/watersheds_prioritized.csv": "data/tables/watersheds_prioritized.csv",
    "data/processed/stage4/train_samples.csv": "data/tables/train_samples.csv",
    "data/processed/stage4/feature_importances.csv": "data/tables/feature_importances.csv",
    "data/processed/stage4/cv_results.csv": "data/tables/cv_results.csv",
}

for src, dst in table_moves.items():
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  ✓ Copied: {os.path.basename(dst)}")

# Move reports
print("\n[5/8] Moving reports...")
report_moves = {
    "data/processed/stage4/Executive_Summary.pdf": "outputs/reports/Executive_Summary.pdf",
    "data/processed/stage4/Watershed_Action_Plans.xlsx": "outputs/reports/Watershed_Action_Plans.xlsx",
    "data/processed/stage4/priority_summary.txt": "outputs/reports/priority_summary.txt",
}

for src, dst in report_moves.items():
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  ✓ Moved: {os.path.basename(dst)}")

# Move figures
print("\n[6/8] Moving figures...")
figs_src = Path("data/processed/figs")
if figs_src.exists():
    for fig in figs_src.iterdir():
        shutil.copy2(fig, f"data/figures/{fig.name}")
    print(f"  ✓ Moved {len(list(figs_src.iterdir()))} figures")

# Organize scripts
print("\n[7/8] Organizing Python scripts...")

script_moves = {
    # Preprocessing
    "src/preprocess.py": "scripts/preprocessing/01_process_dem.py",
    "fix_slope_calculation.py": "scripts/preprocessing/02_calculate_slope.py",
    "src/derive_drainage.py": "scripts/preprocessing/03_calculate_drainage.py",
    "src/features_stack.py": "scripts/preprocessing/04_create_feature_stack.py",
    
    # Analysis
    "src/ahp.py": "scripts/analysis/ahp_basic.py",
    "src/ahp_with_rain.py": "scripts/analysis/ahp_with_rainfall.py",
    "src/ahp_with_lulc.py": "scripts/analysis/ahp_with_lulc.py",
    
    # Watershed
    "src/delineate_watersheds.py": "scripts/watershed/delineate_watersheds.py",
    "src/characterize_watersheds.py": "scripts/watershed/characterize_watersheds.py",
    "src/prioritize_watersheds.py": "scripts/watershed/prioritize_watersheds.py",
    "src/generate_watershed_reports.py": "scripts/watershed/generate_reports.py",
    
    # ML
    "src/sample_wells.py": "scripts/ml/prepare_samples.py",
    "src/train_model.py": "scripts/ml/train_model.py",
    "src/predict_map.py": "scripts/ml/predict_map.py",
    
    # QGIS
    "qgis_characterize_watersheds.py": "scripts/qgis/characterize_watersheds.py",
    
    # Utilities
    "extract_dbf_to_csv.py": "scripts/utilities/extract_dbf_to_csv.py",
    "clean_qgis_output.py": "scripts/utilities/clean_qgis_output.py",
    "verify_qgis_output.py": "scripts/utilities/verify_qgis_output.py",
    "diagnose_slope.py": "scripts/utilities/diagnose_slope.py",
}

for src, dst in script_moves.items():
    if os.path.exists(src):
        shutil.copy2(src, dst)

print(f"  ✓ Organized {len(script_moves)} Python scripts")

# Move documentation
print("\n[8/8] Organizing documentation...")
md_files = [f for f in os.listdir(".") if f.endswith(".md") and f != "README.md"]
for md in md_files:
    shutil.copy2(md, f"docs/archive/{md}")
print(f"  ✓ Moved {len(md_files)} markdown files to docs/archive/")

# Summary
print("\n" + "="*60)
print("✅ REORGANIZATION COMPLETE!")
print("="*60 + "\n")

print("New Structure Created:")
print("  data/rasters/      - All raster files")
print("  data/vectors/      - Shapefiles")
print("  data/tables/       - CSV files")
print("  data/figures/      - Visualizations")
print("  outputs/reports/   - PDF & Excel reports")
print("  outputs/predictions/ - ML predictions")
print("  scripts/          - Organized Python scripts")
print("  docs/archive/     - Documentation")

print("\n📌 Next Steps:")
print("  1. Review new structure")
print("  2. Update import paths in code (use path_config.py)")
print("  3. Test Streamlit dashboard")
print("  4. Clean up old stage folders (optional)")

print("\n⚠️  Note: Original files preserved for safety")
print("  After testing, you can delete:")
print("  - data/processed/stage3/")
print("  - data/processed/stage4/")
print("  - Root directory Python scripts")
print()
