from fastapi import FastAPI, HTTPException, Response, Request
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
import hashlib
import secrets

APP = FastAPI(title="Local Service")
LOCAL_SECRET = "local-secret"
LOCAL_ALG = "HS256"
SESSIONS: dict[str, dict] = {}  # jti -> claims

# Mock user database. In a real application we would use a database
LOCAL_USERS = {
    "local": {"password": "local", "role": "local_user", "department": "local_dept", "risk_score": 0.1},
    "admin": {"password": "admin", "role": "local_admin", "department": "local_dept", "risk_score": 0.0},
    "guest": {"password": "guest", "role": "guest", "department": "external", "risk_score": 0.8},
}

# Mock device database. In a real application we would use a database
LOCAL_DEVICES = {
    "local-laptop": {"device_type": "laptop", "trust_level": 0.9},
    "local-mobile": {"device_type": "mobile", "trust_level": 0.7},
}

class LoginIn(BaseModel):
    username: str
    password: str
    device_id: str | None = None
    remember_device: bool = False

@APP.post("/local-login")
def local_login(inp: LoginIn, resp: Response):
    user = LOCAL_USERS.get(inp.username)
    if not user or user["password"] != inp.password:
        raise HTTPException(status_code=401, detail="Invalid local credentials")
    
    now = datetime.now(timezone.utc)
    
    # Calculate local risk score
    base_risk = user["risk_score"]
    device_risk = 0.0
    time_risk = 0.0
    
    # Device-based risk assessment
    if inp.device_id:
        device_info = LOCAL_DEVICES.get(inp.device_id)
        if device_info:
            device_risk = 1.0 - device_info["trust_level"]
        else:
            device_risk = 0.5  # Unknown device
    
    # Time-based risk (simpler than IdP for local service)
    current_hour = now.hour
    if current_hour < 8 or current_hour > 18:
        time_risk = 0.2
    
    final_risk_score = min(1.0, base_risk + device_risk + time_risk)
    
    # Generate session ID
    session_id = secrets.token_urlsafe(32)
    
    claims = {
        "sub": inp.username,
        "role": user["role"],
        "department": user["department"],
        "risk_score": round(final_risk_score, 2),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),  # Longer session for local
        "typ": "local",
        "session_id": session_id,
        "login_time": now.isoformat(),
    }
    
    if inp.device_id:
        claims["device_id"] = inp.device_id
        claims["device_type"] = LOCAL_DEVICES.get(inp.device_id, {}).get("device_type", "unknown")
        claims["device_trust_level"] = LOCAL_DEVICES.get(inp.device_id, {}).get("trust_level", 0.0)
    
    # Store session
    SESSIONS[session_id] = claims
    
    token = jwt.encode(claims, LOCAL_SECRET, algorithm=LOCAL_ALG)
    resp.set_cookie("local_session", token, httponly=True, samesite="lax", max_age=900)  # 15 minutes
    
    return {
        "status": "local_session_issued",
        "session_id": session_id,
        "risk_score": final_risk_score,
        "expires_in": 900
    }

@APP.get("/local-resource")
def local_resource(req: Request):

    #Enhanced local resource access with contextual verification
    token = req.cookies.get("local_session")
    if not token:
        raise HTTPException(status_code=401, detail="Missing local session")
    
    try:
        claims = jwt.decode(token, LOCAL_SECRET, algorithms=[LOCAL_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid local session")
    
    # Local contextual verification
    risk_score = claims.get("risk_score", 0.0)
    role = claims.get("role")
    
    # High-risk users need additional verification
    if risk_score > 0.6:
        return {"status": "verification_required", "reason": "high risk user", "risk_score": risk_score}
    
    # Guest users have limited access
    if role == "guest" and risk_score > 0.4:
        return {"status": "access_limited", "reason": "guest user with high risk"}
    
    return {
        "status": "ok-local", 
        "subject": claims["sub"], 
        "role": claims["role"],
        "risk_score": risk_score,
        "department": claims.get("department"),
        "device_id": claims.get("device_id")
    }

@APP.get("/local-admin")
def local_admin(req: Request):
    #Admin-only endpoint for local service
    token = req.cookies.get("local_session")

    if not token:
        raise HTTPException(status_code=401, detail="Missing local session")
    
    try:
        claims = jwt.decode(token, LOCAL_SECRET, algorithms=[LOCAL_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid local session")
    
    role = claims.get("role")
    if role != "local_admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"status": "admin_access_granted", "subject": claims["sub"]}

@APP.get("/local-status")
def local_status(req: Request):
    #Show current local session status
    token = req.cookies.get("local_session")
    if not token:
        return {"status": "not_authenticated"}
    
    try:
        claims = jwt.decode(token, LOCAL_SECRET, algorithms=[LOCAL_ALG])
        return {
            "status": "authenticated",
            "user": claims.get("sub"),
            "role": claims.get("role"),
            "department": claims.get("department"),
            "risk_score": claims.get("risk_score"),
            "device_id": claims.get("device_id"),
            "device_trust_level": claims.get("device_trust_level"),
            "login_time": claims.get("login_time"),
            "session_id": claims.get("session_id")
        }
    except Exception:
        return {"status": "invalid_session"}

@APP.post("/local-logout")
def local_logout(req: Request, resp: Response):
    #Logout and clear session
    token = req.cookies.get("local_session")
    if token:
        try:
            claims = jwt.decode(token, LOCAL_SECRET, algorithms=[LOCAL_ALG])
            session_id = claims.get("session_id")
            if session_id in SESSIONS:
                del SESSIONS[session_id]
        except Exception:
            pass
    
    resp.delete_cookie("local_session")
    return {"status": "logged_out"}
    #this is a comment for my fellow group members who said they will check an review what i've done. Please mention this line to me in teams if you been here ;)