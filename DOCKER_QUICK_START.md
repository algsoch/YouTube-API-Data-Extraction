# 🐳 Docker Deployment - Quick Start Guide

**Application**: YouTube Classical Music Data Extraction
**Status**: ✅ Ready to Deploy

---

## 📋 Prerequisites

Make sure you have installed:

- ✅ Docker Desktop for Windows ([Download](https://www.docker.com/products/docker-desktop))
- ✅ Docker Compose (included with Docker Desktop)

### Check Installation

```powershell
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Verify Docker is running
docker ps
```

---

## 🚀 Quick Deployment (3 Steps)

### Step 1: Build the Docker Image

```powershell
# Navigate to your project directory
cd C:\Users\npdim\OneDrive\Documents\MEGA\yt\YouTube-API-Data-Extraction

# Build the Docker image
docker-compose build
```

**Expected output:**

```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition
 => => transferring dockerfile
 => [internal] load .dockerignore
 => [1/6] FROM docker.io/library/python:3.11-slim
 => [2/6] WORKDIR /app
 => [3/6] COPY requirements_api.txt .
 => [4/6] RUN pip install --upgrade pip
 => [5/6] COPY . .
 => [6/6] RUN mkdir -p /app/data
 => exporting to image
 => => naming to docker.io/library/youtube-analyzer
```

---

### Step 2: Start the Application

```powershell
# Start the application in background (-d = detached mode)
docker-compose up -d
```

**Expected output:**

```
[+] Running 2/2
 ✔ Network youtube-analyzer-network  Created    0.1s
 ✔ Container youtube-analyzer         Started    0.5s
```

---

### Step 3: Verify Deployment

```powershell
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs
```

**Access your application:**

- 🌐 Web Interface: http://localhost:8000
- 📊 API Documentation: http://localhost:8000/docs

---

## 📊 Container Management Commands

### View Running Containers

```powershell
docker-compose ps
```

### View Logs (Real-time)

```powershell
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Stop the Application

```powershell
docker-compose stop
```

### Start the Application (Already Built)

```powershell
docker-compose start
```

### Restart the Application

```powershell
docker-compose restart
```

### Stop and Remove Containers

```powershell
docker-compose down
```

### Rebuild and Restart

```powershell
# When you make code changes
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 🔍 Troubleshooting

### Check Container Status

```powershell
docker-compose ps
```

**Expected output:**

```
NAME                  IMAGE               STATUS        PORTS
youtube-analyzer      youtube-analyzer    Up 2 minutes  0.0.0.0:8000->8000/tcp
```

### View Application Logs

```powershell
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50
```

### Access Container Shell

```powershell
docker-compose exec youtube-analyzer bash
```

Inside container:

```bash
# Check Python version
python --version

# List files
ls -la

# Check data directory
ls -la /app/data

# Exit container
exit
```

### Check Container Health

```powershell
docker inspect youtube-analyzer --format='{{.State.Health.Status}}'
```

**Expected:** `healthy`

---

## 📁 Data Persistence

Your data is persisted on your Windows machine:

**Location:** `C:\Users\npdim\OneDrive\Documents\MEGA\yt\YouTube-API-Data-Extraction\data`

**Mounted to container:** `/app/data`

**What's persisted:**

- ✅ All CSV files (videos, channels)
- ✅ Extraction summaries
- ✅ Progress files

**Even if you stop/remove the container, your data is safe!**

---

## 🔑 Environment Variables

Your `.env` file is automatically loaded:

```properties
YOUTUBE_API_KEY=Your_api_keys
```

**To update:**

1. Edit `.env` file
2. Restart container: `docker-compose restart`

---

## 🌐 Port Configuration

**Default:** Port 8000

**To change port:**

Edit `docker-compose.yml`:

```yaml
ports:
  - "9000:8000"  # Change 9000 to your desired port
```

Then restart:

```powershell
docker-compose down
docker-compose up -d
```

---

## 🚀 Advanced: Production Deployment

### Using Docker Run (Without Compose)

```powershell
# Build image
docker build -t youtube-analyzer:latest .

# Run container
docker run -d \
  --name youtube-analyzer \
  -p 8000:8000 \
  -v C:\Users\npdim\OneDrive\Documents\MEGA\yt\YouTube-API-Data-Extraction\data:/app/data \
  -e YOUTUBE_API_KEY=your_api_key_here \
  --restart unless-stopped \
  youtube-analyzer:latest
```

### Deploy to Docker Hub

```powershell
# Login to Docker Hub
docker login

# Tag your image
docker tag youtube-analyzer:latest yourusername/youtube-analyzer:latest

# Push to Docker Hub
docker push yourusername/youtube-analyzer:latest
```

### Deploy to Cloud

**See DOCKER_DEPLOYMENT.md** for detailed instructions on:

- ✅ AWS ECS / Fargate
- ✅ Azure Container Instances
- ✅ Google Cloud Run
- ✅ Heroku Container Registry

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Container is running: `docker-compose ps`
- [ ] Container is healthy: `docker inspect youtube-analyzer --format='{{.State.Health.Status}}'`
- [ ] Web interface accessible: http://localhost:8000
- [ ] Dashboard shows data: Check video/channel counts
- [ ] Analytics working: Click "Analysis" tab
- [ ] Data persists: Stop container, restart, data still there
- [ ] Logs show no errors: `docker-compose logs`

---

## 🎯 Common Issues & Solutions

### Issue: Port 8000 Already in Use

**Error:**

```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution:**

```powershell
# Stop existing server
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change Docker port in docker-compose.yml to 9000
```

### Issue: Docker Desktop Not Running

**Error:**

```
error during connect: This error may indicate that the docker daemon is not running
```

**Solution:**

1. Open Docker Desktop application
2. Wait for Docker to start
3. Retry: `docker-compose up -d`

### Issue: Container Keeps Restarting

**Check logs:**

```powershell
docker-compose logs
```

**Common causes:**

- Missing dependencies (check requirements_api.txt)
- Invalid API key (check .env file)
- Port conflict (change port in docker-compose.yml)

### Issue: Can't Access Web Interface

**Verify:**

```powershell
# Container running?
docker-compose ps

# Port mapped correctly?
docker port youtube-analyzer

# Check logs
docker-compose logs --tail=50
```

**Try:**

- http://localhost:8000
- http://127.0.0.1:8000
- Check Windows Firewall settings

---

## 🎉 Success!

If you see:

```
NAME                  STATUS        PORTS
youtube-analyzer      Up 2 minutes  0.0.0.0:8000->8000/tcp
```

And can access http://localhost:8000 → **You're successfully deployed!** 🚀

---

## 📝 Next Steps

1. ✅ Test all features in browser
2. ✅ Run a test extraction
3. ✅ Verify data persists after restart
4. ✅ Prepare for client demo
5. ✅ (Optional) Deploy to cloud platform

---

## 🆘 Need Help?

**Check logs:**

```powershell
docker-compose logs -f
```

**Restart fresh:**

```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Full cleanup (removes everything):**

```powershell
docker-compose down -v
docker system prune -a
# Then rebuild from scratch
```

---

## 🎯 For Your Client Demo

**Show Docker deployment as a bonus feature:**

> "The application is fully containerized using Docker, which means:
>
> - ✅ Consistent deployment across any environment
> - ✅ Easy to scale horizontally
> - ✅ Works on Windows, Mac, Linux, and all cloud platforms
> - ✅ One-command deployment: `docker-compose up -d`
> - ✅ Data persistence guaranteed
> - ✅ Production-ready with health checks"

**This adds professional credibility to your demo!** 🎉

---

**Ready to deploy?** Run these commands:

```powershell
cd C:\Users\npdim\OneDrive\Documents\MEGA\yt\YouTube-API-Data-Extraction
docker-compose build
docker-compose up -d
docker-compose ps
```

Then open: http://localhost:8000 🚀
