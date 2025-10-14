from typing import Literal

Decision = Literal["allow", "challenge", "deny"]

SENSITIVE_PATHS = {"/export"}  # students can extend
BUSINESS_HOURS = range(7, 20)  # 07:00–19:59

def evaluate_request_context(claims: dict, path: str, method: str) -> Decision:
    # Minimal baseline: if sensitive endpoint and non-admin -> challenge
    role = claims.get("role")
    if path in SENSITIVE_PATHS and role != "admin":
        return "challenge"  # later: simulate MFA required
    # TODO (students): add time-of-day rules, first-time access, device_id checks, trust score, etc.
    return "allow"
