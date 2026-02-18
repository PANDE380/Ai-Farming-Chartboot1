import sys
try:
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from pydantic import BaseModel
    from models import SessionLocal, Knowledge
    import re
    
    print("✓ All imports successful")
    
    # Test database
    db = SessionLocal()
    count = db.query(Knowledge).count()
    print(f"✓ Database connected: {count} entries")
    db.close()
    
    # Test search function
    def preprocess(text: str) -> str:
        text = text.lower().strip()
        return re.sub(r"[^a-zA-Z0-9\s]", "", text)
    
    def search_knowledge(question: str):
        db = SessionLocal()
        clean_q = preprocess(question)
        result = db.query(Knowledge).filter(Knowledge.question.ilike(f"%{clean_q}%")).first()
        db.close()
        return result.answer if result else None
    
    answer = search_knowledge("maize")
    if answer:
        print(f"✓ Search works: Found answer about maize")
    else:
        print("✗ Search returned no results")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
