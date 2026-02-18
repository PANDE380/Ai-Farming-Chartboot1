# train_intent.py
"""
Train and save intent detection model (optional ML-based approach).
"""
import pickle
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from models import SessionLocal, Knowledge

def load_training_data():
    """Load question-intent pairs from database."""
    db = SessionLocal()
    try:
        rows = db.query(Knowledge).all()
        texts = [r.question for r in rows]
        labels = [r.intent or "general" for r in rows]
        return texts, labels
    finally:
        db.close()

def train_and_save(model_path="intent_model.pkl", vect_path="intent_vectorizer.pkl"):
    """Train intent classifier and save model files."""
    print("Loading training data...")
    X_texts, y = load_training_data()
    
    if not X_texts:
        print("✗ No training data found in database. Run import_dataset.py first.")
        return False
    
    print(f"✓ Loaded {len(X_texts)} training examples")
    
    try:
        print("Creating vectorizer...")
        vect = TfidfVectorizer(ngram_range=(1, 2), max_features=2000)
        X = vect.fit_transform(X_texts)
        print(f"✓ Vectorizer created with {len(vect.get_feature_names_out())} features")
        
        print("Training classifier...")
        clf = LogisticRegression(max_iter=300, random_state=42)
        clf.fit(X, y)
        print(f"✓ Model trained")
        
        print(f"Saving models...")
        with open(model_path, "wb") as f:
            pickle.dump(clf, f)
        with open(vect_path, "wb") as f:
            pickle.dump(vect, f)
        
        print(f"✓ Model saved to {model_path}")
        print(f"✓ Vectorizer saved to {vect_path}")
        return True
        
    except Exception as e:
        print(f"✗ Training failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Training Intent Detection Model...\n")
    success = train_and_save()
    sys.exit(0 if success else 1)
