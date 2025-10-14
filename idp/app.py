from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
import os

APP = FastAPI(title="IdP")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")

USERS = {
    "analyst": {"password": "analyst", "role": "analyst"},
    "contractor": {"password": "contractor", "role": "contractor"},
}

class LoginIn(BaseModel):
    username: str
    password: str
    device_id: str | None = None

@APP.post("/login")
def login(inp: LoginIn):
    u = USERS.get(inp.username)
    if not u or u["password"] != inp.password:
        raise HTTPException(status_code=401, detail="invalid credentials")
    now = datetime.now(timezone.utc)
    claims = {
        "sub": inp.username,
        "role": u["role"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=30)).timestamp()),
        "typ": "access",
    }
    print("Secret: " + JWT_SECRET)
    print("Alg: " + JWT_ALG)
    if inp.device_id:
        claims["device_id"] = inp.device_id
    token = jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALG)
    return {"access_token": token, "token_type": "bearer"}
