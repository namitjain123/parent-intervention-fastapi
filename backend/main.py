from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError
import requests

app = FastAPI()
security = HTTPBearer()

TENANT_ID = "e780d35f-2943-4663-83ab-03d9407a2074"
CLIENT_ID = "0c14d865-04b2-4427-9e4f-273649aee872"

# Use the SAME authority family as frontend
OPENID_CONFIG_URL = (
    f"https://parentingplatform.ciamlogin.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"
)

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


@app.get("/")
def home():
    return {"message": "FastAPI is running"}


@app.get("/test")
def test():
    return {"message": "Backend reachable"}


@app.get("/protected")
def protected_route(user=Depends(verify_token)):
    return {
        "message": f"Hello {user.get('name', 'user')}, your token is valid.",
        "user": user,
    }