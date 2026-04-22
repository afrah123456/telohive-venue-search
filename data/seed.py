import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Venue
from app.services.embeddings import get_embedding, get_venue_text

def seed_venues():
    """Load sample venues from JSON into the database."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Clear existing venues
        db.query(Venue).delete()
        db.commit()

        # Load JSON data
        with open("data/venues.json", "r") as f:
            venues_data = json.load(f)

        for venue_data in venues_data:
            venue = Venue(**venue_data)

            # Generate embedding
            venue_text = get_venue_text(venue)
            venue.embedding = get_embedding(venue_text)

            db.add(venue)

        db.commit()
        print(f"✅ Seeded {len(venues_data)} venues successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_venues()