from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError
from pydantic import BaseModel
import requests

app = FastAPI()
security = HTTPBearer()

TENANT_ID = "e780d35f-2943-4663-83ab-03d9407a2074"
CLIENT_ID = "0c14d865-04b2-4427-9e4f-273649aee872"  # backend app id

OPENID_CONFIG_URL = f"https://parentingplatform.ciamlogin.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openid_config = requests.get(OPENID_CONFIG_URL).json()
jwks_uri = openid_config["jwks_uri"]
issuer = openid_config["issuer"]
jwks = requests.get(jwks_uri).json()

# TEMP in-memory store for testing
users_db = {}

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

def get_or_create_user(user_claims):
    azure_id = user_claims.get("sub")
    name = user_claims.get("name", "User")
    email = user_claims.get("preferred_username") or user_claims.get("email") or "unknown@example.com"

    if azure_id not in users_db:
        users_db[azure_id] = {
            "azure_id": azure_id,
            "name": name,
            "email": email,
            "pre_questionnaire_completed": False,
            "current_episode": 0,
        }
    return users_db[azure_id]

@app.get("/me")
def get_me(user=Depends(verify_token)):
    db_user = get_or_create_user(user)
    return db_user

@app.get("/dashboard")
def get_dashboard(user=Depends(verify_token)):
    db_user = get_or_create_user(user)

    episodes = []
    for i in range(1, 5):
        if not db_user["pre_questionnaire_completed"]:
            status = "locked"
        elif i < db_user["current_episode"]:
            status = "completed"
        elif i == db_user["current_episode"]:
            status = "unlocked"
        else:
            status = "locked"

        episodes.append({
            "episode_number": i,
            "title": f"Episode {i}",
            "status": status
        })

    return {
        "name": db_user["name"],
        "email": db_user["email"],
        "pre_questionnaire_completed": db_user["pre_questionnaire_completed"],
        "current_episode": db_user["current_episode"],
        "episodes": episodes,
    }

class CompletePreQRequest(BaseModel):
    participant_id: str

@app.post("/mark-prequestionnaire-complete")
def mark_prequestionnaire_complete(data: CompletePreQRequest):
    if data.participant_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    users_db[data.participant_id]["pre_questionnaire_completed"] = True
    users_db[data.participant_id]["current_episode"] = 1

    return {"message": "Pre-questionnaire marked complete"}

@app.post("/episodes/{episode_number}/complete")
def complete_episode(episode_number: int, user=Depends(verify_token)):
    db_user = get_or_create_user(user)

    if not db_user["pre_questionnaire_completed"]:
        raise HTTPException(status_code=400, detail="Complete pre-questionnaire first")

    if episode_number != db_user["current_episode"]:
        raise HTTPException(status_code=400, detail="Episode is locked")

    db_user["current_episode"] += 1
    return {"message": f"Episode {episode_number} completed"}