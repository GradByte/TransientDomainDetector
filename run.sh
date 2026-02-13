#!/bin/bash

# Run script for Transient Domain Detector

echo "========================================"
echo "Transient Domain Detector"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Elasticsearch is running
if ! curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo "❌ Elasticsearch is not running. Starting services..."
    docker-compose up -d
    
    echo "Waiting for Elasticsearch to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
            echo "✓ Elasticsearch is ready"
            break
        fi
        sleep 2
    done
fi

# Check if model exists
if [ ! -f "saved_models/malicious_domain_model_20260213_082703.joblib" ]; then
    echo "❌ Model file not found!"
    echo "   Expected: saved_models/malicious_domain_model_20260213_082703.joblib"
    exit 1
fi

echo ""
echo "Starting Transient Domain Detector..."
echo "Duration: 1 minute"
echo "========================================"
echo ""

# Run the Spark streaming application
python3 spark_streaming_app.py

echo ""
echo "========================================"
echo "Detection Complete!"
echo "========================================"
echo ""
echo "View results:"
echo "  - Kibana Dashboard: http://localhost:5601"
echo "  - Elasticsearch:    http://localhost:9200/transient-domains/_search"
echo ""
echo "To view statistics:"
echo "  python3 view_results.py"
echo ""
echo "========================================"
