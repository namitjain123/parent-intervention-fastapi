import os
import json
import shutil
import requests
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session
from utils.activity import update_user_activity
from database import Base, engine, get_db
from models import (
    User,
    Episode,
    UserEpisodeProgress,
    UserQuizResponse,
    UserEpisodeReaction,
)
from schemas import (
    CompletePreQRequest,
    EpisodeCompleteRequest,
    QuizResponseRequest,
    EpisodeReactionRequest,
)
from blob_service import upload_audio_file
from utils.transcript_utils import extract_text_from_docx

load_dotenv()

app = FastAPI()
security = HTTPBearer()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

OPENID_CONFIG_URL = (
    f"https://parentingplatform.ciamlogin.com/"
    f"{TENANT_ID}/v2.0/.well-known/openid-configuration"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

openid_config = requests.get(OPENID_CONFIG_URL).json()
jwks_uri = openid_config["jwks_uri"]
issuer = openid_config["issuer"]
jwks = requests.get(jwks_uri).json()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        key = None
        for jwk in jwks["keys"]:
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
            audience=CLIENT_ID,
            issuer=issuer,
        )
        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def get_or_create_user(user_claims, db: Session):
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


@app.get("/test")
def test():
    return {"message": "Backend reachable"}


@app.get("/me")
def get_me(user=Depends(verify_token), db: Session = Depends(get_db)):
    db_user = get_or_create_user(user, db)
    update_user_activity(db_user, db)
    return {
        "id": db_user.id,
        "azure_id": db_user.azure_id,
        "name": db_user.name,
        "email": db_user.email,
        "pre_questionnaire_completed": db_user.pre_questionnaire_completed,
        "post_questionnaire_completed": db_user.post_questionnaire_completed,
        "current_episode": db_user.current_episode,
    }


@app.get("/dashboard")
def get_dashboard(user=Depends(verify_token), db: Session = Depends(get_db)):
    db_user = get_or_create_user(user, db)

    all_episodes = (
        db.query(Episode)
        .filter(Episode.is_published == True)
        .order_by(Episode.episode_number)
        .all()
    )

    episodes = []
    for ep in all_episodes:
        if not db_user.pre_questionnaire_completed:
            status = "locked"
        elif ep.episode_number < db_user.current_episode:
            status = "completed"
        elif ep.episode_number == db_user.current_episode:
            status = "unlocked"
        else:
            status = "locked"

        episodes.append(
            {
                "episode_number": ep.episode_number,
                "title": ep.title,
                "description": ep.description,
                "audio_url": ep.audio_url,
                "status": status,
            }
        )

    all_episodes_completed = db_user.current_episode > 3

    return {
        "name": db_user.name,
        "email": db_user.email,
        "pre_questionnaire_completed": db_user.pre_questionnaire_completed,
        "post_questionnaire_completed": db_user.post_questionnaire_completed,
        "current_episode": db_user.current_episode,
        "all_episodes_completed": all_episodes_completed,
        "episodes": episodes,
    }


