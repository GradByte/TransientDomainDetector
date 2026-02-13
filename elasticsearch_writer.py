"""
Elasticsearch Writer for Domain Classification Results
"""

from elasticsearch import Elasticsearch, helpers
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ElasticsearchWriter:
    """
    Writes domain classification results to Elasticsearch.
    """
    
    def __init__(self, es_host, index_name):
        """
        Initialize Elasticsearch connection.
        
        Args:
            es_host: Elasticsearch host URL (e.g., "http://localhost:9200")
            index_name: Name of the index to write to
        """
        self.es_host = es_host
        self.index_name = index_name
        
        # Connect to Elasticsearch
        self.es = Elasticsearch([es_host], request_timeout=30)
        
        # Check connection
        if self.es.ping():
            logger.info("✓ Connected to Elasticsearch")
        else:
            raise ConnectionError(f"Failed to connect to Elasticsearch at {es_host}")
        
        # Create index with mapping if it doesn't exist
        self._create_index_if_not_exists()
    
    def _create_index_if_not_exists(self):
        """Create the index with appropriate mapping if it doesn't exist."""
        if not self.es.indices.exists(index=self.index_name):
            logger.info(f"Creating index: {self.index_name}")
            
            mapping = {
                "mappings": {
                    "properties": {
                        "domain": {"type": "keyword"},
                        "cert_index": {"type": "long"},
                        "ct_name": {"type": "keyword"},
                        "kafka_timestamp": {"type": "long"},
                        "prediction": {"type": "keyword"},
                        "prediction_label": {"type": "integer"},
                        "confidence": {"type": "float"},
                        "benign_probability": {"type": "float"},
                        "malicious_probability": {"type": "float"},
                        "original_prediction": {"type": "keyword"},
                        "original_prediction_label": {"type": "integer"},
                        "needs_review": {"type": "boolean"},
                        "review_reason": {"type": "keyword"},
                        "processed_timestamp": {"type": "date"},
                        "batch_id": {"type": "long"},
                        "features": {
                            "properties": {
                                "DomainLength": {"type": "integer"},
                                "VowelRatio": {"type": "float"},
                                "ConsoantRatio": {"type": "float"},
                                "NumericRatio": {"type": "float"},
                                "NumericSequence": {"type": "integer"},
                                "StrangeCharacters": {"type": "integer"},
                                "DNSRecordType": {"type": "integer"}
                            }
                        }
                    }
                }
            }
            
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"✓ Index '{self.index_name}' created")
        else:
            logger.info(f"✓ Index '{self.index_name}' already exists")
    
    def index_document(self, document):
        """
        Index a single document.
        
        Args:
            document: Dictionary containing the document data
        """
        try:
            response = self.es.index(index=self.index_name, document=document)
            return response
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            raise
    
    def bulk_index(self, documents):
        """
        Index multiple documents in bulk for better performance.
        
        Args:
            documents: List of document dictionaries
        """
        if not documents:
            return
        
        actions = [
            {
                "_index": self.index_name,
                "_source": doc
            }
            for doc in documents
        ]
        
        try:
            success, failed = helpers.bulk(self.es, actions, raise_on_error=False)
            logger.info(f"✓ Indexed {success} documents successfully")
            
            if failed:
                logger.warning(f"⚠️  Failed to index {len(failed)} documents")
            
            return success, failed
        except Exception as e:
            logger.error(f"Error during bulk indexing: {e}")
            raise
    
    def search(self, query, size=10):
        """
        Search the index.
        
        Args:
            query: Elasticsearch query DSL
            size: Number of results to return
            
        Returns:
            Search results
        """
        try:
            response = self.es.search(index=self.index_name, body=query, size=size)
            return response
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise
    
    def get_malicious_domains(self, limit=10):
        """
        Get recently detected malicious domains.
        
        Args:
            limit: Number of results to return
            
        Returns:
            List of malicious domains
        """
        query = {
            "query": {
                "term": {
                    "prediction": "malicious"
                }
            },
            "sort": [
                {"processed_timestamp": {"order": "desc"}}
            ]
        }
        
        results = self.search(query, size=limit)
        return [hit["_source"] for hit in results["hits"]["hits"]]
    
    def get_review_domains(self, limit=10):
        """
        Get domains flagged for review (prediction_label = 2).
        
        Args:
            limit: Number of results to return
            
        Returns:
            List of domains needing review
        """
        query = {
            "query": {
                "term": {
                    "prediction_label": 2
                }
            },
            "sort": [
                {"processed_timestamp": {"order": "desc"}}
            ]
        }
        
        results = self.search(query, size=limit)
        return [hit["_source"] for hit in results["hits"]["hits"]]
    
    def get_statistics(self):
        """
        Get statistics about classified domains.
        
        Returns:
            Dictionary with statistics
        """
        try:
            # Total count
            total = self.es.count(index=self.index_name)["count"]
            
            # Malicious count (prediction_label = 1)
            malicious_query = {"query": {"term": {"prediction_label": 1}}}
            malicious_count = self.es.count(index=self.index_name, body=malicious_query)["count"]
            
            # Review count (prediction_label = 2)
            review_query = {"query": {"term": {"prediction_label": 2}}}
            review_count = self.es.count(index=self.index_name, body=review_query)["count"]
            
            # Benign count (prediction_label = 0)
            benign_query = {"query": {"term": {"prediction_label": 0}}}
            benign_count = self.es.count(index=self.index_name, body=benign_query)["count"]
            
            # Average confidence
            agg_query = {
                "size": 0,
                "aggs": {
                    "avg_confidence": {"avg": {"field": "confidence"}},
                    "avg_malicious_prob": {"avg": {"field": "malicious_probability"}}
                }
            }
            agg_results = self.es.search(index=self.index_name, body=agg_query)
            
            stats = {
                "total_domains": total,
                "malicious_domains": malicious_count,
                "benign_domains": benign_count,
                "review_domains": review_count,
                "malicious_percentage": (malicious_count / total * 100) if total > 0 else 0,
                "review_percentage": (review_count / total * 100) if total > 0 else 0,
                "avg_confidence": agg_results["aggregations"]["avg_confidence"]["value"],
                "avg_malicious_probability": agg_results["aggregations"]["avg_malicious_prob"]["value"]
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return None
    
    def delete_index(self):
        """Delete the index (use with caution!)."""
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            logger.info(f"✓ Index '{self.index_name}' deleted")
        else:
            logger.info(f"Index '{self.index_name}' does not exist")


# Test the writer
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("ELASTICSEARCH WRITER TEST")
    print("="*70)
    
    try:
        writer = ElasticsearchWriter("http://localhost:9200", "transient-domains-test")
        
        # Test document
        test_doc = {
            "domain": "test-domain-123.com",
            "cert_index": 123456,
            "ct_name": "Test Log",
            "kafka_timestamp": 1234567890,
            "prediction": "malicious",
            "prediction_label": 1,
            "confidence": 0.95,
            "benign_probability": 0.05,
            "malicious_probability": 0.95,
            "processed_timestamp": datetime.utcnow().isoformat(),
            "batch_id": 1,
            "features": {
                "DomainLength": 20,
                "VowelRatio": 0.3,
                "ConsoantRatio": 0.6,
                "NumericRatio": 0.15,
                "NumericSequence": 3,
                "StrangeCharacters": 2,
                "DNSRecordType": 0
            }
        }
        
        print("\nIndexing test document...")
        writer.index_document(test_doc)
        print("✓ Document indexed successfully")
        
        print("\nGetting statistics...")
        stats = writer.get_statistics()
        if stats:
            print(f"  Total domains: {stats['total_domains']}")
            print(f"  Malicious: {stats['malicious_domains']}")
            print(f"  Benign: {stats['benign_domains']}")
        
        print("\nCleaning up test index...")
        writer.delete_index()
        print("✓ Test complete")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        print("\nMake sure Elasticsearch is running:")
        print("  docker-compose up -d elasticsearch")
