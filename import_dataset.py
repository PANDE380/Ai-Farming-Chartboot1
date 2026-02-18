"""
Import farming FAQ dataset into the database.
"""
import csv
import os
from models import Knowledge, SessionLocal

def import_dataset(csv_file: str = "a sample_Farming_FAQ_Assistant_Dataset.csv"):
    """Import CSV dataset into the knowledge database."""
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found")
        return False
    
    db = SessionLocal()
    try:
        count_before = db.query(Knowledge).count()
        
        with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            
            if not reader.fieldnames:
                print("Error: CSV file is empty or malformed")
                return False
            
            added = 0
            for i, row in enumerate(reader, 1):
                try:
                    question = row.get("Question", "").lower().strip()
                    answer = row.get("Answer", "").strip()
                    
                    if not question or not answer:
                        print(f"⚠ Row {i}: Skipping - missing question or answer")
                        continue
                    
                    # Check for duplicates
                    existing = db.query(Knowledge).filter(
                        Knowledge.question.ilike(question)
                    ).first()
                    
                    if existing:
                        print(f"⚠ Row {i}: Duplicate entry skipped")
                        continue
                    
                    knowledge = Knowledge(
                        question=question,
                        answer=answer,
                        intent="general",
                        crop=None,
                        language="english",
                        topic=None
                    )
                    db.add(knowledge)
                    added += 1
                    
                    if added % 50 == 0:
                        print(f"  Processing... {added} entries added")
                
                except Exception as e:
                    print(f"⚠ Row {i}: Error - {e}")
                    continue
        
        db.commit()
        count_after = db.query(Knowledge).count()
        
        print(f"\n✓ Dataset import successful!")
        print(f"  Added: {added} new entries")
        print(f"  Total in database: {count_after}")
        return True
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Importing farming dataset...")
    success = import_dataset()
    exit(0 if success else 1)
