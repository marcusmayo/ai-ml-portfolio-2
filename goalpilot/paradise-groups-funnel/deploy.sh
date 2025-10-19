#!/bin/bash
set -e

echo "🏗️  Building Docker image..."
docker build -t paradise-funnel:v1 -f infra/Dockerfile .

echo "🏷️  Tagging for GCR..."
docker tag paradise-funnel:v1 gcr.io/paradise-groups-funnel/paradise-funnel:v1

echo "☁️  Pushing to GCR..."
docker push gcr.io/paradise-groups-funnel/paradise-funnel:v1

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy paradise-funnel \
  --image gcr.io/paradise-groups-funnel/paradise-funnel:v1 \
  --region us-east1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --timeout 60s \
  --min-instances 0 \
  --max-instances 10

echo "✅ Deployment complete!"
gcloud run services describe paradise-funnel --region us-east1 --format='value(status.url)'
