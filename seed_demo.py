#!/usr/bin/env python3
"""Create demo users and sample knowledge base entries for testing."""

from models import SessionLocal, User, Knowledge
import hashlib

def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

def seed_demo_data():
    db = SessionLocal()
    try:
        # Create demo user if not exists
        demo_user = db.query(User).filter(User.username == "demo").first()
        if not demo_user:
            demo = User(
                username="demo",
                email="demo@farming.ai",
                password=hash_password("demo123"),
                role="farmer"
            )
            db.add(demo)
            print("✓ Created demo user (username: demo, password: demo123)")
        
        # Create admin user if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin = User(
                username="admin",
                email="admin@farming.ai",
                password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin)
            print("✓ Created admin user (username: admin, password: admin123)")
        
        db.commit()
        
        # Add sample knowledge base entries
        sample_kb = [
            {
                "question": "What are common crop diseases I should watch for?",
                "answer": "Common crop diseases include: 1) Early/Late Blight in potatoes, 2) Powdery Mildew in various crops, 3) Root Rot in beans, 4) Leaf Spot in tomatoes, 5) Rust in small grains. Regular scouting and proper spacing help with prevention.",
                "intent": "disease",
                "crop": "general"
            },
            {
                "question": "How do I know if my crops have nutrient deficiency?",
                "answer": "Signs of nutrient deficiency: Nitrogen deficiency shows yellowing leaves, Phosphorus deficiency shows purple coloring, Potassium deficiency shows brown leaf edges. Get a soil test to determine exact deficiencies and apply appropriate fertilizer.",
                "intent": "fertilizer",
                "crop": "general"
            },
            {
                "question": "How often should I water my crops?",
                "answer": "Water requirements depend on crop type and soil moisture. Most crops need 1-2 inches per week. Water deeply but less frequently to encourage deep root growth. Check soil moisture 4 inches deep - if dry, it's time to water. Avoid watering in hot sun.",
                "intent": "irrigation",
                "crop": "general"
            },
            {
                "question": "When is the best time to harvest crops?",
                "answer": "Harvest timing varies by crop: Grains should be at boot stage, Tomatoes when fully colored, Beans when pods are firm, Root vegetables when mature size, Leafy greens before bolting. Early morning harvesting usually provides best quality.",
                "intent": "harvest",
                "crop": "general"
            },
            {
                "question": "How does weather affect crop yields?",
                "answer": "Weather significantly impacts yields: Temperature affects growth rates and crop maturity, Rainfall affects irrigation needs and disease pressure, Frost can damage sensitive crops, Wind can cause physical damage and water loss, Humidity promotes fungal diseases. Monitor weather forecasts for optimal timing.",
                "intent": "weather",
                "crop": "general"
            },
        ]
        
        # Add knowledge entries if they don't exist
        for entry in sample_kb:
            existing = db.query(Knowledge).filter(Knowledge.question == entry["question"]).first()
            if not existing:
                kb = Knowledge(
                    question=entry["question"],
                    answer=entry["answer"],
                    intent=entry.get("intent", "general"),
                    crop=entry.get("crop", None),
                    language="english"
                )
                db.add(kb)
        
        db.commit()
        print("✓ Added sample knowledge base entries")
        
    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()
    print("\n✓ Demo data seeding complete!")
