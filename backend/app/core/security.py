import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User

security = HTTPBearer()

# Fetched once at import time, same as the original main.py behaviour.
_openid_config = requests.get(settings.openid_config_url).json()
_jwks_uri = _openid_config["jwks_uri"]
_issuer = _openid_config["issuer"]
_jwks = requests.get(_jwks_uri).json()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        key = None
        for jwk in _jwks["keys"]:
            if jwk["kid"] == kid:
                key = {
                    "kty": jwk["kty"],
                    "kid": jwk["kid"],
                    "use": jwk["use"],
                    "n": jwk["n"],
                    "e": jwk["e"],
                }
                break

        if not key:
            raise HTTPException(status_code=401, detail="Public key not found")

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.CLIENT_ID,
            issuer=_issuer,
        )

        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def get_or_create_user(user_claims, db: Session) -> User:
    azure_id = user_claims.get("sub")
    name = user_claims.get("name", "User")
    email = (
        user_claims.get("preferred_username")
        or user_claims.get("email")
        or "unknown@example.com"
    )

    db_user = db.query(User).filter(User.azure_id == azure_id).first()

    if not db_user:
        db_user = User(
            azure_id=azure_id,
            name=name,
            email=email,
            pre_questionnaire_completed=False,
            post_questionnaire_completed=False,
            current_episode=0,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return db_user
