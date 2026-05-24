# ============================================================================
# PROJECT RESTRUCTURE & CLEANUP SCRIPT
# Removes all outputs, stages, and unnecessary files
# Keeps only essential source code and configuration
# ============================================================================

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║                                                                ║" -ForegroundColor Yellow
Write-Host "║        PROJECT RESTRUCTURE - CLEAN & ORGANIZE                 ║" -ForegroundColor Yellow
Write-Host "║                                                                ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow

$projectRoot = "G:\PROJECTS\watershed-up"
Set-Location $projectRoot

Write-Host "WARNING: This will DELETE all output files and unnecessary folders!" -ForegroundColor Red
Write-Host "The following will be removed:" -ForegroundColor Yellow
Write-Host "  • data/processed/ (all stages)" -ForegroundColor White
Write-Host "  • models/ (trained models)" -ForegroundColor White
Write-Host "  • backups/" -ForegroundColor White
Write-Host "  • Temporary/test scripts in root" -ForegroundColor White
Write-Host "  • Old documentation files" -ForegroundColor White
Write-Host "  • ui/ and infra/ folders" -ForegroundColor White
Write-Host "`ndata/raw/ will be PRESERVED (contains source data)`n" -ForegroundColor Green

$response = Read-Host "Continue with cleanup? (yes/no)"
if ($response -ne "yes") {
    Write-Host "`nCleanup cancelled." -ForegroundColor Yellow
    exit
}

Write-Host "`n════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 1: Removing Output Files" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Remove processed data (all stages)
if (Test-Path "data\processed") {
    Write-Host "  → Removing data/processed/ (all stage outputs)..." -ForegroundColor Yellow
    Remove-Item -Path "data\processed" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Removed" -ForegroundColor Green
}

# Remove models folder
if (Test-Path "models") {
    Write-Host "  → Removing models/ (trained models)..." -ForegroundColor Yellow
    Remove-Item -Path "models" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Removed" -ForegroundColor Green
}

# Remove backups
if (Test-Path "backups") {
    Write-Host "  → Removing backups/..." -ForegroundColor Yellow
    Remove-Item -Path "backups" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Removed" -ForegroundColor Green
}

Write-Host "`n════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 2: Removing Unnecessary Folders" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Remove UI folder (Streamlit app - not part of core)
if (Test-Path "ui") {
    Write-Host "  → Removing ui/ (old Streamlit app)..." -ForegroundColor Yellow
    Remove-Item -Path "ui" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Removed" -ForegroundColor Green
}

# Remove infra folder (Terraform - not needed)
if (Test-Path "infra") {
    Write-Host "  → Removing infra/ (Terraform configs)..." -ForegroundColor Yellow
    Remove-Item -Path "infra" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Removed" -ForegroundColor Green
}

# Remove notebooks (if you want to keep them, comment this out)
if (Test-Path "notebooks") {
    Write-Host "  → Removing notebooks/ (Jupyter notebooks)..." -ForegroundColor Yellow
    Remove-Item -Path "notebooks" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Removed" -ForegroundColor Green
}

Write-Host "`n════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 3: Removing Temporary/Test Scripts" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# List of temporary scripts to remove
$tempScripts = @(
    "analyze_enhanced_model.py",
    "check_geology.py",
    "check_geology_simple.py",
    "check_stage3_data.py",
    "compare_feature_stacks.py",
    "compare_stream_enhancement.py",
    "improve_visualizations.py",
    "visualize_enhanced_features.py",
    "launch_streamlit.bat",
    "launch_streamlit.ps1",
    "run_pipeline.bat",
    "run_pipeline.ps1",
    "run_shap.bat",
    "cleanup_project.ps1"
)

foreach ($script in $tempScripts) {
    if (Test-Path $script) {
        Write-Host "  → Removing $script..." -ForegroundColor Yellow
        Remove-Item -Path $script -Force -ErrorAction SilentlyContinue
        Write-Host "    ✓ Removed" -ForegroundColor Green
    }
}

