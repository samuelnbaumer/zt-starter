from fastapi import FastAPI, Depends, HTTPException
from auth import get_claims
from context import evaluate_request_context

APP = FastAPI(title="Resource API")

@APP.get("/resource")
def resource(claims: dict = Depends(get_claims)):
    decision = evaluate_request_context(claims, "/resource", "GET")
    if decision == "deny":
        raise HTTPException(status_code=403, detail="denied by context policy")
    if decision == "challenge":
        # For PoC, simulate an MFA step-up requirement
        return {"status": "mfa_required", "reason": "context challenge"}
    return {"status": "ok", "subject": claims.get("sub"), "role": claims.get("role")}

@APP.get("/export")
def export(claims: dict = Depends(get_claims)):
    decision = evaluate_request_context(claims, "/export", "GET")
    if decision == "deny":
        raise HTTPException(status_code=403, detail="denied by context policy")
    if decision == "challenge":
        return {"status": "mfa_required", "reason": "sensitive endpoint"}
    return {"status": "export_ready"}

@APP.get("/admin")
def admin_panel(claims: dict = Depends(get_claims)):
    decision = evaluate_request_context(claims, "/admin", "GET")
    if decision == "deny":
        raise HTTPException(status_code=403, detail="Access denied: insufficient privileges")
    if decision == "challenge":
        return {"status": "mfa_required", "reason": "admin access requires additional verification"}
    return {"status": "admin_access_granted", "subject": claims.get("sub"), "role": claims.get("role")}

@APP.get("/sensitive")
def sensitive_data(claims: dict = Depends(get_claims)):
    decision = evaluate_request_context(claims, "/sensitive", "GET")
    if decision == "deny":
        raise HTTPException(status_code=403, detail="Access denied: sensitive data access restricted")
    if decision == "challenge":
        return {"status": "mfa_required", "reason": "sensitive data access requires additional verification"}
    return {"status": "sensitive_data_accessed", "data": "confidential information"}

@APP.get("/status")
def status(claims: dict = Depends(get_claims)):
    #Public endpoint to show current user context and risk assessment
    return {
        "status": "ok",
        "user": claims.get("sub"),
        "role": claims.get("role"),
        "department": claims.get("department"),
        "risk_score": claims.get("risk_score"),
        "device_id": claims.get("device_id"),
        "device_trust_level": claims.get("device_trust_level"),
        "login_time": claims.get("login_time")
    }