@app.post("/mark-prequestionnaire-complete")
def mark_prequestionnaire_complete(
    data: CompletePreQRequest, db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.azure_id == data.participant_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.pre_questionnaire_completed = True

    if db_user.current_episode == 0:
        db_user.current_episode = 1

    db.commit()

    return {"message": "Pre-questionnaire marked complete"}


@app.post("/mark-postquestionnaire-complete")
def mark_postquestionnaire_complete(
    data: CompletePreQRequest, db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.azure_id == data.participant_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.post_questionnaire_completed = True
    db.commit()

    return {"message": "Post-questionnaire marked complete"}


@app.get("/episodes/{episode_number}")
def get_episode(
    episode_number: int,
    user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    db_user = get_or_create_user(user, db)

    if not db_user.pre_questionnaire_completed:
        raise HTTPException(
            status_code=403, detail="Complete pre-questionnaire first"
        )

    if episode_number > db_user.current_episode:
        raise HTTPException(status_code=403, detail="Episode is locked")

    episode = db.query(Episode).filter(Episode.episode_number == episode_number).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    quiz_data = []
    if episode.quiz_json:
        try:
            quiz_data = json.loads(episode.quiz_json)
        except json.JSONDecodeError:
            quiz_data = []

    return {
        "episode_number": episode.episode_number,
        "title": episode.title,
        "description": episode.description,
        "audio_url": episode.audio_url,
        "transcript_url": episode.transcript_url,
        "transcript_text": episode.transcript_text or "",
        "quiz": quiz_data,
    }


@app.post("/episodes/{episode_number}/start")
def start_episode(
    episode_number: int,
    user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    db_user = get_or_create_user(user, db)

    if not db_user.pre_questionnaire_completed:
        raise HTTPException(
            status_code=400, detail="Complete pre-questionnaire first"
        )

    if episode_number > db_user.current_episode:
        raise HTTPException(status_code=400, detail="Episode is locked")

    episode = db.query(Episode).filter(Episode.episode_number == episode_number).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    progress = (
        db.query(UserEpisodeProgress)
        .filter(
            UserEpisodeProgress.user_id == db_user.id,
            UserEpisodeProgress.episode_id == episode.id,
        )
        .first()
    )

    if not progress:
        progress = UserEpisodeProgress(
            user_id=db_user.id,
            episode_id=episode.id,
            started_at=datetime.utcnow(),
            completed=False,
            time_spent_seconds=0,
        )
        db.add(progress)
    else:
        if not progress.started_at:
            progress.started_at = datetime.utcnow()

    db.commit()

    return {"message": f"Episode {episode_number} started"}


@app.post("/episodes/{episode_number}/complete")
def complete_episode(
    episode_number: int,
    data: EpisodeCompleteRequest,
    user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    db_user = get_or_create_user(user, db)

    if not db_user.pre_questionnaire_completed:
        raise HTTPException(
            status_code=400, detail="Complete pre-questionnaire first"
        )

    if episode_number != db_user.current_episode:
        raise HTTPException(status_code=400, detail="Episode is locked")

    episode = db.query(Episode).filter(Episode.episode_number == episode_number).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    progress = (
        db.query(UserEpisodeProgress)
        .filter(
            UserEpisodeProgress.user_id == db_user.id,
            UserEpisodeProgress.episode_id == episode.id,
        )
        .first()
    )

    if not progress:
        progress = UserEpisodeProgress(
            user_id=db_user.id,
            episode_id=episode.id,
            started_at=datetime.utcnow(),
            completed=True,
            completed_at=datetime.utcnow(),
            time_spent_seconds=data.time_spent_seconds,
        )
        db.add(progress)
    else:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        progress.time_spent_seconds = data.time_spent_seconds

    db_user.current_episode += 1
    db.commit()

    return {"message": f"Episode {episode_number} completed successfully"}


@app.post("/episodes/{episode_number}/quiz-response")
def save_quiz_response(
    episode_number: int,
    data: QuizResponseRequest,
    user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    db_user = get_or_create_user(user, db)

    if not db_user.pre_questionnaire_completed:
        raise HTTPException(
            status_code=400, detail="Complete pre-questionnaire first"
        )

    if episode_number > db_user.current_episode:
        raise HTTPException(status_code=400, detail="Episode is locked")

    episode = db.query(Episode).filter(Episode.episode_number == episode_number).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    quiz_response = UserQuizResponse(
        user_id=db_user.id,
        episode_id=episode.id,
        question_text=data.question_text,
        response_text=data.response_text,
        skipped=data.skipped,
    )

    db.add(quiz_response)
    db.commit()
    db.refresh(quiz_response)

    return {
        "message": "Quiz response saved successfully",
        "response_id": quiz_response.id,
    }


@app.post("/episodes/{episode_number}/reaction")
def save_episode_reaction(
    episode_number: int,
    data: EpisodeReactionRequest,
    user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    db_user = get_or_create_user(user, db)

    if not db_user.pre_questionnaire_completed:
        raise HTTPException(
            status_code=400, detail="Complete pre-questionnaire first"
        )

    if episode_number > db_user.current_episode:
        raise HTTPException(status_code=400, detail="Episode is locked")

    episode = db.query(Episode).filter(Episode.episode_number == episode_number).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    reaction = UserEpisodeReaction(
        user_id=db_user.id,
        episode_id=episode.id,
        emoji=data.emoji,
        audio_timestamp_seconds=data.audio_timestamp_seconds,
    )

    db.add(reaction)
    db.commit()
    db.refresh(reaction)

    return {
        "message": "Reaction saved successfully",
        "reaction_id": reaction.id,
        "audio_timestamp_seconds": reaction.audio_timestamp_seconds,
    }


@app.post("/upload-transcript/{episode_number}")
def upload_transcript(
    episode_number: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    episode = db.query(Episode).filter(Episode.episode_number == episode_number).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    temp_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transcript_text = ""

    if file.filename.endswith(".docx"):
        transcript_text = extract_text_from_docx(temp_path)
    elif file.filename.endswith(".txt"):
        with open(temp_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()
    else:
        raise HTTPException(
            status_code=400,
            detail="Only .docx or .txt transcript files are supported",
        )

    episode.transcript_text = transcript_text
    episode.transcript_url = (
        f"http://127.0.0.1:8000/uploads/{os.path.basename(temp_path)}"
    )

    db.commit()

    return {
        "message": "Transcript uploaded and processed",
        "transcript_url": episode.transcript_url,
    }


@app.post("/admin/episodes/upload")
def upload_episode(
    episode_number: int = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    quiz_json: str = Form("[]"),
    audio_file: UploadFile = File(...),
    transcript_file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    try:
        parsed_quiz = json.loads(quiz_json)
        if not isinstance(parsed_quiz, list):
            raise ValueError("quiz_json must be a list")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid quiz_json format")

    filename = f"episode_{episode_number}_{audio_file.filename}"
    audio_url = upload_audio_file(audio_file.file, filename)

    transcript_url = None
    transcript_text = None

    if transcript_file:
        transcript_filename = f"episode_{episode_number}_{transcript_file.filename}"
        transcript_path = os.path.join(UPLOAD_DIR, transcript_filename)

        with open(transcript_path, "wb") as buffer:
            shutil.copyfileobj(transcript_file.file, buffer)

        transcript_url = f"http://127.0.0.1:8000/uploads/{transcript_filename}"

        if transcript_file.filename.endswith(".docx"):
            transcript_text = extract_text_from_docx(transcript_path)
        elif transcript_file.filename.endswith(".txt"):
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
        episode = Episode(
            episode_number=episode_number,
            title=title,
            description=description,
            audio_url=audio_url,
            transcript_url=transcript_url,
            transcript_text=transcript_text,
            quiz_json=json.dumps(parsed_quiz),
            is_published=True,
        )
        db.add(episode)

    db.commit()

    return {
        "message": "Episode uploaded successfully",
        "audio_url": audio_url,
        "transcript_url": transcript_url,
        "quiz_count": len(parsed_quiz),
    }