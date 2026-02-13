"""
Malicious Domain Classifier - Inference Module
This module provides a simple interface to use the trained malicious domain detection model.

Usage:
    from domain_classifier import DomainClassifier
    
    # Initialize classifier with saved model
    classifier = DomainClassifier('saved_models/malicious_domain_model_XXXXXX.joblib')
    
    # Predict a single domain
    result = classifier.predict(domain_features)
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']:.2%}")
    
    # Predict multiple domains
    results = classifier.predict_batch(list_of_features)
"""

import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict, List, Union


class DomainClassifier:
    """
    A classifier for detecting malicious domains using a pre-trained model.
    """
    
    def __init__(self, model_path: str):
        """
        Initialize the classifier with a saved model.
        
        Args:
            model_path: Path to the saved model file (.joblib)
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model package
        print(f"Loading model from: {model_path}")
        self.model_package = joblib.load(model_path)
        
        self.model = self.model_package['model']
        self.label_encoders = self.model_package['label_encoders']
        self.feature_names = self.model_package['feature_names']
        self.metadata = self.model_package['metadata']
        
        print(f"✓ Model loaded successfully")
        print(f"  Model Type: {self.metadata['model_type']}")
        print(f"  Created: {self.metadata['created_at']}")
        print(f"  Test Accuracy: {self.metadata['test_accuracy']:.4f}")
        print(f"  Test AUC-ROC: {self.metadata['test_auc']:.4f}")
    
    
    def get_required_features(self) -> List[str]:
        """
        Get the list of required features for prediction.
        
        Returns:
            List of feature names
        """
        return self.feature_names
    
    
    def get_model_info(self) -> Dict:
        """
        Get model metadata information.
        
        Returns:
            Dictionary containing model metadata
        """
        return self.metadata
    
    
    def _validate_features(self, features: Dict) -> None:
        """
        Validate that all required features are present.
        
        Args:
            features: Dictionary of feature values
        
        Raises:
            ValueError: If required features are missing
        """
        missing_features = set(self.feature_names) - set(features.keys())
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
    
    
    def predict(self, features: Dict) -> Dict:
        """
        Predict if a domain is malicious or benign.
        
        Args:
            features: Dictionary containing all required features
                Example:
                {
                    'Entropy': 4.5,
                    'EntropyOfSubDomains': 0,
                    'ConsoantRatio': 0.6,
                    'NumericRatio': 0.1,
                    ...
                }
        
        Returns:
            Dictionary containing:
                - prediction: 'malicious' or 'benign'
                - prediction_label: 1 or 0
                - confidence: probability of the predicted class
                - probabilities: {'benign': float, 'malicious': float}
        """
        # Validate features
        self._validate_features(features)
        
        # Create DataFrame
        X = pd.DataFrame([features])[self.feature_names]
        
        # Make prediction
        prediction_label = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Prepare result
        result = {
            'prediction': 'malicious' if prediction_label == 1 else 'benign',
            'prediction_label': int(prediction_label),
            'confidence': float(probabilities[prediction_label]),
            'probabilities': {
                'benign': float(probabilities[0]),
                'malicious': float(probabilities[1])
            }
        }
        
        return result
    
    
    def predict_batch(self, features_list: List[Dict]) -> List[Dict]:
        """
        Predict multiple domains at once.
        
        Args:
            features_list: List of feature dictionaries
        
        Returns:
            List of prediction result dictionaries
        """
        results = []
        for features in features_list:
            try:
                result = self.predict(features)
                results.append(result)
            except Exception as e:
                results.append({
                    'prediction': 'error',
                    'prediction_label': -1,
                    'confidence': 0.0,
                    'probabilities': {'benign': 0.0, 'malicious': 0.0},
                    'error': str(e)
                })
        
        return results
    
    
    def predict_proba(self, features: Dict) -> np.ndarray:
        """
        Get prediction probabilities for both classes.
        
        Args:
            features: Dictionary containing all required features
        
        Returns:
            NumPy array with [benign_probability, malicious_probability]
        """
        self._validate_features(features)
        X = pd.DataFrame([features])[self.feature_names]
        return self.model.predict_proba(X)[0]
    
    
    def get_feature_importance(self, top_n: int = 15) -> pd.DataFrame:
        """
        Get the most important features used by the model.
        
        Args:
            top_n: Number of top features to return
        
        Returns:
            DataFrame with features and their importance scores
        """
        if not hasattr(self.model, 'feature_importances_'):
            raise AttributeError("Model does not support feature importance")
        
        feature_importance = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': self.model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        return feature_importance.head(top_n)


def create_feature_template() -> Dict:
    """
    Create a template dictionary with all required features.
    Fill in the values based on your domain analysis.
    
    Returns:
        Dictionary with all feature names initialized to 0
    """
    template = {
        # Entropy Features
        'Entropy': 0.0,
        'EntropyOfSubDomains': 0.0,
        
        # Character Composition Features
        'ConsoantRatio': 0.0,  # Note: Typo in original dataset
        'NumericRatio': 0.0,
        'SpecialCharRatio': 0.0,
        'VowelRatio': 0.0,
        'StrangeCharacters': 0,
        
        # Sequence Features
        'ConsoantSequence': 0,  # Note: Typo in original dataset
        'VowelSequence': 0,
        'NumericSequence': 0,
        'SpecialCharSequence': 0,
        
        # Domain Structure Features
        'DomainLength': 0,
        'SubdomainNumber': 0,
        
        # DNS & Security Features
        'MXDnsResponse': 0,
        'TXTDnsResponse': 0,
        'HasSPFInfo': 0,
        'HasDkimInfo': 0,
        'HasDmarcInfo': 0,
        
        # Infrastructure Features
        'DomainInAlexaDB': 0,
        'CommonPorts': 0,
        'HttpResponseCode': 0,
        
        # Reputation & Registration Features
        'IpReputation': 0,
        'DomainReputation': 0,
        'CreationDate': 0,
        'LastUpdateDate': 0,
        'ASN': 0,
        'CountryCode': 0,
        
        # TLD and DNS Record Type
        'TLD': 0,
        'DNSRecordType': 0
    }
    
    return template


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("DOMAIN CLASSIFIER - INFERENCE MODULE")
    print("="*60)
    
    # Find the most recent model in saved_models directory
    saved_models_dir = 'saved_models'
    
    if os.path.exists(saved_models_dir):
        model_files = [f for f in os.listdir(saved_models_dir) if f.endswith('.joblib')]
        
        if model_files:
            # Get the most recent model
            model_files.sort(reverse=True)
            model_path = os.path.join(saved_models_dir, model_files[0])
            
            # Initialize classifier
            print(f"\nInitializing classifier with: {model_path}\n")
            classifier = DomainClassifier(model_path)
            
            # Show required features
            print("\n" + "="*60)
            print("REQUIRED FEATURES")
            print("="*60)
            print(f"Total features required: {len(classifier.get_required_features())}")
            print("\nFeature names:")
            for i, feature in enumerate(classifier.get_required_features(), 1):
                print(f"  {i:2d}. {feature}")
            
            # Show feature importance
            print("\n" + "="*60)
            print("TOP 10 MOST IMPORTANT FEATURES")
            print("="*60)
            print(classifier.get_feature_importance(top_n=10).to_string(index=False))
            
            # Example prediction
            print("\n" + "="*60)
            print("EXAMPLE PREDICTION")
            print("="*60)
            
            # Create example features (suspicious domain characteristics)
            example_features = create_feature_template()
            example_features.update({
                'Entropy': 4.5,
                'DomainLength': 120,
                'StrangeCharacters': 15,
                'ConsoantSequence': 8,
                'NumericRatio': 0.3,
                'DomainInAlexaDB': 0,
                'HasSPFInfo': 0,
                'HasDkimInfo': 0,
                'HasDmarcInfo': 0
            })
            
            # Make prediction
            result = classifier.predict(example_features)
            
            print(f"\nPrediction: {result['prediction'].upper()}")
            print(f"Confidence: {result['confidence']:.2%}")
            print(f"\nProbabilities:")
            print(f"  - Benign: {result['probabilities']['benign']:.2%}")
            print(f"  - Malicious: {result['probabilities']['malicious']:.2%}")
            
            print("\n" + "="*60)
            print("USAGE IN YOUR PROJECT")
            print("="*60)
            print("\n1. Import the classifier:")
            print("   from domain_classifier import DomainClassifier, create_feature_template")
            print("\n2. Initialize with your model:")
            print("   classifier = DomainClassifier('path/to/model.joblib')")
            print("\n3. Prepare features:")
            print("   features = create_feature_template()")
            print("   features['Entropy'] = 4.5")
            print("   features['DomainLength'] = 120")
            print("   # ... set other features ...")
            print("\n4. Make prediction:")
            print("   result = classifier.predict(features)")
            print("   print(result['prediction'], result['confidence'])")
            
        else:
            print("\n✗ No saved models found in 'saved_models' directory")
            print("  Please train a model first by running malicious_domain_detector.py")
    else:
        print("\n✗ 'saved_models' directory not found")
        print("  Please train a model first by running malicious_domain_detector.py")
