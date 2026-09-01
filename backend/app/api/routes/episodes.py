from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas import EpisodeCompleteRequest, EpisodeReactionRequest, QuizResponseRequest
from app.services import episode_service
from app.services.episode_access import ensure_episode_access

router = APIRouter(tags=["episodes"])


@router.get("/episodes/{episode_number}")
def get_episode(
    episode_number: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_episode_access(user, episode_number)
    return episode_service.get_episode_detail(db, episode_number)


@router.post("/episodes/{episode_number}/start")
def start_episode(
    episode_number: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_episode_access(user, episode_number)
    episode_service.start_episode(db, user, episode_number)
    return {"message": f"Episode {episode_number} started"}


@router.post("/episodes/{episode_number}/complete")
def complete_episode(
    episode_number: int,
    data: EpisodeCompleteRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_episode_access(user, episode_number)
    advanced = episode_service.complete_episode(db, user, episode_number, data.time_spent_seconds)
    return {"message": f"Episode {episode_number} completed successfully", "advanced": advanced}


@router.post("/episodes/{episode_number}/quiz-response")
def save_quiz_response(
    episode_number: int,
    data: QuizResponseRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_episode_access(user, episode_number)
    quiz_response = episode_service.save_quiz_response(
        db, user, episode_number, data.question_text, data.response_text, data.skipped
    )
    return {
        "message": "Quiz response saved successfully",
        "response_id": quiz_response.id,
    }


@router.post("/episodes/{episode_number}/reaction")
def save_episode_reaction(
    episode_number: int,
    data: EpisodeReactionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_episode_access(user, episode_number)
    reaction = episode_service.save_episode_reaction(
        db, user, episode_number, data.emoji, data.audio_timestamp_seconds
    )
    return {
        "message": "Reaction saved successfully",
        "reaction_id": reaction.id,
        "audio_timestamp_seconds": reaction.audio_timestamp_seconds,
    }


@router.post("/upload-transcript/{episode_number}")
def upload_transcript(
    episode_number: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    episode = episode_service.upload_transcript(db, episode_number, file)
    return {
        "message": "Transcript uploaded and processed",
        "transcript_url": episode.transcript_url,
    }
