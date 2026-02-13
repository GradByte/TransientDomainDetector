"""
Real-time Transient Domain Detection with Spark Streaming
Reads from Kafka, classifies domains using ML, writes to Elasticsearch
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import Row
import json
import sys
from datetime import datetime
from feature_extractor import DomainFeatureExtractor
from domain_classifier import DomainClassifier
from elasticsearch_writer import ElasticsearchWriter
import logging
import warnings

# Silence deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TransientDomainDetector:
    """
    Real-time transient domain detection system using Spark Streaming.
    """
    
    def __init__(self, model_path, kafka_servers, kafka_topic, es_host, es_index):
        """
        Initialize the detector.
        
        Args:
            model_path: Path to the trained ML model
            kafka_servers: Kafka bootstrap servers
            kafka_topic: Kafka topic to subscribe to
            es_host: Elasticsearch host
            es_index: Elasticsearch index name
        """
        self.model_path = model_path
        self.kafka_servers = kafka_servers
        self.kafka_topic = kafka_topic
        self.es_host = es_host
        self.es_index = es_index
        
        # Initialize Spark Session
        logger.info("Initializing Spark Session...")
        self.spark = SparkSession.builder \
            .appName("TransientDomainDetector") \
            .config("spark.jars.packages", 
                   "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
            .config("spark.sql.streaming.checkpointLocation", "./checkpoint") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Initialize feature extractor
        logger.info("Initializing Feature Extractor...")
        self.feature_extractor = DomainFeatureExtractor()
        
        # Initialize ML classifier
        logger.info(f"Loading ML model from {model_path}...")
        self.classifier = DomainClassifier(model_path)
        
        # Initialize Elasticsearch writer
        logger.info(f"Connecting to Elasticsearch at {es_host}...")
        self.es_writer = ElasticsearchWriter(es_host, es_index)
        
        logger.info("Initialization complete!")
    
    def process_batch(self, batch_df, batch_id):
        """
        Process a batch of domains: extract features, classify, write to ES.
        
        Args:
            batch_df: Batch dataframe from Spark
            batch_id: Batch identifier
        """
        if batch_df.isEmpty():
            logger.info(f"Batch {batch_id}: No data")
            return
        
        logger.info(f"Processing batch {batch_id} with {batch_df.count()} domains")
        
        # Collect domains from the batch
        domains = batch_df.collect()
        
        results = []
        for row in domains:
            try:
                domain = row.domain
                cert_index = row.cert_index
                ct_name = row.ct_name
                timestamp = row.timestamp
                
                # Extract features
                features = self.feature_extractor.extract_all_model_features(domain)
                
                # Classify domain
                prediction = self.classifier.predict(features)
                
                # Apply confidence threshold: benign with <80% confidence → flag for review
                original_prediction = prediction['prediction']
                original_label = prediction['prediction_label']
                needs_review = False
                
                if prediction['prediction'] == 'benign' and prediction['confidence'] < 0.80:
                    # Flag for review with special label (2 = needs review)
                    prediction['prediction'] = 'review'
                    prediction['prediction_label'] = 2
                    needs_review = True
                
                # Prepare result for Elasticsearch
                result = {
                    'domain': domain,
                    'cert_index': cert_index,
                    'ct_name': ct_name,
                    'kafka_timestamp': timestamp,
                    'prediction': prediction['prediction'],
                    'prediction_label': prediction['prediction_label'],
                    'confidence': prediction['confidence'],
                    'benign_probability': prediction['probabilities']['benign'],
                    'malicious_probability': prediction['probabilities']['malicious'],
                    'original_prediction': original_prediction,
                    'original_prediction_label': original_label,
                    'needs_review': needs_review,
                    'review_reason': 'low_confidence_benign' if needs_review else None,
                    'processed_timestamp': datetime.utcnow().isoformat(),
                    'batch_id': batch_id,
                    'features': {
                        'DomainLength': features['DomainLength'],
                        'VowelRatio': features['VowelRatio'],
                        'ConsoantRatio': features['ConsoantRatio'],
                        'NumericRatio': features['NumericRatio'],
                        'NumericSequence': features['NumericSequence'],
                        'StrangeCharacters': features['StrangeCharacters'],
                        'DNSRecordType': features['DNSRecordType']
                    }
                }
                
                results.append(result)
                
                # Log result
                if prediction['prediction'] == 'review':
                    status = "⚠️  REVIEW"
                elif prediction['prediction'] == 'malicious':
                    status = "🔴 MALICIOUS"
                else:
                    status = "✓ BENIGN"
                logger.info(f"  {domain:<40} {status} (confidence: {prediction['confidence']:.2%})")
                
            except Exception as e:
                logger.error(f"Error processing domain {row.domain}: {e}")
                continue
        
        # Write results to Elasticsearch
        if results:
            try:
                self.es_writer.bulk_index(results)
                logger.info(f"Batch {batch_id}: Written {len(results)} results to Elasticsearch")
            except Exception as e:
                logger.error(f"Error writing to Elasticsearch: {e}")
    
    def run(self, duration_minutes=1):
        """
        Run the streaming application.
        
        Args:
            duration_minutes: How long to run (in minutes)
        """
        logger.info("="*70)
        logger.info("TRANSIENT DOMAIN DETECTOR - STARTING")
        logger.info("="*70)
        logger.info(f"Kafka Servers: {self.kafka_servers}")
        logger.info(f"Kafka Topic: {self.kafka_topic}")
        logger.info(f"Elasticsearch: {self.es_host}")
        logger.info(f"Index: {self.es_index}")
        logger.info(f"Duration: {duration_minutes} minute(s)")
        logger.info("="*70)
        
        # Define schema for Kafka messages
        schema = StructType([
            StructField("domain", StringType(), True),
            StructField("cert_index", LongType(), True),
            StructField("ct_name", StringType(), True),
            StructField("timestamp", LongType(), True)
        ])
        
        # Read from Kafka stream
        kafka_df = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_servers) \
            .option("subscribe", self.kafka_topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        # Parse JSON from Kafka
        parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json") \
            .select(from_json(col("json"), schema).alias("data")) \
            .select("data.*")
        
        # Process stream in batches
        query = parsed_df.writeStream \
            .foreachBatch(self.process_batch) \
            .outputMode("append") \
            .trigger(processingTime='10 seconds') \
            .start()
        
        # Run for specified duration
        logger.info(f"\n🚀 Streaming started! Processing domains for {duration_minutes} minute(s)...\n")
        
        try:
            # Wait for the specified duration (convert minutes to milliseconds)
            query.awaitTermination(timeout=duration_minutes * 60)
            logger.info("\n⏰ Time limit reached. Stopping stream...")
            query.stop()
        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user. Stopping stream...")
            query.stop()
        except Exception as e:
            logger.error(f"\n❌ Error during streaming: {e}")
            query.stop()
            raise
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("STREAMING COMPLETED")
        logger.info("="*70)
        logger.info(f"Results written to Elasticsearch index: {self.es_index}")
        logger.info("You can now view the results in Kibana!")
        logger.info("="*70)
        
        self.spark.stop()


def main():
    """Main entry point."""
    # Configuration
    MODEL_PATH = "saved_models/malicious_domain_model_20260213_082703.joblib"
    KAFKA_SERVERS = "kafka.zonestream.openintel.nl:9092"
    KAFKA_TOPIC = "newly_registered_domain"
    ES_HOST = "http://localhost:9200"
    ES_INDEX = "transient-domains"
    DURATION_MINUTES = 10  # Run for 1 minute
    
    # Check if model exists
    import os
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Model file not found: {MODEL_PATH}")
        logger.error("Please ensure the model file is in the correct location.")
        sys.exit(1)
    
    try:
        # Initialize and run detector
        detector = TransientDomainDetector(
            model_path=MODEL_PATH,
            kafka_servers=KAFKA_SERVERS,
            kafka_topic=KAFKA_TOPIC,
            es_host=ES_HOST,
            es_index=ES_INDEX
        )
        
        detector.run(duration_minutes=DURATION_MINUTES)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
