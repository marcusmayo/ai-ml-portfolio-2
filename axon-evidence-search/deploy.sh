#!/bin/bash

# Axon Evidence Search - One-Click Deployment Script
# This script deploys your AI evidence search tool to Google Cloud

echo "🚀 Starting Axon Evidence Search Deployment..."
echo "=============================================="

# Set your project (change this to your project ID)
PROJECT_ID="ai-ml-portfolio-473014"
echo "📝 Setting Google Cloud project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Navigate to backend directory
echo "📁 Moving to backend directory..."
cd ~/workspace/ai-ml-portfolio-2/axon-evidence-search/backend

# Enable required Google Cloud services
echo "🔧 Enabling Google Cloud services..."
echo "   - Vision API (for AI image analysis)"
echo "   - App Engine (for web hosting)"
gcloud services enable vision.googleapis.com
gcloud services enable appengine.googleapis.com

# Check if App Engine app exists, if not create it
echo "🏗️  Setting up App Engine..."
if ! gcloud app describe >/dev/null 2>&1; then
    echo "   Creating new App Engine application..."
    gcloud app create --region=us-central
else
    echo "   App Engine application already exists"
fi

# Deploy the application
echo "🚀 Deploying to Google Cloud..."
echo "   This may take 2-3 minutes..."
gcloud app deploy --quiet

# Get the application URL
echo "✅ Deployment complete!"
echo "=============================================="
echo "🌐 Your live demo URL:"
gcloud app browse --no-launch-browser

echo ""
echo "🎯 Next Steps:"
echo "1. Click the URL above to test your demo"
echo "2. Upload test images from: axon-evidence-search/data/sample_images/"
echo "3. Share the URL with your hiring manager!"
echo ""
echo "💡 Pro Tip: The first request might be slow (cold start)"
echo "   Visit the URL once before your demo to warm it up!"
echo ""
echo "🔍 Troubleshooting:"
echo "   - Check logs: gcloud app logs tail -s default"
echo "   - View in console: https://console.cloud.google.com/appengine"
echo ""
echo "Good luck with your interview! 🍀"
