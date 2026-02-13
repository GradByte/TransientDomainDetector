#!/bin/bash

# Setup script for Transient Domain Detector

echo "========================================"
echo "Transient Domain Detector - Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker."
    exit 1
fi

echo "✓ Docker found: $(docker --version)"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✓ Docker Compose found: $(docker-compose --version)"

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if model exists
if [ ! -f "saved_models/malicious_domain_model_20260213_082703.joblib" ]; then
    echo ""
    echo "⚠️  Warning: Model file not found!"
    echo "   Expected: saved_models/malicious_domain_model_20260213_082703.joblib"
    echo "   Please ensure the model file is in the correct location."
else
    echo ""
    echo "✓ Model file found"
fi

# Start Elasticsearch and Kibana
echo ""
echo "Starting Elasticsearch and Kibana..."
docker-compose up -d

# Wait for Elasticsearch to be ready
echo ""
echo "Waiting for Elasticsearch to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        echo "✓ Elasticsearch is ready"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

# Wait for Kibana to be ready
echo ""
echo "Waiting for Kibana to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5601/api/status > /dev/null 2>&1; then
        echo "✓ Kibana is ready"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Services running:"
echo "  - Elasticsearch: http://localhost:9200"
echo "  - Kibana:        http://localhost:5601"
echo ""
echo "To run the detector:"
echo "  ./run.sh"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "========================================"
