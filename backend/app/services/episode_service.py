import json
import os
import shutil
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Episode, User, UserEpisodeProgress, UserEpisodeReaction, UserQuizResponse
from app.services.blob_service import upload_file_to_blob
from app.services.transcript_service import extract_text_from_docx


def get_episode_or_404(db: Session, episode_number: int) -> Episode:
    episode = db.query(Episode).filter(Episode.episode_number == episode_number).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


def _get_progress(db: Session, user: User, episode: Episode) -> UserEpisodeProgress | None:
    return (
        db.query(UserEpisodeProgress)
        .filter(
            UserEpisodeProgress.user_id == user.id,
            UserEpisodeProgress.episode_id == episode.id,
        )
        .first()
    )


def get_episode_detail(db: Session, episode_number: int) -> dict:
    episode = get_episode_or_404(db, episode_number)

    quiz_data = []
    transcript_data = []

    if episode.quiz_json:
        try:
            quiz_data = json.loads(episode.quiz_json)
        except json.JSONDecodeError:
            quiz_data = []

    if episode.transcript_text:
        try:
            transcript_data = json.loads(episode.transcript_text)
        except json.JSONDecodeError:
            transcript_data = []

    return {
        "episode_number": episode.episode_number,
        "title": episode.title,
        "description": episode.description,
        "audio_url": episode.audio_url,
        "transcript_url": episode.transcript_url,
        "transcript": transcript_data,
        "quiz": quiz_data,
    }


def start_episode(db: Session, user: User, episode_number: int) -> None:
    episode = get_episode_or_404(db, episode_number)
    progress = _get_progress(db, user, episode)

    now = datetime.now(timezone.utc)

    if not progress:
        progress = UserEpisodeProgress(
            user_id=user.id,
            episode_id=episode.id,
            started_at=now,
            completed=False,
            time_spent_seconds=0,
        )
        db.add(progress)
    elif not progress.started_at:
        progress.started_at = now

    db.commit()


def complete_episode(db: Session, user: User, episode_number: int, time_spent_seconds: int) -> bool:
    """
    Mark an episode complete. Returns True if this call advanced the
    participant's progress (a genuine first-time completion), or False if it
    was a review visit to an already-completed episode - in which case
    progress metrics and current_episode are left untouched, preserving the
    original completion data for research purposes.
    """
    if episode_number > user.current_episode:
        raise HTTPException(status_code=400, detail="Episode is locked")

    if episode_number < user.current_episode:
        return False

    episode = get_episode_or_404(db, episode_number)
    progress = _get_progress(db, user, episode)

    now = datetime.now(timezone.utc)

    if not progress:
        progress = UserEpisodeProgress(
            user_id=user.id,
            episode_id=episode.id,
            started_at=now,
            completed=True,
            completed_at=now,
            time_spent_seconds=time_spent_seconds,
        )
        db.add(progress)
    else:
        progress.completed = True
        progress.completed_at = now
        progress.time_spent_seconds = time_spent_seconds

    user.current_episode += 1

    # 8 matches the "all_episodes_completed" threshold in user_service.py.
    if user.current_episode > 8 and not user.all_episodes_completed_at:
        user.all_episodes_completed_at = now

    db.commit()
    return True


def save_quiz_response(
    db: Session, user: User, episode_number: int,
    question_text: str | None, response_text: str | None, skipped: bool,
) -> UserQuizResponse:
    episode = get_episode_or_404(db, episode_number)

    quiz_response = UserQuizResponse(
        user_id=user.id,
        episode_id=episode.id,
        question_text=question_text,
        response_text=response_text,
        skipped=skipped,
    )

    db.add(quiz_response)
    db.commit()
    db.refresh(quiz_response)
    return quiz_response


def save_episode_reaction(
    db: Session, user: User, episode_number: int, emoji: str, audio_timestamp_seconds: int,
) -> UserEpisodeReaction:
    episode = get_episode_or_404(db, episode_number)

    reaction = UserEpisodeReaction(
        user_id=user.id,
        episode_id=episode.id,
        emoji=emoji,
        audio_timestamp_seconds=audio_timestamp_seconds,
    )

    db.add(reaction)
    db.commit()
    db.refresh(reaction)
    return reaction


def upload_transcript(db: Session, episode_number: int, file: UploadFile) -> Episode:
    episode = get_episode_or_404(db, episode_number)

    temp_path = os.path.join(settings.UPLOAD_DIR, f"temp_{file.filename}")

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.endswith(".docx"):
        transcript_text = extract_text_from_docx(temp_path)
    elif file.filename.endswith(".txt"):
        with open(temp_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()
    else:
        raise HTTPException(
            status_code=400,
            detail="Only .docx or .json transcript files are supported",
        )

    episode.transcript_text = transcript_text
    episode.transcript_url = upload_file_to_blob(
        transcript_text.encode("utf-8"),
        f"transcript_{episode_number}.txt",
        "text/plain"
    )

    db.commit()
    return episode


def create_or_update_episode(
    db: Session,
    episode_number: int,
    title: str,
    description: str,
    quiz_json: str,
    audio_file: UploadFile,
    transcript_file: UploadFile | None,
) -> dict:
    try:
        parsed_quiz = json.loads(quiz_json)

        if not isinstance(parsed_quiz, list):
            raise ValueError("quiz_json must be a list")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid quiz_json format")

    filename = f"episode_{episode_number}_{audio_file.filename}"
    audio_url = upload_file_to_blob(
        audio_file.file,
        filename,
        audio_file.content_type
    )

    transcript_url = None
    transcript_text = None

    if transcript_file:
        transcript_filename = f"episode_{episode_number}_{transcript_file.filename}"
        transcript_bytes = transcript_file.file.read()

        transcript_url = upload_file_to_blob(
            transcript_bytes,
            transcript_filename,
            transcript_file.content_type
        )

        transcript_path = os.path.join(
            settings.UPLOAD_DIR,
            transcript_filename
        )

        with open(transcript_path, "wb") as buffer:
            buffer.write(transcript_bytes)

        if transcript_file.filename.endswith(".docx"):
            transcript_text = extract_text_from_docx(transcript_path)
        elif transcript_file.filename.endswith(".json"):
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript_text = f.read()
        else:
            raise HTTPException(
                status_code=400,
                detail="Only .docx or .txt transcript files are supported",
            )

    existing = db.query(Episode).filter(Episode.episode_number == episode_number).first()

    if existing:
        existing.title = title
        existing.description = description
        existing.audio_url = audio_url
        existing.transcript_url = transcript_url
        existing.transcript_text = transcript_text
        existing.quiz_json = json.dumps(parsed_quiz)
        existing.is_published = True
    else:
        db.add(Episode(
            episode_number=episode_number,
            title=title,
            description=description,
            audio_url=audio_url,
            transcript_url=transcript_url,
            transcript_text=transcript_text,
            quiz_json=json.dumps(parsed_quiz),
            is_published=True,
        ))

    db.commit()

    return {
        "message": "Episode uploaded successfully",
        "audio_url": audio_url,
        "transcript_url": transcript_url,
        "quiz_count": len(parsed_quiz),
    }
