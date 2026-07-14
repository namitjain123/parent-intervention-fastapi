from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import episode_service
from app.services.episode_access import process_delayed_survey_unlocks

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/episodes/upload")
def upload_episode(
    episode_number: int = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    quiz_json: str = Form("[]"),
    audio_file: UploadFile = File(...),
    transcript_file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    return episode_service.create_or_update_episode(
        db, episode_number, title, description, quiz_json, audio_file, transcript_file
    )


@router.post("/process-delayed-unlocks")
def admin_process_delayed_unlocks(db: Session = Depends(get_db)):
    return process_delayed_survey_unlocks(db)
