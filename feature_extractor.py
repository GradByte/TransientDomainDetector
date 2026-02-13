"""
Feature Extraction Module for Domain Analysis
Extracts features from domain names for ML classification
"""

import re
import math
from collections import Counter
from typing import Dict


class DomainFeatureExtractor:
    """
    Extracts features from domain names for malicious domain detection.
    Focuses on the most important features that can be calculated directly from the domain.
    """
    
    def __init__(self):
        self.vowels = set('aeiouAEIOU')
        self.consonants = set('bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ')
        self.digits = set('0123456789')
        self.special_chars = set('.-_~!@#$%^&*()+={}[]|\\:;"\'<>?,/')
    
    def extract_features(self, domain: str) -> Dict:
        """
        Extract all important features from a domain name.
        
        Args:
            domain: Domain name (e.g., "example.com" or "example.com.")
            
        Returns:
            Dictionary with extracted features
        """
        # Clean domain (remove trailing dot if present)
        domain = domain.rstrip('.')
        
        # Extract domain without TLD for analysis
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            # Remove TLD for character analysis
            domain_without_tld = '.'.join(domain_parts[:-1])
        else:
            domain_without_tld = domain
        
        features = {}
        
        # 1. Domain Length
        features['DomainLength'] = len(domain)
        
        # 2. Character Ratios
        total_chars = len(domain_without_tld.replace('.', ''))
        if total_chars > 0:
            vowel_count = sum(1 for c in domain_without_tld if c in self.vowels)
            consonant_count = sum(1 for c in domain_without_tld if c in self.consonants)
            digit_count = sum(1 for c in domain_without_tld if c in self.digits)
            
            features['VowelRatio'] = vowel_count / total_chars
            features['ConsoantRatio'] = consonant_count / total_chars  # Typo intentional (matches dataset)
            features['NumericRatio'] = digit_count / total_chars
        else:
            features['VowelRatio'] = 0.0
            features['ConsoantRatio'] = 0.0
            features['NumericRatio'] = 0.0
        
        # 3. Numeric Sequence (longest consecutive digits)
        features['NumericSequence'] = self._longest_sequence(domain_without_tld, self.digits)
        
        # 4. Strange Characters (special characters count)
        features['StrangeCharacters'] = sum(1 for c in domain_without_tld 
                                           if c in self.special_chars and c not in '.-')
        
        # 5. DNS Record Type (default to 0 for A record, can be updated later)
        features['DNSRecordType'] = 0
        
        return features
    
    def _longest_sequence(self, text: str, char_set: set) -> int:
        """
        Find the longest consecutive sequence of characters from char_set in text.
        
        Args:
            text: Input string
            char_set: Set of characters to look for
            
        Returns:
            Length of longest sequence
        """
        max_length = 0
        current_length = 0
        
        for char in text:
            if char in char_set:
                current_length += 1
                max_length = max(max_length, current_length)
            else:
                current_length = 0
        
        return max_length
    
    def extract_all_model_features(self, domain: str) -> Dict:
        """
        Extract features and fill in defaults for all 29 model features.
        Only the important features are calculated; others get default values.
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary with all 29 features required by the model
        """
        # Extract important features
        important_features = self.extract_features(domain)
        
        # Create full feature set with defaults
        all_features = {
            'Entropy': 0.0,
            'EntropyOfSubDomains': 0.0,
            'ConsoantRatio': important_features['ConsoantRatio'],
            'NumericRatio': important_features['NumericRatio'],
            'SpecialCharRatio': 0.0,
            'VowelRatio': important_features['VowelRatio'],
            'ConsoantSequence': 0,
            'VowelSequence': 0,
            'NumericSequence': important_features['NumericSequence'],
            'SpecialCharSequence': 0,
            'DomainLength': important_features['DomainLength'],
            'SubdomainNumber': 0,
            'StrangeCharacters': important_features['StrangeCharacters'],
            'CreationDate': 0,
            'LastUpdateDate': 0,
            'ASN': 0,
            'HttpResponseCode': 0,
            'MXDnsResponse': 0,
            'TXTDnsResponse': 0,
            'HasSPFInfo': 0,
            'HasDkimInfo': 0,
            'HasDmarcInfo': 0,
            'DomainInAlexaDB': 0,
            'CommonPorts': 0,
            'IpReputation': 0,
            'DomainReputation': 0,
            'TLD': 0,
            'CountryCode': 0,
            'DNSRecordType': important_features['DNSRecordType']
        }
        
        return all_features
    
    def batch_extract(self, domains: list) -> list:
        """
        Extract features for multiple domains.
        
        Args:
            domains: List of domain names
            
        Returns:
            List of feature dictionaries
        """
        return [self.extract_all_model_features(domain) for domain in domains]


# Test the feature extractor
if __name__ == "__main__":
    extractor = DomainFeatureExtractor()
    
    # Test domains
    test_domains = [
        "google.com",
        "example123.com",
        "xk2j9m3p4q5r.com",
        "chaseyourcuriosity.com",
        "test-domain-123.net"
    ]
    
    print("="*70)
    print("FEATURE EXTRACTION TEST")
    print("="*70)
    
    for domain in test_domains:
        print(f"\nDomain: {domain}")
        print("-" * 70)
        features = extractor.extract_features(domain)
        for key, value in features.items():
            print(f"  {key:<25} {value}")
