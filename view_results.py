#!/usr/bin/env python3
"""
View Results from Elasticsearch
Displays statistics and recent detections
"""

from elasticsearch_writer import ElasticsearchWriter
from datetime import datetime
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70)


def print_section(text):
    """Print a formatted section header."""
    print("\n" + "-"*70)
    print(text)
    print("-"*70)


def main():
    """Display results from Elasticsearch."""
    
    print_header("TRANSIENT DOMAIN DETECTOR - RESULTS")
    
    try:
        # Connect to Elasticsearch
        writer = ElasticsearchWriter("http://localhost:9200", "transient-domains")
        
        # Get statistics
        print_section("STATISTICS")
        stats = writer.get_statistics()
        
        if stats:
            print(f"\n  Total Domains Analyzed:     {stats['total_domains']:>6}")
            print(f"  Malicious Domains:          {stats['malicious_domains']:>6} ({stats['malicious_percentage']:>5.2f}%)")
            print(f"  Benign Domains:             {stats['benign_domains']:>6} ({100-stats['malicious_percentage']:>5.2f}%)")
            print(f"  Needs Review (Low Conf):    {stats['review_domains']:>6} ({stats['review_percentage']:>5.2f}%)")
            print(f"  Average Confidence:         {stats['avg_confidence']:>6.2%}")
            print(f"  Avg Malicious Probability:  {stats['avg_malicious_probability']:>6.2%}")
        else:
            print("\n  No data available yet.")
        
        # Get domains needing review
        print_section("DOMAINS NEEDING REVIEW (Low Confidence Benign - Top 20)")
        review_domains = writer.get_review_domains(limit=20)
        
        if review_domains:
            print(f"\n  {'Domain':<45} {'Confidence':<12} {'Reason'}")
            print("  " + "-"*75)
            
            for domain_data in review_domains:
                domain = domain_data['domain']
                confidence = domain_data['confidence']
                reason = domain_data.get('review_reason', 'unknown')
                
                print(f"  {domain:<45} {confidence:>6.2%}      {reason}")
        else:
            print("\n  No domains flagged for review.")
        
        # Get recent malicious domains
        print_section("RECENT MALICIOUS DOMAINS (Top 20)")
        malicious = writer.get_malicious_domains(limit=20)
        
        if malicious:
            print(f"\n  {'Domain':<45} {'Confidence':<12} {'Time'}")
            print("  " + "-"*68)
            
            for domain_data in malicious:
                domain = domain_data['domain']
                confidence = domain_data['confidence']
                timestamp = domain_data.get('processed_timestamp', 'N/A')
                
                # Parse timestamp
                if timestamp != 'N/A':
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        time_str = timestamp
                else:
                    time_str = 'N/A'
                
                print(f"  {domain:<45} {confidence:>6.2%}      {time_str}")
        else:
            print("\n  No malicious domains detected yet.")
        
        # Get all recent domains (mixed)
        print_section("RECENT DETECTIONS (All - Last 15)")
        
        query = {
            "query": {"match_all": {}},
            "sort": [{"processed_timestamp": {"order": "desc"}}]
        }
        
        recent = writer.search(query, size=15)
        
        if recent and recent['hits']['hits']:
            print(f"\n  {'Domain':<40} {'Prediction':<12} {'Confidence':<12}")
            print("  " + "-"*68)
            
            for hit in recent['hits']['hits']:
                data = hit['_source']
                domain = data['domain'][:39]  # Truncate if too long
                prediction = data['prediction']
                confidence = data['confidence']
                
                pred_symbol = "🔴" if prediction == "malicious" else "✓"
                
                print(f"  {domain:<40} {pred_symbol} {prediction:<10} {confidence:>6.2%}")
        else:
            print("\n  No data available yet.")
        
        # Print footer
        print_header("END OF RESULTS")
        print("\nView more in Kibana: http://localhost:5601")
        print("Elasticsearch: http://localhost:9200/transient-domains/_search")
        print()
        
    except ConnectionError as e:
        print("\n❌ Error: Could not connect to Elasticsearch")
        print("   Make sure Elasticsearch is running: docker-compose up -d")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Full error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