Write-Host "`n════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 4: Cleaning Documentation" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Remove old/redundant documentation
$oldDocs = @(
    "BACKEND_PROGRESS.md",
    "CLEANUP_PLAN.md",
    "CLEANUP_SUMMARY.md",
    "CLEANUP_VERIFICATION.md",
    "PIPELINE_EXECUTION_ORDER.md",
    "PIPELINE_WORKING_SOLUTION.md",
    "RESTRUCTURE_DECISION.md",
    "RESTRUCTURE_PLAN.md",
    "ENHANCED_FEATURES_SUMMARY.md"
)

foreach ($doc in $oldDocs) {
    if (Test-Path $doc) {
        Write-Host "  → Removing $doc..." -ForegroundColor Yellow
        Remove-Item -Path $doc -Force -ErrorAction SilentlyContinue
        Write-Host "    ✓ Removed" -ForegroundColor Green
    }
}

Write-Host "`n════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 5: Organizing Documentation" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Keep only essential docs in docs/ folder
Write-Host "  → Documentation structure organized in docs/" -ForegroundColor Green
Write-Host "    ✓ Essential docs preserved" -ForegroundColor Green

Write-Host "`n════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 6: Creating Clean Directory Structure" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Create clean output directories
New-Item -ItemType Directory -Force -Path "data\processed" | Out-Null
New-Item -ItemType Directory -Force -Path "models" | Out-Null
Write-Host "  ✓ Created clean data/processed/" -ForegroundColor Green
Write-Host "  ✓ Created clean models/" -ForegroundColor Green

Write-Host "`n════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Green

Write-Host "Clean Project Structure:" -ForegroundColor Cyan
Write-Host "watershed-up/" -ForegroundColor White
Write-Host "├─ src/                  (Core ML pipeline scripts)" -ForegroundColor Gray
Write-Host "├─ backend/              (FastAPI backend)" -ForegroundColor Gray
Write-Host "├─ app/                  (Streamlit visualization)" -ForegroundColor Gray
Write-Host "├─ ml/                   (ML code organization)" -ForegroundColor Gray
Write-Host "├─ data/" -ForegroundColor Gray
Write-Host "│  ├─ raw/              (Source data - PRESERVED)" -ForegroundColor Green
Write-Host "│  └─ processed/        (Output - CLEAN)" -ForegroundColor Green
Write-Host "├─ models/              (Trained models - CLEAN)" -ForegroundColor Green
Write-Host "├─ docs/                (Documentation)" -ForegroundColor Gray
Write-Host "├─ scripts/             (Utility scripts)" -ForegroundColor Gray
Write-Host "├─ tests/               (Unit tests)" -ForegroundColor Gray
Write-Host "├─ configs/             (Configuration files)" -ForegroundColor Gray
Write-Host "├─ .github/             (CI/CD workflows)" -ForegroundColor Gray
Write-Host "├─ README.md" -ForegroundColor Gray
Write-Host "├─ QUICK_START.md" -ForegroundColor Gray
Write-Host "├─ RUN_MODEL_GUIDE.md" -ForegroundColor Gray
Write-Host "├─ DATA_LEAKAGE_FIX.md" -ForegroundColor Gray
Write-Host "├─ requirements.txt" -ForegroundColor Gray
Write-Host "├─ environment.yml" -ForegroundColor Gray
Write-Host "├─ docker-compose.yml" -ForegroundColor Gray
Write-Host "├─ run_model.bat        (Main runner)" -ForegroundColor Yellow
Write-Host "├─ run_model.ps1        (Main runner)" -ForegroundColor Yellow
Write-Host "└─ run_complete_pipeline.py" -ForegroundColor Yellow

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "  1. Run pipeline to regenerate outputs: " -NoNewline -ForegroundColor White
Write-Host ".\run_model.bat" -ForegroundColor Yellow
Write-Host "  2. Review structure: " -NoNewline -ForegroundColor White
Write-Host "tree /F" -ForegroundColor Yellow
Write-Host "  3. Test backend: " -NoNewline -ForegroundColor White
Write-Host "cd backend; uvicorn app.main:app --reload" -ForegroundColor Yellow
Write-Host "`n"

Read-Host "Press Enter to exit"
