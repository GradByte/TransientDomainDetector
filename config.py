"""
Configuration for Transient Domain Detector
"""

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = "kafka.zonestream.openintel.nl:9092"
KAFKA_TOPIC = "newly_registered_domain"

# Model Configuration
MODEL_PATH = "saved_models/malicious_domain_model_20260213_082703.joblib"

# Elasticsearch Configuration
ELASTICSEARCH_HOST = "http://localhost:9200"
ELASTICSEARCH_INDEX = "transient-domains"

# Spark Configuration
SPARK_APP_NAME = "TransientDomainDetector"
SPARK_CHECKPOINT_DIR = "./checkpoint"

# Processing Configuration
PROCESSING_DURATION_MINUTES = 1  # How long to collect and process domains
BATCH_INTERVAL_SECONDS = 10  # Process batch every 10 seconds

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
