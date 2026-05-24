@echo off
REM ============================================
REM Watershed Groundwater Potential Model
REM Complete End-to-End Pipeline Runner
REM ============================================

echo.
echo ========================================
echo WATERSHED GROUNDWATER POTENTIAL MODEL
echo Complete Pipeline Execution
echo ========================================
echo.

REM Activate Python venv environment
echo [1/9] Activating Python environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate .venv environment
    echo Please run: py -3.11 -m venv .venv
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [2/9] Processing DEM (slope ^& hillshade)...
python scripts\preprocessing\01_process_dem.py
if errorlevel 1 (
    echo ERROR: DEM processing failed
    pause
    exit /b 1
)

echo [3/9] Creating feature stack (14 bands)...
python scripts\preprocessing\04_create_feature_stack.py
if errorlevel 1 (
    echo ERROR: Feature stack creation failed
    pause
    exit /b 1
)

echo [4/9] Generating training samples...
python scripts\ml\01_prepare_samples.py --stack data\rasters\features_stack.tif --n 5000
if errorlevel 1 (
    echo ERROR: Sample generation failed
    pause
    exit /b 1
)

echo [5/9] Validating samples...
python scripts\ml\02_check_samples.py
if errorlevel 1 (
    echo ERROR: Sample validation failed
    pause
    exit /b 1
)

echo [6/9] Training Random Forest model...
python scripts\ml\03_train_model.py --in data\tables\train_samples.csv
if errorlevel 1 (
    echo ERROR: Model training failed
    pause
    exit /b 1
)

echo [7/9] Generating predictions...
python scripts\ml\04_predict_map.py --stack data\rasters\features_stack.tif --model models\rf_baseline.pkl
if errorlevel 1 (
    echo ERROR: Prediction generation failed
    pause
    exit /b 1
)

echo [8/9] Analyzing model performance...
python scripts\ml\06_analyze_enhanced_model.py
if errorlevel 1 (
    echo ERROR: Model analysis failed
    pause
    exit /b 1
)

echo [9/9] Printing summary...
python scripts\ml\08_print_ml_summary.py
if errorlevel 1 (
    echo ERROR: Summary generation failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo PIPELINE COMPLETE!
echo ========================================
echo.
echo Output Files:
echo   Feature Stack: data\rasters\features_stack.tif (14 bands)
echo   Model:         models\rf_baseline.pkl
echo   Samples:       data\tables\train_samples.csv (5,000)
echo   CV Results:    data\tables\cv_results.csv
echo   Importances:   data\tables\feature_importances.csv
echo   Predictions:   data\rasters\predicted_grp_*.tif
echo   Figures:       data\figures\*.png
echo.
echo Model Performance:
echo   Accuracy:          44.4%%
echo   Balanced Accuracy: 40.0%%
echo   Top Features:      LULC (15.8%%), Rain (13.3%%), Drainage (10.7%%)
echo.
echo Next Steps:
echo   1. Launch dashboard:  streamlit run app\main.py
echo   2. View figures:      data\figures\
echo   3. Check importances: data\tables\feature_importances.csv
echo.
pause
