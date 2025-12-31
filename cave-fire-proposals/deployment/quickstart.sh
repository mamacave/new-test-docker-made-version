#!/bin/bash
# Quick start script for deploying Cave Fire Proposals

set -e

PLATFORM=${1:-docker-compose}
ENVIRONMENT=${2:-development}

echo "🚀 Cave Fire Proposals - Quick Deploy"
echo "Platform: $PLATFORM"
echo "Environment: $ENVIRONMENT"
echo ""

case $PLATFORM in
  docker)
    echo "Building Docker image..."
    docker build -t cave-fire-proposals:latest .
    echo "Starting container..."
    docker run -d -p 8000:8000 --name cave-fire-proposals cave-fire-proposals:latest
    echo "✅ Deployed! API available at http://localhost:8000"
    ;;
    
  docker-compose)
    echo "Starting services with Docker Compose..."
    if [ "$ENVIRONMENT" == "production" ]; then
      docker-compose -f deployment/docker-compose.prod.yml up -d
    else
      docker-compose up -d
    fi
    echo "✅ Deployed! API available at http://localhost:8000"
    ;;
    
  kubernetes)
    echo "Deploying to Kubernetes..."
    kubectl apply -f deployment/kubernetes-deployment.yml
    echo "Waiting for deployment..."
    kubectl wait --for=condition=available --timeout=300s \
      deployment/cave-fire-proposals-api -n cave-fire-proposals
    echo "✅ Deployed to Kubernetes!"
    ;;
    
  cloud-run)
    echo "Deploying to Google Cloud Run..."
    gcloud run deploy cave-fire-proposals \
      --source . \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated
    ;;
    
  *)
    echo "❌ Unknown platform: $PLATFORM"
    echo "Usage: $0 [docker|docker-compose|kubernetes|cloud-run] [development|production]"
    exit 1
    ;;
esac

echo ""
echo "📋 Next steps:"
echo "  - Test: curl http://localhost:8000/api/compose -H 'Content-Type: application/json' -d '{}'"
echo "  - Logs: docker logs cave-fire-proposals (or kubectl logs ...)"
echo "  - Stop:  docker stop cave-fire-proposals (or docker-compose down)"
