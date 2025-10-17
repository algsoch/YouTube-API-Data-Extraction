# Docker Hub Deployment Guide

This guide will help you push your YouTube Data Extractor application to Docker Hub for easy distribution and deployment.

## Prerequisites

1. **Docker Hub Account**: Create a free account at https://hub.docker.com/
2. **Docker Installed**: Verify with `docker --version`
3. **Application Built**: Ensure your Docker image is built

## Step 1: Login to Docker Hub

Open PowerShell and login to Docker Hub:

```powershell
docker login
```

You'll be prompted for:
- **Username**: Your Docker Hub username
- **Password**: Your Docker Hub password or Personal Access Token (PAT)

**Alternative**: Use Personal Access Token (more secure)
```powershell
docker login -u YOUR_USERNAME
# Then paste your PAT when prompted for password
```

## Step 2: Tag Your Image

Tag your local image with your Docker Hub username:

```powershell
# Format: docker tag LOCAL_IMAGE DOCKERHUB_USERNAME/REPOSITORY_NAME:TAG
docker tag youtube-api-data-extraction-youtube-analyzer YOUR_USERNAME/youtube-extractor:latest
docker tag youtube-api-data-extraction-youtube-analyzer YOUR_USERNAME/youtube-extractor:v1.0
```

**Example** (replace `YOUR_USERNAME` with your actual Docker Hub username):
```powershell
docker tag youtube-api-data-extraction-youtube-analyzer algsoch/youtube-extractor:latest
docker tag youtube-api-data-extraction-youtube-analyzer algsoch/youtube-extractor:v1.0
```

## Step 3: Push to Docker Hub

Push your tagged images:

```powershell
docker push YOUR_USERNAME/youtube-extractor:latest
docker push YOUR_USERNAME/youtube-extractor:v1.0
```

**Example**:
```powershell
docker push algsoch/youtube-extractor:latest
docker push algsoch/youtube-extractor:v1.0
```

This may take 5-10 minutes depending on your internet speed (image is ~500MB).

## Step 4: Verify on Docker Hub

1. Go to https://hub.docker.com/
2. Login to your account
3. Navigate to "Repositories"
4. You should see `youtube-extractor` with tags `latest` and `v1.0`

## Step 5: Update Repository Description

On Docker Hub, add a description for your repository:

```markdown
# YouTube Classical Music Data Extractor

Professional tool for extracting YouTube video and channel data using the YouTube Data API v3.

## Features
- 🎵 Automated data extraction for classical music content
- 📊 6-tab analytics dashboard with visualizations
- 🔍 Custom search query builder
- 📁 CSV export functionality
- 🔄 Real-time extraction progress tracking
- ⚠️ Quota management with countdown timers
- 📱 Fully responsive design

## Quick Start

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e YOUTUBE_API_KEY=your_api_key_here \
  YOUR_USERNAME/youtube-extractor:latest
```

Then open http://localhost:8000 in your browser.

## Documentation
Full documentation available in the GitHub repository.
```

## Deployment Options

### Option 1: Deploy from Docker Hub

Anyone can now deploy your application:

```powershell
# Pull the image
docker pull YOUR_USERNAME/youtube-extractor:latest

# Run the container
docker run -d `
  -p 8000:8000 `
  -v ${PWD}/data:/app/data `
  -e YOUTUBE_API_KEY=your_api_key_here `
  --name youtube-analyzer `
  YOUR_USERNAME/youtube-extractor:latest
```

### Option 2: Use Docker Compose (Recommended)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  youtube-analyzer:
    image: YOUR_USERNAME/youtube-extractor:latest
    container_name: youtube-analyzer
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
    restart: unless-stopped
