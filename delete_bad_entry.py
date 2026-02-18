from models import SessionLocal, Knowledge

db = SessionLocal()

# Find and delete entries with "crops are plants"
entries = db.query(Knowledge).filter(Knowledge.answer.ilike("%crops are plants%")).all()

if entries:
    for entry in entries:
        print(f"Deleting: Q='{entry.question}' | A='{entry.answer[:50]}...'")
        db.delete(entry)
    db.commit()
    print(f"✓ Deleted {len(entries)} entry/entries")
else:
    print("No entries found with 'crops are plants'")

db.close()
