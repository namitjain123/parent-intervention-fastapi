from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import verify_token, get_or_create_user
from app.db.session import get_db
from app.models import User


def get_current_user(
    user_claims: dict = Depends(verify_token),
    db: Session = Depends(get_db),
) -> User:
    return get_or_create_user(user_claims, db)
