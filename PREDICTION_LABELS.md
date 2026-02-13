# Prediction Label Reference

## 🏷️ Prediction Labels

The system uses a 3-category classification system:

| Label | Prediction | Description | Action |
|-------|-----------|-------------|--------|
| **0** | `benign` | High-confidence benign domain (≥80% confidence) | ✅ Safe - No action needed |
| **1** | `malicious` | Malicious domain detected by model | 🔴 Block/Monitor |
| **2** | `review` | Low-confidence benign (<80% confidence) | ⚠️ Needs manual review |

---

## 📊 How It Works

### Label 0: Benign
- **Model prediction**: Benign
- **Confidence**: ≥ 80%
- **Action**: Domain is considered safe
- **Example**: `google.com` (98% confidence)

### Label 1: Malicious
- **Model prediction**: Malicious
- **Confidence**: Any
- **Action**: Domain should be blocked or monitored
- **Example**: `xk2j9m3p4q5r.com` (95% confidence)

### Label 2: Review (Low Confidence)
- **Model prediction**: Benign (originally)
- **Confidence**: < 80%
- **Action**: Needs manual review/further investigation
- **Reason**: Uncertainty suggests potential risk
- **Example**: `weird-domain-name.com` (72% confidence)

---

## 🔍 Querying in Elasticsearch

### Get all benign domains
```json
{
  "query": {
    "term": {
      "prediction_label": 0
    }
  }
}
```

### Get all malicious domains
```json
{
  "query": {
    "term": {
      "prediction_label": 1
    }
  }
}
```

### Get all domains needing review
```json
{
  "query": {
    "term": {
      "prediction_label": 2
    }
  }
}
```

### Get high-risk domains (malicious + review)
```json
{
  "query": {
    "terms": {
      "prediction_label": [1, 2]
    }
  }
}
```

---

## 📈 Kibana Visualizations

### Pie Chart - Distribution by Label

Create a pie chart with:
- **Slice by**: `prediction_label`
- **Metrics**: Count

This will show:
- 0 (Benign)
- 1 (Malicious)
- 2 (Review)

### Filter for Review Domains

In Kibana Discover, use:
```
prediction_label: 2
```

Or create a saved search:
```
prediction_label: 2 AND confidence < 0.8
```

---

## 🎯 Why Label 2 (Review)?

**Conservative Security Approach:**

1. **Low confidence = uncertainty**: When the model isn't confident, it's safer to flag for review
2. **Reduces false negatives**: Uncertain domains won't slip through as "benign"
3. **Human verification**: Allows security team to investigate suspicious but uncertain domains
4. **Historical tracking**: Can analyze which low-confidence domains turned out to be malicious

**Example Scenario:**
```
Domain: suspicious-looking-123.com
Original Prediction: benign (72% confidence)
New Label: 2 (review)
Result: Security team reviews and finds it's a typosquatting domain
```

---

## 📝 Document Fields

Each document in Elasticsearch contains:

```json
{
  "prediction": "review",                    // Current prediction
  "prediction_label": 2,                     // Current label (0/1/2)
  "original_prediction": "benign",           // Original model prediction
  "original_prediction_label": 0,            // Original label
  "confidence": 0.72,                        // Prediction confidence
  "needs_review": true,                      // Boolean flag
  "review_reason": "low_confidence_benign"   // Why it needs review
}
```

---

## 🛡️ Security Benefits

### Before (2 labels)
- Benign (80% confidence) → ✅ Marked as safe
- Risk: Uncertain domains might be malicious

### After (3 labels)
- Benign (80% confidence) → ⚠️ Flagged for review
- Benefit: Uncertain domains are investigated

---

## 💡 Tips

1. **Regular Review**: Check label 2 domains daily
2. **Threshold Tuning**: The 80% threshold can be adjusted in code if needed
3. **Automated Actions**: 
   - Label 0: Whitelist
   - Label 1: Blacklist
   - Label 2: Manual queue
4. **Analytics**: Track conversion rate of label 2 to label 1 (review → confirmed malicious)

---

## 🔧 Configuration

To change the confidence threshold (default: 80%), edit `spark_streaming_app.py`:

```python
if prediction['prediction'] == 'benign' and prediction['confidence'] < 0.80:
    # Change 0.80 to your desired threshold
```

**Recommendation**: Keep at 80% for balanced security and false positive rate.

---

**Quick Reference:**
- 0️⃣ = Safe ✅
- 1️⃣ = Dangerous 🔴
- 2️⃣ = Uncertain ⚠️
