# 🐳 Docker Deployment Guide

## Quick Start with Docker

### 1. Build the Docker Image

```bash
docker build -t youtube-analyzer:latest .
```

### 2. Run with Docker Compose (Recommended)

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

The application will be available at: **http://localhost:8000**

### 3. Or Run with Docker Command

```bash
docker run -d \
  --name youtube-analyzer \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e YOUTUBE_API_KEY=your_api_key_here \
  youtube-analyzer:latest
```

## Environment Variables

Create a `.env` file in the project root:

```env
YOUTUBE_API_KEY=your_actual_api_key_here
```

## Volume Mounts

The `/app/data` directory is mounted to persist your CSV data files:

- **Videos CSV**: `classical_music_videos_*.csv`
- **Channels CSV**: `classical_music_channels_*.csv`
- **Reports**: `extraction_summary_*.txt`

## Docker Commands Reference

### Build
```bash
# Build image
docker build -t youtube-analyzer:latest .

# Build with no cache
docker build --no-cache -t youtube-analyzer:latest .
```

### Run
```bash
# Run in foreground
docker run -p 8000:8000 youtube-analyzer:latest

# Run in background
docker run -d -p 8000:8000 youtube-analyzer:latest

# Run with volume mount
docker run -d -p 8000:8000 -v ./data:/app/data youtube-analyzer:latest
```

### Manage
```bash
# List containers
docker ps

# View logs
docker logs youtube-analyzer

# Follow logs
docker logs -f youtube-analyzer

# Stop container
docker stop youtube-analyzer

# Remove container
docker rm youtube-analyzer

# Remove image
docker rmi youtube-analyzer:latest
```

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Remove volumes
docker-compose down -v
```

## Deploy to Cloud Platforms

### Deploy to AWS ECS

1. **Push to ECR**:
```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag youtube-analyzer:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/youtube-analyzer:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/youtube-analyzer:latest
```

2. **Create ECS Task Definition** with environment variable `YOUTUBE_API_KEY`

3. **Create ECS Service** and expose port 8000

### Deploy to Azure Container Instances

```bash
# Create resource group
az group create --name youtube-analyzer-rg --location eastus

# Create container instance
az container create \
  --resource-group youtube-analyzer-rg \
  --name youtube-analyzer \
  --image youtube-analyzer:latest \
  --dns-name-label youtube-analyzer \
  --ports 8000 \
  --environment-variables YOUTUBE_API_KEY=your_key_here
```

### Deploy to Google Cloud Run

```bash
# Tag for Google Container Registry
docker tag youtube-analyzer:latest gcr.io/<project-id>/youtube-analyzer:latest

# Push to GCR
docker push gcr.io/<project-id>/youtube-analyzer:latest

# Deploy to Cloud Run
gcloud run deploy youtube-analyzer \
  --image gcr.io/<project-id>/youtube-analyzer:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars YOUTUBE_API_KEY=your_key_here
```

### Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create youtube-analyzer-demo

# Set API key
heroku config:set YOUTUBE_API_KEY=your_key_here

# Push to Heroku
heroku container:push web
heroku container:release web

# Open app
heroku open
```

## Production Considerations

### Security
- **Never commit** `.env` file with real API keys
- Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- Enable HTTPS/TLS in production
- Implement authentication if exposing publicly

### Performance
- Use production WSGI server (already using uvicorn)
- Consider adding Redis for caching
- Set resource limits in docker-compose:
  ```yaml
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
  ```

### Monitoring
- Add application monitoring (New Relic, DataDog, etc.)
- Set up log aggregation (ELK Stack, CloudWatch, etc.)
- Configure health check endpoint (already available at `/health`)

### Scaling
- Use orchestration platforms (Kubernetes, Docker Swarm)
- Implement horizontal scaling with load balancer
- Consider database for large-scale data storage

## Health Check

The application includes a health check endpoint:

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy"}
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs youtube-analyzer

# Common issues:
# - Missing .env file or API key
# - Port 8000 already in use
# - Insufficient memory
```

### Data not persisting
```bash
# Ensure volume is properly mounted
docker inspect youtube-analyzer | grep Mounts -A 10

# Check data directory permissions
ls -la ./data
```

### Can't access application
```bash
# Verify container is running
docker ps

# Check port mapping
docker port youtube-analyzer

# Test from inside container
docker exec youtube-analyzer curl http://localhost:8000/health
```

## Demo Deployment Checklist

For your client demo:

- ✅ Build Docker image
- ✅ Test locally with `docker-compose up`
- ✅ Verify all 6 pages load correctly
- ✅ Check analytics display properly
- ✅ Test CSV download functionality
- ✅ Verify data tables with search/pagination
- ✅ Ensure quota management works
- ✅ Deploy to cloud platform (optional)
- ✅ Prepare backup of data files
- ✅ Document any custom configurations

## Support

For issues or questions:
- Check application logs: `docker-compose logs -f`
- Verify API endpoint: `curl http://localhost:8000/api/status`
- Review quota status: `curl http://localhost:8000/api/quota/status`

---

**Ready for Client Demo!** 🎉

Your application is now containerized and ready to impress your client with:
- ✅ Professional Docker deployment
- ✅ Easy cloud deployment options
- ✅ Scalable architecture
- ✅ Production-ready setup
