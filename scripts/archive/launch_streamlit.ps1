# Launch Streamlit Platform with UTF-8 encoding support
# Fixes emoji/Unicode character display issues on Windows

Write-Host ""
Write-Host "========================================"
Write-Host "Launching GRPZ Streamlit Platform"
Write-Host "========================================"
Write-Host ""
Write-Host "Platform will open at: http://localhost:8501"
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

# Activate conda environment
conda activate watershed-up
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to activate watershed-up environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Set UTF-8 encoding for Python I/O
$env:PYTHONIOENCODING = "utf-8"

# Launch Streamlit
streamlit run app\main.py
