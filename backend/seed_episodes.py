"""
Run once to seed test episodes into the local SQLite database.

    venv\\Scripts\\activate
    python seed_episodes.py
"""

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Episode

Base.metadata.create_all(bind=engine)

EPISODES = [
    {"episode_number": 1, "title": "Episode 1: Getting Started", "description": "Introduction to the program.", "audio_url": "https://example.com/ep1.mp3"},
    {"episode_number": 2, "title": "Episode 2: Building Connections", "description": "Learn about building strong connections.", "audio_url": "https://example.com/ep2.mp3"},
    {"episode_number": 3, "title": "Episode 3: Communication", "description": "Effective communication strategies.", "audio_url": "https://example.com/ep3.mp3"},
    {"episode_number": 4, "title": "Episode 4: Boundaries", "description": "Setting healthy boundaries.", "audio_url": "https://example.com/ep4.mp3"},
    {"episode_number": 5, "title": "Episode 5: Routines", "description": "Creating positive routines.", "audio_url": "https://example.com/ep5.mp3"},
    {"episode_number": 6, "title": "Episode 6: Emotions", "description": "Managing emotions together.", "audio_url": "https://example.com/ep6.mp3"},
    {"episode_number": 7, "title": "Episode 7: Problem Solving", "description": "Collaborative problem solving.", "audio_url": "https://example.com/ep7.mp3"},
    {"episode_number": 8, "title": "Episode 8: Wrap Up", "description": "Reflecting on your journey.", "audio_url": "https://example.com/ep8.mp3"},
]

db = SessionLocal()

for ep in EPISODES:
    exists = db.query(Episode).filter(Episode.episode_number == ep["episode_number"]).first()
    if not exists:
        db.add(Episode(**ep, is_published=True))
        print(f"Added Episode {ep['episode_number']}")
    else:
        print(f"Episode {ep['episode_number']} already exists, skipping")

db.commit()
db.close()
print("Done.")
