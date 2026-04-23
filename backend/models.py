from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    azure_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    pre_questionnaire_completed = Column(Boolean, default=False)
    post_questionnaire_completed = Column(Boolean, default=False)
    current_episode = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_activity_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_reminder_sent_at = Column(DateTime, nullable=True)
    reminder_count = Column(Integer, default=0)
    midway_reminder_sent_at = Column(DateTime, nullable=True)
    
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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

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


class UserQuizResponse(Base):
    __tablename__ = "user_quiz_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)

    question_text = Column(Text, nullable=True)
    response_text = Column(Text, nullable=True)
    skipped = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserEpisodeReaction(Base):
    __tablename__ = "user_episode_reactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)

    emoji = Column(String, nullable=False)
    audio_timestamp_seconds = Column(Integer, nullable=False)   # new
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))