#!/bin/bash
set -e

echo "=============================================="
echo "DEPLOYING INTERVIEW PREDICTOR"
echo "=============================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Create .env with: GEMINI_API_KEY=your_key"
    exit 1
fi

# Stop and remove old containers
echo "=== Stopping old containers ==="
docker-compose down 2>/dev/null || true

# Build fresh image
echo ""
echo "=== Building Docker image ==="
docker-compose build --no-cache

# Start services
echo ""
echo "=== Starting services ==="
docker-compose up -d

# Wait for startup
echo ""
echo "=== Waiting for startup (30 seconds) ==="
sleep 30

# Check health
echo ""
echo "=== Testing health endpoint ==="
for i in {1..5}; do
    if curl -sf http://localhost:8080/health; then
        echo ""
        echo "✅ HEALTH CHECK PASSED!"
        break
    fi
    echo "Attempt $i/5..."
    sleep 3
done

# Show logs
echo ""
echo "=== Container logs ==="
docker-compose logs --tail=50

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")

echo ""
echo "=============================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "=============================================="
echo "URL: http://$PUBLIC_IP:8080"
echo ""
echo "Commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo "  Rebuild:      docker-compose up -d --build"
