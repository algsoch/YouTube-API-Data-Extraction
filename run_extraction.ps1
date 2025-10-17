# YouTube Data Extraction Runner
# Simple PowerShell script to run the extraction with error handling

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "YouTube Classical Music Data Extraction" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please run: copy .env.example .env" -ForegroundColor Yellow
    Write-Host "Then edit .env and add your YouTube API key" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
}

# Run validation
Write-Host "Running pre-flight checks..." -ForegroundColor Green
python validate_setup.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Pre-flight checks failed. Please fix the issues above." -ForegroundColor Red
    exit 1
}

# Run main extraction
Write-Host ""
Write-Host "Starting data extraction..." -ForegroundColor Green
Write-Host "Press Ctrl+C at any time to stop (progress will be saved)" -ForegroundColor Yellow
Write-Host ""

python main.py

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "Extraction completed successfully!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Check the 'data' folder for your CSV files." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Extraction stopped. Check youtube_extraction.log for details." -ForegroundColor Yellow
    Write-Host "Run this script again to resume from where you left off." -ForegroundColor Yellow
}
