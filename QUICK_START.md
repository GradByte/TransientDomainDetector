# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup (5 minutes)

```bash
./setup.sh
```

This will:
- ✅ Install Python dependencies
- ✅ Start Elasticsearch & Kibana (Docker)
- ✅ Verify model is present

### Step 2: Run (1 minute)

```bash
./run.sh
```

This will:
- ✅ Connect to OpenINTEL Kafka stream
- ✅ Collect newly registered domains for 1 minute
- ✅ Extract features and classify each domain
- ✅ Store results in Elasticsearch

### Step 3: View Results

```bash
python3 view_results.py
```

Or open Kibana: http://localhost:5601

---

## 📊 What You'll See

### Console Output (during run)

```
Processing batch 1 with 15 domains
  google-analytics-test.com         ✓ BENIGN (confidence: 98.50%)
  suspicious-domain-12345.net       🔴 MALICIOUS (confidence: 95.20%)
  legitimate-site.org               ✓ BENIGN (confidence: 99.10%)
  ...
```

### Results Summary

```
STATISTICS
  Total Domains Analyzed:         150
  Malicious Domains:               12 ( 8.00%)
  Benign Domains:                 138 (92.00%)
  Average Confidence:           95.23%
```

---

## 🔧 Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View Elasticsearch data
curl http://localhost:9200/transient-domains/_search?pretty

# Test system before running
python3 test_system.py

# View logs
docker-compose logs -f elasticsearch
```

---

## 🌐 Access Points

- **Kibana Dashboard**: http://localhost:5601
- **Elasticsearch API**: http://localhost:9200
- **Index Name**: `transient-domains`

---

## ⚡ Quick Test

Want to test without running the full system?

```bash
# Test feature extraction
python3 -c "
from feature_extractor import DomainFeatureExtractor
extractor = DomainFeatureExtractor()
features = extractor.extract_features('suspicious-domain-12345.com')
print(features)
"

# Test classification
python3 -c "
from domain_classifier import DomainClassifier
from feature_extractor import DomainFeatureExtractor

classifier = DomainClassifier('saved_models/malicious_domain_model_20260213_082703.joblib')
extractor = DomainFeatureExtractor()

features = extractor.extract_all_model_features('xk2j9m3p4q5r.com')
result = classifier.predict(features)
print(f\"Prediction: {result['prediction']} ({result['confidence']:.2%})\")
"
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Elasticsearch not starting | Increase Docker memory to at least 4GB |
| "Model not found" error | Check `saved_models/` directory has the .joblib file |
| No data in results | Wait for Kafka stream (may take 10-30 seconds for first data) |
| Import errors | Run `pip install -r requirements.txt` |

---

## 📝 Notes

- **Duration**: System runs for 1 minute by default (configurable in `config.py`)
- **Processing**: Domains are processed in 10-second batches
- **Rate**: Depends on OpenINTEL stream (usually 50-200 domains/minute)
- **Storage**: All results are stored in Elasticsearch for later analysis

---

## 🎯 Next Steps

1. ✅ Run the detector
2. ✅ View results in Kibana
3. ✅ Create custom dashboards
4. ✅ Set up alerts for malicious domains
5. ✅ Integrate with your security tools

---

**Need Help?** Check the full [README.md](README.md) for detailed documentation.
