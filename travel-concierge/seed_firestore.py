"""
Firestore seed script for Travel Concierge agent.
Hardcodes GCP Project ID: 'qwiklabs-gcp-02-9a8f822bd17b'
"""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-02-9a8f822bd17b"
COLLECTION_NAME = "destinations"

SEED_DESTINATIONS = [
    {
        "id": "kyoto",
        "name": "Kyoto, Japan",
        "description": "Ancient capital famous for historic Buddhist temples, traditional wooden houses, and cherry blossoms.",
        "category": "Cultural & Historic",
        "average_cost_per_day": 180,
        "popular_activities": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji Temple"],
        "best_season": "Spring & Autumn",
    },
    {
        "id": "cape_town",
        "name": "Cape Town, South Africa",
        "description": "Coastal city known for dramatic mountain landscapes, pristine beaches, and vibrant harbor life.",
        "category": "Nature & Adventure",
        "average_cost_per_day": 140,
        "popular_activities": ["Table Mountain Hike", "Cape Point Tour", "Boulders Beach Penguins"],
        "best_season": "November to March",
    },
    {
        "id": "paris",
        "name": "Paris, France",
        "description": "Global center for art, fashion, gastronomy, and iconic architectural landmarks.",
        "category": "Urban & Culinary",
        "average_cost_per_day": 230,
        "popular_activities": ["Eiffel Tower", "Louvre Museum", "Seine River Cruise"],
        "best_season": "May to September",
    },
    {
        "id": "reykjavik",
        "name": "Reykjavik, Iceland",
        "description": "Gateway to volcanic landscapes, geothermal springs, and stunning Northern Lights.",
        "category": "Nature & Adventure",
        "average_cost_per_day": 250,
        "popular_activities": ["Golden Circle Tour", "Blue Lagoon Spa", "Northern Lights Hunting"],
        "best_season": "September to April",
    },
]


def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    print(f"Seeding '{COLLECTION_NAME}' in project '{PROJECT_ID}'...")
    for item in SEED_DESTINATIONS:
        doc_ref = collection.document(item["id"])
        doc_ref.set(item)
        print(f"  - Seeded destination: {item['name']} (ID: {item['id']})")

    print(f"✅ Successfully seeded {len(SEED_DESTINATIONS)} destinations into Firestore.")


if __name__ == "__main__":
    seed_database()
