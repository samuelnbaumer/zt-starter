from typing import Literal
from datetime import datetime, timezone

Decision = Literal["allow", "challenge", "deny"]

SENSITIVE_PATHS = {"/export", "/admin", "/sensitive"}  # Extended sensitive endpoints
BUSINESS_HOURS = range(7, 20)  # 07:00–19:59
HIGH_RISK_THRESHOLD = 0.7  # Risk score threshold for additional verification
ADMIN_ROLES = {"admin", "manager"}

def evaluate_request_context(claims: dict, path: str, method: str) -> Decision:
    #Enhanced contextual verification implementing Zero Trust principles. Evaluates access based on identity, device, time, and risk factors.
    role = claims.get("role")
    risk_score = claims.get("risk_score", 0.0)
    device_id = claims.get("device_id")
    device_trust_level = claims.get("device_trust_level", 0.0)
    department = claims.get("department", "unknown")
    
    # Get current time for time-based checks
    current_hour = datetime.now(timezone.utc).hour
    
    # 1. High-Risk User Verification
    if risk_score > HIGH_RISK_THRESHOLD:
        return "challenge"  # Require additional verification for high-risk users
    
    # 2. Sensitive Endpoint Access
    if path in SENSITIVE_PATHS:
        # Only admins can access sensitive endpoints
        if role not in ADMIN_ROLES:
            return "deny"
        
        # Even admins need additional verification for very sensitive operations
        if path == "/export" and risk_score > 0.4:
            return "challenge"
    
    # 3. Time-Based Verification
    if current_hour not in BUSINESS_HOURS:
        # Outside business hours - stricter controls
        if role == "contractor":
            return "deny"  # Contractors denied outside business hours
        elif risk_score > 0.3:
            return "challenge"  # Higher risk users need verification outside hours
    
    # 4. Device-Based Verification
    if device_id:
        # Unknown or untrusted devices require additional verification
        if device_trust_level < 0.5:
            if path in SENSITIVE_PATHS:
                return "challenge"
            elif risk_score > 0.4:
                return "challenge"
    
    # 5. Departmental Restrictions
    if path.startswith("/admin") and department not in {"it", "management"}:
        return "deny"
    
    # 6. Contractor Restrictions
    if role == "contractor":
        # Contractors have limited access
        if path.startswith("/admin"):
            return "deny"
        if risk_score > 0.5:
            return "challenge"
    
    # 7. First time access
    # In a real system, this would check against a database of previous logins. For demo purposes, we'll simulate based on device trust level
    if device_trust_level == 0.0 and risk_score > 0.2:
        return "challenge"  # First-time access from unknown device
    
    # Default: allow access
    return "allow"
