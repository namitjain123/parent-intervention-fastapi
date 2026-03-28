from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    azure_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    pre_questionnaire_completed = Column(Boolean, default=False)
    current_episode = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    progress = relationship("UserEpisodeProgress", back_populates="user")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    episode_number = Column(Integer, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    audio_url = Column(String, nullable=False)
    transcript_url = Column(String, nullable=True)
    transcript_text = Column(Text, nullable=True)
    quiz_json = Column(Text, nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    progress = relationship("UserEpisodeProgress", back_populates="episode")


class UserEpisodeProgress(Base):
    __tablename__ = "user_episode_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)

    started_at = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    time_spent_seconds = Column(Integer, default=0)

    user = relationship("User", back_populates="progress")
    episode = relationship("Episode", back_populates="progress")