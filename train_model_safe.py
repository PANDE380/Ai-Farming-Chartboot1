#!/usr/bin/env python3
"""
Simplified intent model training (uses basic vectorizer without sklearn issues).
Falls back to keyword-based approach if sklearn has compatibility issues.
"""
import pickle
import sys
import json
from collections import defaultdict
from models import SessionLocal, Knowledge

def train_and_save_simple(model_path="intent_model.pkl", vect_path="intent_vectorizer.pkl"):
    """Train using simple keyword-based approach."""
    print("Loading training data from database...")
    db = SessionLocal()
    try:
        rows = db.query(Knowledge).all()
        training_data = [
            {"text": r.question, "intent": r.intent or "general"}
            for r in rows
        ]
        
        if not training_data:
            print("✗ No training data found in database.")
            return False
        
        print(f"✓ Loaded {len(training_data)} training examples")
        
        # Build keyword mappings
        intent_keywords = defaultdict(list)
        for item in training_data:
            words = item["text"].lower().split()
            intent_keywords[item["intent"]].extend(words)
        
        # Save models
        print("Saving models...")
        
        model_data = {
            "type": "keyword_based",
            "intents": list(set(item["intent"] for item in training_data)),
            "training_samples": len(training_data),
            "examples": training_data[:100]  # Save first 100 examples
        }
        
        with open(model_path, "wb") as f:
            pickle.dump(model_data, f)
        
        vectorizer_data = {
            "type": "intent_keywords",
            "intent_keywords": dict(intent_keywords),
            "num_features": sum(len(v) for v in intent_keywords.values())
        }
        
        with open(vect_path, "wb") as f:
            pickle.dump(vectorizer_data, f)
        
        print(f"✓ Model saved to {model_path}")
        print(f"✓ Vectorizer saved to {vect_path}")
        print(f"✓ Trained on intents: {', '.join(model_data['intents'])}")
        return True
        
    except Exception as e:
        print(f"✗ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def try_sklearn_training(model_path="intent_model.pkl", vect_path="intent_vectorizer.pkl"):
    """Try to train with sklearn if available."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        
        print("Using scikit-learn for training...")
        
        db = SessionLocal()
        try:
            rows = db.query(Knowledge).all()
            X_texts = [r.question for r in rows]
            y = [r.intent or "general" for r in rows]
            
            if not X_texts:
                print("✗ No training data found.")
                return False
            
            print(f"✓ Loaded {len(X_texts)} examples")
            print("Creating vectorizer...")
            
            vect = TfidfVectorizer(ngram_range=(1, 2), max_features=2000)
            X = vect.fit_transform(X_texts)
            print(f"✓ Vectorizer created with {len(vect.get_feature_names_out())} features")
            
            print("Training classifier...")
            clf = LogisticRegression(max_iter=300, random_state=42)
            clf.fit(X, y)
            print(f"✓ Model trained on {len(set(y))} intents")
            
            print("Saving models...")
            with open(model_path, "wb") as f:
                pickle.dump(clf, f)
            with open(vect_path, "wb") as f:
                pickle.dump(vect, f)
            
            print(f"✓ Model saved to {model_path}")
            print(f"✓ Vectorizer saved to {vect_path}")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"⚠ Scikit-learn training failed ({type(e).__name__})")
        print(f"  Falling back to keyword-based approach...")
        return None

if __name__ == "__main__":
    print("🤖 Training Intent Detection Model...\n")
    
    # Try sklearn first
    result = try_sklearn_training()
    
    # If sklearn fails or is not available, use simple approach
    if result is None or result is False:
        print()
        result = train_and_save_simple()
    
    if result:
        print("\n✅ Model training complete!")
    else:
        print("\n✗ Model training failed!")
    
    sys.exit(0 if result else 1)
