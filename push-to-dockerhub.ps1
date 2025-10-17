# Docker Hub Deployment Script
# Username: algsoch
# Repository: youtube-extractor

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Docker Hub Deployment Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if logged in
Write-Host "Step 1: Checking Docker Hub login status..." -ForegroundColor Yellow
docker info | Select-String -Pattern "Username"

$loginCheck = docker info 2>&1 | Select-String -Pattern "Username"
if (-not $loginCheck) {
    Write-Host "Not logged in to Docker Hub. Please run: docker login" -ForegroundColor Red
    Write-Host "Username: algsoch" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Docker Hub login verified" -ForegroundColor Green
Write-Host ""

# Step 2: Tag the image
Write-Host "Step 2: Tagging images..." -ForegroundColor Yellow

$localImage = "youtube-api-data-extraction-youtube-analyzer"
$dockerhubRepo = "algsoch/youtube-extractor"

# Tag as latest
Write-Host "Tagging as latest..." -ForegroundColor Gray
docker tag $localImage "$dockerhubRepo:latest"

# Tag as v1.0
Write-Host "Tagging as v1.0..." -ForegroundColor Gray
docker tag $localImage "$dockerhubRepo:v1.0"

Write-Host "✓ Images tagged successfully" -ForegroundColor Green
Write-Host ""

# Step 3: List tagged images
Write-Host "Step 3: Verifying tagged images..." -ForegroundColor Yellow
docker images | Select-String -Pattern "algsoch"
Write-Host ""

# Step 4: Push to Docker Hub
Write-Host "Step 4: Pushing to Docker Hub..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes depending on your internet speed..." -ForegroundColor Gray
Write-Host ""

Write-Host "Pushing latest tag..." -ForegroundColor Gray
docker push "$dockerhubRepo:latest"

Write-Host ""
Write-Host "Pushing v1.0 tag..." -ForegroundColor Gray
docker push "$dockerhubRepo:v1.0"

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "✓ Deployment Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your image is now available at:" -ForegroundColor Cyan
Write-Host "https://hub.docker.com/r/algsoch/youtube-extractor" -ForegroundColor Cyan
Write-Host ""
Write-Host "Anyone can now pull your image with:" -ForegroundColor Yellow
Write-Host "docker pull algsoch/youtube-extractor:latest" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to https://hub.docker.com/r/algsoch/youtube-extractor" -ForegroundColor White
Write-Host "2. Add a description and documentation" -ForegroundColor White
Write-Host "3. Test pulling from Docker Hub: docker pull algsoch/youtube-extractor:latest" -ForegroundColor White
Write-Host ""
