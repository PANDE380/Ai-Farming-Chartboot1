# seed_data.py
from models import SessionLocal, Knowledge

db = SessionLocal()

sample_data = [
    # planting
    {
        "question": "How do I plant maize?",
        "answer": "Prepare the land, use certified seeds, plant in rows and give enough spacing 75cm.",
        "intent": "planting",
        "crop": "maize",
        "language": "english",
        "topic": "planting"
    },
    {
        "question": "When should I plant beans?",
        "answer": "Plant beans at the start of the rainy season for good soil moisture.",
        "intent": "planting",
        "crop": "beans",
        "language": "english",
        "topic": "planting"
    },

    # pests / disease
    {
        "question": "How do I control maize pests?",
        "answer": "Use pesticides like cypermethrin, practice crop rotation and remove infected plants.",
        "intent": "pest_disease",
        "crop": "maize",
        "language": "english",
        "topic": "pest control"
    },
    {
        "question": "What can I do if my chicken are dying?",
        "answer": "Provide clean water, balanced feed, vaccines and proper housing ventilation.",
        "intent": "pest_disease",
        "crop": "chicken",
        "language": "english",
        "topic": "animal health"
    },

    # fertilizer
    {
        "question": "Best fertilizer for tomatoes?",
        "answer": "Use NPK 17:17:17 during early growth and CAN during flowering.",
        "intent": "fertilizer",
        "crop": "tomato",
        "language": "english",
        "topic": "fertilizer"
    },

    # general
    {
        "question": "How do I rear chicken?",
        "answer": "Provide clean water, balanced feed, vaccines and proper housing ventilation.",
        "intent": "animal_husbandry",
        "crop": "chicken",
        "language": "english",
        "topic": "rearing"
    }
]

# insert only new entries (avoid duplicates)
for item in sample_data:
    exists = db.query(Knowledge).filter(Knowledge.question == item["question"]).first()
    if not exists:
        record = Knowledge(
            question=item["question"],
            answer=item["answer"],
            intent=item["intent"],
            crop=item["crop"],
            language=item["language"],
            topic=item["topic"]
        )
        db.add(record)

db.commit()
print("Seed data inserted/updated.")
