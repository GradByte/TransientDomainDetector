# Saved Models Directory

This directory should contain your trained machine learning model for domain classification.

## ⚠️ Required Setup

**You must add a trained model to this directory before running the detector.**

### Getting the Model

#### Option 1: Train from MaliciousDomainDetectorML Repository

1. Clone the model training repository:
   ```bash
   git clone https://github.com/GradByte/MaliciousDomainDetectorML.git
   cd MaliciousDomainDetectorML
   ```

2. Install dependencies and train the model:
   ```bash
   pip install -r requirements.txt
   python malicious_domain_detector.py
   ```

3. Copy the trained model files here:
   ```bash
   cp saved_models/*.joblib "/path/to/Transient Domain Detector/saved_models/"
   cp saved_models/*.json "/path/to/Transient Domain Detector/saved_models/"
   ```

#### Option 2: Use Your Own Model

If you have your own trained model:
- Place your `.joblib` model file in this directory
- Update `config.py` with your model filename
- Ensure your model is compatible with the feature extraction in `feature_extractor.py`

### Expected Files

After setup, this directory should contain:
```
saved_models/
├── your_model.joblib              # Your trained model
└── your_model_metadata.json       # (Optional) Model metadata
```

### Model Format

The model should be:
- Saved using `joblib` or `pickle`
- A scikit-learn compatible classifier
- Trained to use the 7 features extracted by `feature_extractor.py`:
  - DomainLength
  - VowelRatio
  - ConsoantRatio
  - NumericRatio
  - NumericSequence
  - StrangeCharacters
  - DNSRecordType

### Update Configuration

After adding your model, update the `MODEL_PATH` in `config.py`:

```python
MODEL_PATH = "saved_models/malicious_domain_model_YYYYMMDD_HHMMSS.joblib"
```

Replace with your actual model filename.

---

**Note**: Model files are not included in this repository due to their size. You must obtain or train them separately.
