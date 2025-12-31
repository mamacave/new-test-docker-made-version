# Cave Fire Proposals - Deployment Guide

This guide covers multiple deployment strategies for the Cave Fire Proposals API.

## Table of Contents

- [Quick Start with Docker](#quick-start-with-docker)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
  - [Docker Compose](#docker-compose)
  - [Kubernetes](#kubernetes)
  - [Cloud Platforms](#cloud-platforms)
- [CI/CD Pipeline](#cicd-pipeline)
- [Configuration](#configuration)
- [Monitoring & Logging](#monitoring--logging)

---

## Quick Start with Docker

Build and run the application using Docker:

```bash
# Build the image
docker build -t cave-fire-proposals:latest .

# Run the container
docker run -p 8000:8000 cave-fire-proposals:latest

# Test the API
curl http://localhost:8000/api/compose -H "Content-Type: application/json" -d '{}'
```

---

## Local Development

### Using Docker Compose

The easiest way to run the application locally:

```bash
# Start the API server
docker-compose up

# Or run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

The API will be available at `http://localhost:8000`.

### With Nginx (Production-like)

To run with nginx as a reverse proxy:

```bash
docker-compose --profile production up
```

This starts both the API and nginx on port 80.

### Without Docker

If you prefer to run without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.server:app --reload --port 8000
```

---

## Production Deployment

### Docker Compose

For simple production deployments:

1. Update `docker-compose.yml` environment variables
2. Remove the `--reload` flag from the command
3. Configure nginx with SSL certificates
4. Deploy:

```bash
docker-compose --profile production up -d
```

### Kubernetes

#### Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Container registry access (e.g., GitHub Container Registry)

#### Deployment Steps

1. **Build and push the image:**

```bash
# Using the CI/CD pipeline (recommended)
git tag v1.0.0
git push origin v1.0.0

# Or manually
docker build -t ghcr.io/YOUR_ORG/cave-fire-proposals:v1.0.0 .
docker push ghcr.io/YOUR_ORG/cave-fire-proposals:v1.0.0
```

2. **Update the Kubernetes manifests:**

Edit `deployment/kubernetes-deployment.yml` and update:
- Image repository: `ghcr.io/YOUR_ORG/YOUR_REPO`
- Domain: `api.example.com`
- Resource limits based on your needs

3. **Deploy to Kubernetes:**

```bash
# Apply the manifests
kubectl apply -f deployment/kubernetes-deployment.yml

# Check deployment status
kubectl get pods -n cave-fire-proposals
kubectl get svc -n cave-fire-proposals

# View logs
kubectl logs -n cave-fire-proposals -l app=cave-fire-proposals-api -f
```

#### Using Helm (Alternative)

If you have a Helm chart:

```bash
helm install cave-fire-proposals ./chart \
  --namespace cave-fire-proposals \
  --create-namespace \
  --values deployment/helm-values.yml
```

Update the values in `deployment/helm-values.yml` before deploying.

### Cloud Platforms

#### AWS ECS

1. Push image to ECR:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag cave-fire-proposals:latest <account>.dkr.ecr.us-east-1.amazonaws.com/cave-fire-proposals:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/cave-fire-proposals:latest
```

2. Create ECS task definition with:
   - Image: Your ECR image
   - Port mapping: 8000
   - Environment variables
   - Resource limits

3. Create ECS service with ALB

#### Google Cloud Run

```bash
# Build and deploy in one command
gcloud run deploy cave-fire-proposals \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name cave-fire-proposals \
  --image ghcr.io/YOUR_ORG/cave-fire-proposals:latest \
  --dns-name-label cave-fire-proposals \
  --ports 8000
```

#### Fly.io

Create `fly.toml`:

```toml
app = "cave-fire-proposals"

[build]
  image = "ghcr.io/YOUR_ORG/cave-fire-proposals:latest"

[[services]]
  http_checks = []
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

Deploy:

```bash
fly deploy
```

---

## CI/CD Pipeline

The repository includes a GitHub Actions workflow that:

1. **Builds** the Docker image
2. **Pushes** to GitHub Container Registry
3. **Scans** for security vulnerabilities
4. **Tags** images appropriately
5. **Generates** deployment artifacts

### Automatic Deployments

**On push to main:**
- Builds and tags as `latest`
- Runs security scans
- Available at: `ghcr.io/YOUR_ORG/YOUR_REPO:latest`

**On tag (v*):**
- Builds and tags with version
- Creates semantic version tags
- Available at: `ghcr.io/YOUR_ORG/YOUR_REPO:v1.0.0`

### Manual Deployment

Trigger manually from GitHub Actions UI or:

```bash
gh workflow run build-and-deploy.yml
```

### Accessing Container Images

Images are published to GitHub Container Registry. To pull:

```bash
# Login (if private)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull the image
docker pull ghcr.io/YOUR_ORG/YOUR_REPO:latest
```

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Environment name | `production` | No |
| `LOG_LEVEL` | Logging level | `info` | No |

### Secrets Management

For production, use proper secrets management:

**Kubernetes:**
```bash
kubectl create secret generic app-secrets \
  --from-literal=API_KEY=your-secret \
  -n cave-fire-proposals
```

**Docker Compose:**
```bash
# Use .env file (not committed)
echo "API_KEY=your-secret" > .env
```

---

## Monitoring & Logging

### Health Checks

The application includes built-in health checks:

```bash
# Docker health check runs automatically
docker ps  # Check HEALTH status

# Manual health check
curl http://localhost:8000/api/compose
```

### Kubernetes Health Checks

The deployment includes:
- **Liveness probe**: Ensures pod is running
- **Readiness probe**: Ensures pod is ready for traffic

### Logs

**Docker Compose:**
```bash
docker-compose logs -f api
```

**Kubernetes:**
```bash
# All pods
kubectl logs -n cave-fire-proposals -l app=cave-fire-proposals-api -f

# Specific pod
kubectl logs -n cave-fire-proposals <pod-name> -f
```

### Metrics (Optional)

To add Prometheus metrics:

1. Install `prometheus-fastapi-instrumentator`:
```bash
pip install prometheus-fastapi-instrumentator
```

2. Add to `app/server.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

3. Scrape metrics from `/metrics` endpoint

---

## Scaling

### Horizontal Scaling

**Kubernetes:**
```bash
# Manual scaling
kubectl scale deployment cave-fire-proposals-api --replicas=5 -n cave-fire-proposals

# Auto-scaling is configured via HPA (3-10 replicas based on CPU/memory)
kubectl get hpa -n cave-fire-proposals
```

**Docker Compose:**
```bash
docker-compose up --scale api=3
```

### Performance Tuning

For high-traffic scenarios, adjust:

1. **Worker processes** (add to Dockerfile CMD):
```bash
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

2. **Resource limits** in Kubernetes manifests

3. **Connection pooling** if using databases

---

## Rollback

### Kubernetes

```bash
# View rollout history
kubectl rollout history deployment/cave-fire-proposals-api -n cave-fire-proposals

# Rollback to previous version
kubectl rollout undo deployment/cave-fire-proposals-api -n cave-fire-proposals

# Rollback to specific revision
kubectl rollout undo deployment/cave-fire-proposals-api --to-revision=2 -n cave-fire-proposals
```

### Docker Compose

```bash
# Pull previous image version
docker pull ghcr.io/YOUR_ORG/YOUR_REPO:v1.0.0

# Update docker-compose.yml with the old tag
# Restart services
docker-compose down
docker-compose up -d
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs <container-id>

# Check if port is available
lsof -i :8000

# Inspect container
docker inspect <container-id>
```

### Kubernetes pod failures

```bash
# Describe pod for events
kubectl describe pod <pod-name> -n cave-fire-proposals

# Check logs
kubectl logs <pod-name> -n cave-fire-proposals

# Check resource constraints
kubectl top pods -n cave-fire-proposals
```

### Image pull errors

```bash
# Verify image exists
docker pull ghcr.io/YOUR_ORG/YOUR_REPO:latest

# Check image pull secrets
kubectl get secrets -n cave-fire-proposals
```

---

## Security Best Practices

1. ✅ **Non-root user** - Container runs as user 1000
2. ✅ **Multi-stage build** - Minimal attack surface
3. ✅ **Security scanning** - Trivy scans in CI/CD
4. ✅ **Read-only root filesystem** - Can be enabled if needed
5. ✅ **Resource limits** - Prevents resource exhaustion
6. ✅ **Network policies** - Add Kubernetes NetworkPolicies as needed

### Additional Security

- Use private registries for images
- Enable Pod Security Standards
- Rotate credentials regularly
- Keep base images updated
- Monitor CVE databases

---

## Support

For issues or questions:
- Check application logs
- Review CI/CD pipeline output
- Check resource utilization
- Verify network connectivity

