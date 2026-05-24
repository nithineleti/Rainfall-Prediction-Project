"""
Centralized Path Configuration
All paths for data, outputs, and models
"""
from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"

# Data subdirectories
RASTERS_DIR = DATA_DIR / "rasters"
VECTORS_DIR = DATA_DIR / "vectors"
TABLES_DIR = DATA_DIR / "tables"
FIGURES_DIR = DATA_DIR / "figures"
RAW_DIR = DATA_DIR / "raw"

# Output subdirectories
REPORTS_DIR = OUTPUTS_DIR / "reports"
PREDICTIONS_DIR = OUTPUTS_DIR / "predictions"

# Input rasters (data/rasters/)
DEM = RASTERS_DIR / "dem_lucknow.tif"
SLOPE = RASTERS_DIR / "slope_lucknow.tif"
HILLSHADE = RASTERS_DIR / "hillshade_lucknow.tif"
LULC = RASTERS_DIR / "lulc_lucknow.tif"
RAINFALL = RASTERS_DIR / "rainfall_lucknow.tif"
NDVI = RASTERS_DIR / "ndvi_lucknow.tif"

# Derived rasters (data/rasters/)
FLOW_ACC = RASTERS_DIR / "flow_acc_lucknow.tif"
STREAM_NETWORK = RASTERS_DIR / "stream_network_lucknow.tif"
DRAINAGE_DENSITY = RASTERS_DIR / "drainage_density_lucknow.tif"
TWI = RASTERS_DIR / "twi_lucknow.tif"
ASPECT = RASTERS_DIR / "aspect_lucknow.tif"
PLAN_CURVATURE = RASTERS_DIR / "plan_curvature_lucknow.tif"
PROFILE_CURVATURE = RASTERS_DIR / "profile_curvature_lucknow.tif"
TPI = RASTERS_DIR / "tpi_lucknow.tif"
DIST_TO_STREAM = RASTERS_DIR / "distance_to_stream_lucknow.tif"

# Feature stack
FEATURES_STACK = RASTERS_DIR / "features_stack.tif"
FEATURES_BANDS_CSV = RASTERS_DIR / "features_stack_bands.csv"

# GWP from AHP
GWP_AHP = RASTERS_DIR / "gwp_ahp_lucknow.tif"
GWP_AHP_CLASS = RASTERS_DIR / "gwp_ahp_class_lucknow.tif"

# Vectors (data/vectors/)
WATERSHEDS_GRID = VECTORS_DIR / "watersheds_grid.shp"
WATERSHEDS_CHARACTERIZED = VECTORS_DIR / "watersheds_characterized.shp"
WATERSHEDS_PRIORITIZED = VECTORS_DIR / "watersheds_prioritized.shp"

# Tables (data/tables/)
WATERSHEDS_CSV = TABLES_DIR / "watersheds_characterized.csv"
WATERSHEDS_PRIORITY_CSV = TABLES_DIR / "watersheds_prioritized.csv"
TRAIN_SAMPLES_CSV = TABLES_DIR / "train_samples.csv"
FEATURE_IMPORTANCE_CSV = TABLES_DIR / "feature_importances.csv"
CV_RESULTS_CSV = TABLES_DIR / "cv_results.csv"

# Raw data subdirectories
RAW_CHIRPS_DIR = RAW_DIR / "lucknow_chirps"
RAW_DEM_DIR = RAW_DIR / "lucknow_dem_12.5"
RAW_GEOLOGY_DIR = RAW_DIR / "lucknow_geology"
RAW_LULC_DIR = RAW_DIR / "lucknow_lulc"
RAW_NDVI_DIR = RAW_DIR / "lucknow_ndvi"
RAW_SHP_DIR = RAW_DIR / "lucknow_shp"
RAW_SOIL_DIR = RAW_DIR / "lucknow_soil"
RAW_WELLS_DIR = RAW_DIR / "lucknow_wells"

# Raw input files
RAW_RAINFALL = RAW_CHIRPS_DIR / "chirps_map_2010_2020_mean_lucknow.tif"
RAW_DEM = RAW_DEM_DIR / "dem_lucknow_12.5.tif"
RAW_LULC = RAW_LULC_DIR / "lulc_worldcover_2021.tif"
RAW_NDVI = RAW_NDVI_DIR / "ndvi_mean_lucknow.tif"
RAW_DISTRICT_SHP = RAW_SHP_DIR / "lucknow.shp"
RAW_GEOLOGY_SHP = RAW_GEOLOGY_DIR / "geology_lucknow.shp"

# Soil data
RAW_SOIL_CLAY = RAW_SOIL_DIR / "soil_clay_lucknow.tif"
RAW_SOIL_SAND = RAW_SOIL_DIR / "soil_sand_lucknow.tif"
RAW_SOIL_SILT = RAW_SOIL_DIR / "soil_silt_lucknow.tif"

# Well data
RAW_WELLS_WDC = RAW_WELLS_DIR / "lucknow_Water_Level_WDC.csv"
RAW_WELLS_CGWB = RAW_WELLS_DIR / "wells_cgwb.csv"
RAW_WELLS_CGWB_INFERRED = RAW_WELLS_DIR / "wells_cgwb_inferred.csv"
WELLS_CSV = RAW_WELLS_WDC  # Default well data file

# Reports (outputs/reports/)
EXECUTIVE_SUMMARY_PDF = REPORTS_DIR / "Executive_Summary.pdf"
ACTION_PLANS_XLSX = REPORTS_DIR / "Watershed_Action_Plans.xlsx"
PRIORITY_SUMMARY_TXT = REPORTS_DIR / "priority_summary.txt"

# ML Predictions (outputs/predictions/)
ML_PREDICTION = PREDICTIONS_DIR / "predicted_grp_score.tif"
ML_PREDICTION_CLASS = PREDICTIONS_DIR / "predicted_class.tif"

# Models
RF_MODEL = MODELS_DIR / "rf_baseline.pkl"

# Script paths (for imports)
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
PREPROCESSING_DIR = SCRIPTS_DIR / "preprocessing"
ANALYSIS_DIR = SCRIPTS_DIR / "analysis"
WATERSHED_DIR = SCRIPTS_DIR / "watershed"
ML_DIR = SCRIPTS_DIR / "ml"
UTILITIES_DIR = SCRIPTS_DIR / "utilities"
QGIS_DIR = SCRIPTS_DIR / "qgis"
VISUALIZATION_DIR = SCRIPTS_DIR / "visualization"

# Ensure directories exist
def ensure_dirs():
    """Create all necessary directories"""
    dirs = [
        RASTERS_DIR, VECTORS_DIR, TABLES_DIR, FIGURES_DIR,
        REPORTS_DIR, PREDICTIONS_DIR, MODELS_DIR
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    print("Path Configuration:")
    print(f"  Project Root: {PROJECT_ROOT}")
    print(f"  Data Dir: {DATA_DIR}")
    print(f"  Outputs Dir: {OUTPUTS_DIR}")
    print(f"  Models Dir: {MODELS_DIR}")
    print(f"\nAll paths configured successfully!")
