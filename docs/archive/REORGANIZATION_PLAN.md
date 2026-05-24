# Project Reorganization Plan

## Current Issues
1. Scattered Python scripts (60+ files in root)
2. Stage-based folders (stage3, stage4, stage5) - confusing
3. Multiple output locations
4. Unclear file purposes

## New Structure

```
watershed-up/
├── README.md
├── requirements.txt
├── environment.yml
│
├── config/                      # Configuration files
│   └── config.yml
│
├── data/
│   ├── raw/                     # Original datasets (unchanged)
│   ├── rasters/                 # All processed rasters
│   │   ├── dem_lucknow.tif
│   │   ├── slope_lucknow.tif
│   │   ├── lulc_lucknow.tif
│   │   ├── rainfall_lucknow.tif
│   │   ├── ndvi_lucknow.tif
│   │   ├── flow_acc_lucknow.tif
│   │   ├── drainage_density_lucknow.tif
│   │   ├── stream_network_lucknow.tif
│   │   ├── twi_lucknow.tif
│   │   ├── aspect_lucknow.tif
│   │   ├── features_stack.tif
│   │   └── gwp_score_lucknow.tif
│   │
│   ├── vectors/                 # Shapefiles & vector data
│   │   ├── watersheds_grid.shp
│   │   ├── watersheds_characterized.shp
│   │   └── watersheds_prioritized.shp
│   │
│   ├── tables/                  # CSV files
│   │   ├── watersheds_characterized.csv
│   │   ├── watersheds_prioritized.csv
│   │   ├── train_samples.csv
│   │   └── feature_importances.csv
│   │
│   └── figures/                 # Output visualizations
│
├── models/                      # Trained ML models
│   └── rf_baseline.pkl
│
├── outputs/                     # Final reports & deliverables
│   ├── reports/
│   │   ├── Executive_Summary.pdf
│   │   └── Watershed_Action_Plans.xlsx
│   └── predictions/
│       ├── gwp_predictions.tif
│       └── gwp_class.tif
│
├── scripts/                     # All Python scripts organized by function
│   ├── preprocessing/
│   │   ├── 01_process_dem.py
│   │   ├── 02_calculate_slope.py
│   │   ├── 03_calculate_drainage.py
│   │   └── 04_create_feature_stack.py
│   │
│   ├── analysis/
│   │   ├── ahp_analysis.py
│   │   └── spatial_statistics.py
│   │
│   ├── watershed/
│   │   ├── delineate_watersheds.py
│   │   ├── characterize_watersheds.py
│   │   ├── prioritize_watersheds.py
│   │   └── generate_reports.py
│   │
│   ├── ml/
│   │   ├── prepare_samples.py
│   │   ├── train_model.py
│   │   ├── predict_map.py
│   │   └── evaluate_model.py
│   │
│   └── utilities/
│       ├── fix_slope_calculation.py
│       ├── extract_dbf_to_csv.py
│       └── quality_checks.py
│
├── app/                         # Streamlit dashboard
│   ├── main.py
│   └── pages/
│
├── docs/                        # Documentation
│   ├── methodology/
│   ├── results/
│   └── guides/
│
├── tests/                       # Unit tests
│
└── notebooks/                   # Jupyter notebooks for exploration

```

## Migration Steps

1. Create new folder structure
2. Move rasters from stage3/stage4 to `data/rasters/`
3. Move vectors to `data/vectors/`
4. Move CSV files to `data/tables/`
5. Organize Python scripts into `scripts/` subfolders
6. Move reports to `outputs/reports/`
7. Update all import paths in code
8. Clean up root directory

## Files to Archive (not delete)
- All markdown documentation files → `docs/archive/`
- Backup files → `backups/`
- Test scripts → keep only active ones

## Benefits
✅ Clear separation by data type (rasters/vectors/tables)
✅ Logical script organization by function
✅ Easy to find files
✅ No confusing stage numbers
✅ Clean root directory
✅ Professional structure
