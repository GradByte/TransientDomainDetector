"""
Test System Components
Verifies all components are working correctly before running the full system
"""

import sys
import os


def test_imports():
    """Test if all required imports work."""
    print("="*70)
    print("TESTING IMPORTS")
    print("="*70)
    
    tests = {
        "pandas": "pandas",
        "numpy": "numpy",
        "sklearn": "scikit-learn",
        "joblib": "joblib",
        "pyspark": "pyspark",
        "elasticsearch": "elasticsearch",
        "websocket": "websocket-client"
    }
    
    failed = []
    
    for module, package in tests.items():
        try:
            __import__(module)
            print(f"✓ {package:<25} OK")
        except ImportError as e:
            print(f"✗ {package:<25} FAILED")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("\n✓ All imports successful")
    return True


def test_model():
    """Test if model file exists and can be loaded."""
    print("\n" + "="*70)
    print("TESTING MODEL")
    print("="*70)
    
    model_path = "saved_models/malicious_domain_model_20260213_082703.joblib"
    
    if not os.path.exists(model_path):
        print(f"✗ Model file not found: {model_path}")
        return False
    
    print(f"✓ Model file exists: {model_path}")
    
    try:
        from domain_classifier import DomainClassifier
        classifier = DomainClassifier(model_path)
        print(f"✓ Model loaded successfully")
        print(f"  - Type: {classifier.metadata['model_type']}")
        print(f"  - Test Accuracy: {classifier.metadata['test_accuracy']:.4f}")
        print(f"  - Test AUC: {classifier.metadata['test_auc']:.4f}")
        print(f"  - Features: {classifier.metadata['n_features']}")
        return True
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return False


def test_feature_extraction():
    """Test feature extraction."""
    print("\n" + "="*70)
    print("TESTING FEATURE EXTRACTION")
    print("="*70)
    
    try:
        from feature_extractor import DomainFeatureExtractor
        
        extractor = DomainFeatureExtractor()
        
        # Test domains
        test_domains = [
            "google.com",
            "suspicious-domain-12345.com",
            "xk2j9m3p4q5r.net"
        ]
        
        print("\nExtracting features from test domains...")
        for domain in test_domains:
            features = extractor.extract_features(domain)
            print(f"\n  Domain: {domain}")
            print(f"    Length: {features['DomainLength']}")
            print(f"    Numeric Ratio: {features['NumericRatio']:.2f}")
            print(f"    Consonant Ratio: {features['ConsoantRatio']:.2f}")
        
        print("\n✓ Feature extraction working")
        return True
    except Exception as e:
        print(f"✗ Feature extraction failed: {e}")
        return False


def test_classification():
    """Test end-to-end classification."""
    print("\n" + "="*70)
    print("TESTING CLASSIFICATION")
    print("="*70)
    
    try:
        from domain_classifier import DomainClassifier
        from feature_extractor import DomainFeatureExtractor
        
        classifier = DomainClassifier("saved_models/malicious_domain_model_20260213_082703.joblib")
        extractor = DomainFeatureExtractor()
        
        test_cases = [
            ("google.com", "benign"),
            ("legitimate-site.org", "benign"),
            ("xk2j9m3p4q5r6s7t8u9v0w1x2y3z.com", "malicious"),
            ("test123456789012345.net", "suspicious")
        ]
        
        print("\nClassifying test domains...")
        for domain, expected in test_cases:
            features = extractor.extract_all_model_features(domain)
            result = classifier.predict(features)
            
            status = "🔴" if result['prediction'] == 'malicious' else "✓"
            print(f"\n  {status} {domain}")
            print(f"     Prediction: {result['prediction']}")
            print(f"     Confidence: {result['confidence']:.2%}")
        
        print("\n✓ Classification working")
        return True
    except Exception as e:
        print(f"✗ Classification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_elasticsearch():
    """Test Elasticsearch connection."""
    print("\n" + "="*70)
    print("TESTING ELASTICSEARCH")
    print("="*70)
    
    try:
        from elasticsearch import Elasticsearch
        
        es = Elasticsearch(["http://localhost:9200"], request_timeout=5)
        
        if es.ping():
            print("✓ Elasticsearch is running")
            
            # Get cluster info
            info = es.info()
            print(f"  Version: {info['version']['number']}")
            print(f"  Cluster: {info['cluster_name']}")
            
            return True
        else:
            print("✗ Elasticsearch is not responding")
            print("  Run: docker-compose up -d")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to Elasticsearch: {e}")
        print("  Make sure Elasticsearch is running: docker-compose up -d")
        return False


def test_spark():
    """Test Spark setup."""
    print("\n" + "="*70)
    print("TESTING SPARK")
    print("="*70)
    
    try:
        from pyspark.sql import SparkSession
        
        spark = SparkSession.builder \
            .appName("TestSpark") \
            .config("spark.driver.memory", "1g") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
        
        print("✓ Spark session created")
        print(f"  Version: {spark.version}")
        
        # Test simple operation
        data = [("test1", 1), ("test2", 2)]
        df = spark.createDataFrame(data, ["name", "value"])
        count = df.count()
        
        print(f"  Test DataFrame count: {count}")
        
        spark.stop()
        print("✓ Spark working correctly")
        return True
    except Exception as e:
        print(f"✗ Spark test failed: {e}")
        return False


def test_kafka_connectivity():
    """Test Kafka connectivity."""
    print("\n" + "="*70)
    print("TESTING KAFKA CONNECTIVITY")
    print("="*70)
    
    import socket
    
    kafka_host = "kafka.zonestream.openintel.nl"
    kafka_port = 9092
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((kafka_host, kafka_port))
        sock.close()
        
        if result == 0:
            print(f"✓ Can reach Kafka at {kafka_host}:{kafka_port}")
            return True
        else:
            print(f"✗ Cannot reach Kafka at {kafka_host}:{kafka_port}")
            print("  Check your internet connection and firewall settings")
            return False
    except Exception as e:
        print(f"✗ Kafka connectivity test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("TRANSIENT DOMAIN DETECTOR - SYSTEM TEST")
    print("="*70)
    
    tests = [
        ("Imports", test_imports),
        ("Model", test_model),
        ("Feature Extraction", test_feature_extraction),
        ("Classification", test_classification),
        ("Elasticsearch", test_elasticsearch),
        ("Spark", test_spark),
        ("Kafka Connectivity", test_kafka_connectivity)
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED - SYSTEM READY")
        print("="*70)
        print("\nYou can now run the detector:")
        print("  ./run.sh")
        print()
        return 0
    else:
        print("\n" + "="*70)
        print("✗ SOME TESTS FAILED - PLEASE FIX ISSUES")
        print("="*70)
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