```

Then run:
```powershell
docker-compose up -d
```

### Option 3: Cloud Deployment

#### Deploy to AWS ECS
```bash
# Coming soon - AWS ECS deployment guide
```

#### Deploy to Google Cloud Run
```bash
# Coming soon - Google Cloud Run deployment guide
```

#### Deploy to Azure Container Instances
```bash
# Coming soon - Azure deployment guide
```

## Updating Your Image

When you make changes to your application:

1. **Rebuild the image**:
   ```powershell
   docker-compose build
   ```

2. **Tag with new version**:
   ```powershell
   docker tag youtube-api-data-extraction-youtube-analyzer YOUR_USERNAME/youtube-extractor:v1.1
   ```

3. **Push new version**:
   ```powershell
   docker push YOUR_USERNAME/youtube-extractor:v1.1
   docker push YOUR_USERNAME/youtube-extractor:latest
   ```

## Security Best Practices

### 1. Use Personal Access Tokens (PAT)

Instead of your Docker Hub password, create a PAT:
- Go to Docker Hub → Account Settings → Security
- Click "New Access Token"
- Copy the token and use it for `docker login`

### 2. Never Commit API Keys

Ensure your `.env` file is in `.gitignore`:
```
.env
*.env
.env.local
```

### 3. Use Docker Secrets (Production)

For production deployments, use Docker secrets:
```powershell
# Create secret
echo "your_api_key" | docker secret create youtube_api_key -

# Use in docker-compose.yml
secrets:
  youtube_api_key:
    external: true
```

## Troubleshooting

### Issue: "denied: requested access to the resource is denied"

**Solution**: Make sure you're logged in and using the correct username:
```powershell
docker login
docker push YOUR_USERNAME/youtube-extractor:latest
```

### Issue: "no basic auth credentials"

**Solution**: Login again with correct credentials:
```powershell
docker logout
docker login -u YOUR_USERNAME
```

### Issue: Upload is slow

**Solution**: The first push is slow (~5-10 min). Subsequent pushes are faster (only changed layers).

### Issue: Image too large

**Current size**: ~500MB (reasonable for Python app with dependencies)

To reduce size:
- Use multi-stage builds (already implemented)
- Use `.dockerignore` (already implemented)
- Remove unused dependencies

## Image Information

**Base Image**: `python:3.11-slim`
**Size**: ~500MB compressed
**Architecture**: linux/amd64
**Ports**: 8000
**Volumes**: `/app/data`
**Environment Variables**: `YOUTUBE_API_KEY`

## Automated Builds (Optional)

Set up GitHub Actions to automatically build and push on every commit:

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            YOUR_USERNAME/youtube-extractor:latest
            YOUR_USERNAME/youtube-extractor:${{ github.sha }}
```

## Client Demo Commands

For your client demo, show these professional commands:

```powershell
# Pull from Docker Hub (shows it's published)
docker pull YOUR_USERNAME/youtube-extractor:latest

# Run with one command
docker run -d -p 8000:8000 `
  -v ${PWD}/data:/app/data `
  -e YOUTUBE_API_KEY=$env:YOUTUBE_API_KEY `
  YOUR_USERNAME/youtube-extractor:latest

# Check status
docker ps

# View logs
docker logs -f youtube-analyzer

# Open in browser
Start-Process "http://localhost:8000"
```

## Support and Documentation

- **GitHub Repository**: https://github.com/algsoch/YouTube-API-Data-Extraction
- **Docker Hub**: https://hub.docker.com/r/YOUR_USERNAME/youtube-extractor
- **Issues**: Report issues on GitHub

## Version History

- **v1.0** (October 2025)
  - Initial release
  - Fixed quota exceeded visibility bug
  - Fixed analytics NaN JSON serialization errors
  - Improved responsive navbar
  - Added comprehensive documentation
  - Docker Hub deployment ready

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker login` | Login to Docker Hub |
| `docker tag SOURCE TARGET` | Tag an image |
| `docker push IMAGE:TAG` | Push image to Docker Hub |
| `docker pull IMAGE:TAG` | Pull image from Docker Hub |
| `docker images` | List local images |
| `docker rmi IMAGE` | Remove local image |
| `docker logout` | Logout from Docker Hub |

---

**Ready for Client Demo!** 🚀

Your application is now:
✅ Containerized with Docker
✅ Published to Docker Hub
✅ Deployable anywhere in seconds
✅ Professional and production-ready
