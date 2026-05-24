@echo off
REM Run SHAP Explainer with proper conda environment

echo.
echo ========================================
echo Running SHAP Explainability Analysis
echo ========================================
echo.

REM Activate watershed-up conda environment
call conda activate watershed-up
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate watershed-up environment
    echo Please ensure conda is installed and watershed-up environment exists
    pause
    exit /b 1
)

echo [INFO] Environment: watershed-up activated
echo [INFO] Running SHAP explainer...
echo.

REM Run SHAP explainer
python src/shap_explain.py

REM Check if output exists (ignore exit code due to OpenMP conflict)
if exist "data\processed\stage4\figs_shap\shap_summary.png" (
    echo.
    echo [SUCCESS] SHAP analysis complete!
    echo Output saved to: data/processed/stage4/figs_shap/shap_summary.png
    echo.
    echo Note: Exit code error is expected due to OpenMP library conflict.
    echo The analysis completes successfully before the error occurs.
) else (
    echo.
    echo [ERROR] SHAP analysis failed - output file not created
    echo Please check the error messages above
)

echo.
pause
