from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Episode, User
from app.services.activity_service import update_user_activity
from app.services.user_service import get_dashboard_payload, get_profile_payload

router = APIRouter(tags=["users"])


@router.get("/me")
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    update_user_activity(user, db)
    return get_profile_payload(user)


@router.get("/dashboard")
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    all_episodes = (
        db.query(Episode)
        .filter(Episode.is_published == True)
        .order_by(Episode.episode_number)
        .all()
    )
    return get_dashboard_payload(user, all_episodes)
