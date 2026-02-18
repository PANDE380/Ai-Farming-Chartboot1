import csv
from models import Knowledge, SessionLocal

db = SessionLocal()

# Import the professional farming dataset
with open("professional_farming_dataset.csv", "r", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    
    count = 0
    for row in reader:
        # Skip if question is empty
        if not row.get("Question", "").strip():
            continue
        
        # Check if this question already exists in database
        existing = db.query(Knowledge).filter(
            Knowledge.question == row["Question"].lower().strip()
        ).first()
        
        if existing:
            print(f"Skipping duplicate: {row['Question'][:50]}...")
            continue
        
        knowledge = Knowledge(
            question=row["Question"].lower().strip(),
            answer=row["Answer"].strip(),
            intent="general",
            crop=None,
            language="english",
            topic=None
        )
        
        db.add(knowledge)
        count += 1
    
    db.commit()

print(f"✓ PROFESSIONAL DATASET IMPORTED SUCCESSFULLY!")
print(f"✓ Added {count} new Q&A pairs to the database")
print(f"✓ Your chatbot now has comprehensive farming knowledge including:")
print(f"  - Crop management (maize, beans, tomato, cassava)")
print(f"  - Pest and disease control")
print(f"  - Soil and water management")
print(f"  - Livestock management")
print(f"  - Conversational responses for natural interaction")
