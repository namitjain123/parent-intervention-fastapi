from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas import CompletePreQRequest, ParticipantOnlyRequest
from app.services import questionnaire_service

router = APIRouter(tags=["questionnaires"])


@router.post("/mark-prequestionnaire-complete")
def mark_prequestionnaire_complete(
    data: CompletePreQRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    print("DATA RECEIVED:", data)

    db_user = questionnaire_service.complete_pre_questionnaire(
        db, data.participant_id, data.grade, data.teacher, background_tasks
    )

    return {
        "message": "Pre-questionnaire marked complete",
        "user_class": db_user.user_class,
        "grade": db_user.grade,
        "teacher_name": db_user.teacher_name,
        "delayed_survey_unlocked": db_user.delayed_survey_unlocked,
        "delayed_survey_completed": db_user.delayed_survey_completed,
        "delayed_unlock_at": db_user.delayed_unlock_at,
        "current_episode": db_user.current_episode,
    }


@router.post("/mark-delayed-survey-complete")
def mark_delayed_survey_complete(
    data: ParticipantOnlyRequest, db: Session = Depends(get_db)
):
    db_user = questionnaire_service.complete_delayed_survey(db, data.participant_id)

    return {
        "message": "Delayed survey marked complete",
        "current_episode": db_user.current_episode,
        "delayed_survey_completed": db_user.delayed_survey_completed,
    }


@router.post("/mark-postquestionnaire-complete")
def mark_postquestionnaire_complete(
    data: ParticipantOnlyRequest, db: Session = Depends(get_db)
):
    questionnaire_service.complete_post_questionnaire(db, data.participant_id)
    return {"message": "Post-questionnaire marked complete"}


@router.get("/survey-access-status")
def survey_access_status(user: User = Depends(get_current_user)):
    return questionnaire_service.get_survey_access_status(user)
