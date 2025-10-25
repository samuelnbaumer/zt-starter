from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
import os

APP = FastAPI(title="IdP")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")

# Mock user database. In a real application we would use a database
USERS = {
    "analyst": {"password": "analyst", "role": "analyst", "risk_score": 0.2, "department": "analytics"},
    "contractor": {"password": "contractor", "role": "contractor", "risk_score": 0.6, "department": "external"},
    "admin": {"password": "admin", "role": "admin", "risk_score": 0.1, "department": "it"},
    "manager": {"password": "manager", "role": "manager", "risk_score": 0.3, "department": "management"},
}

# Trusted devices registry
TRUSTED_DEVICES = {
    "mac-001": {"device_type": "laptop", "trust_level": 0.9, "last_seen": "2024-01-15"},
    "mobile-002": {"device_type": "mobile", "trust_level": 0.7, "last_seen": "2024-01-14"},
    "desktop-003": {"device_type": "desktop", "trust_level": 0.8, "last_seen": "2024-01-15"},
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
    
    # Calculate dynamic risk score based on user, device, and time
    base_risk = u["risk_score"]
    device_risk = 0.0
    time_risk = 0.0
    
    # Device-based risk assessment
    if inp.device_id:
        device_info = TRUSTED_DEVICES.get(inp.device_id)
        if device_info:
            device_risk = 1.0 - device_info["trust_level"]  # Higher trust = lower risk
        else:
            device_risk = 0.5  # Unknown device = medium risk
    
    # Time-based risk (higher risk outside business hours)
    current_hour = now.hour
    if current_hour < 7 or current_hour > 19:
        time_risk = 0.3  # Higher risk outside business hours
    
    # Calculate final risk score (0.0 = low risk, 1.0 = high risk)
    final_risk_score = min(1.0, base_risk + device_risk + time_risk)
    
    claims = {
        "sub": inp.username,
        "role": u["role"],
        "department": u["department"],
        "risk_score": round(final_risk_score, 2),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=30)).timestamp()),
        "typ": "access",
        "login_time": now.isoformat(),
    }
    
    print("Secret: " + JWT_SECRET)
    print("Alg: " + JWT_ALG)
    print(f"Risk Score: {final_risk_score}")
    
    if inp.device_id:
        claims["device_id"] = inp.device_id
        claims["device_type"] = TRUSTED_DEVICES.get(inp.device_id, {}).get("device_type", "unknown")
        claims["device_trust_level"] = TRUSTED_DEVICES.get(inp.device_id, {}).get("trust_level", 0.0)
    
    token = jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALG)
    return {"access_token": token, "token_type": "bearer", "risk_score": final_risk_score}
