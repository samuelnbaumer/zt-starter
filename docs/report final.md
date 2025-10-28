# Zero Trust Architecture - Design and Implementation Report

## Architecture Overview and Changes to the Starter Code

This implementation builds on the provided Zero Trust Starter Repository and extends it to demonstrase a practical transition from perimeter-based security to continuous verification. The system is composed of three independent FastAPI services that illustrate both centralised and decentralised authentication:

1. **Identity Provider (IdP):** provides centralised authentication and issues signed JWTs.
2. **Resource API:** represents a protected service that verifies JWTs and perform contextual verification.
3. **Local Service:** demonstrates a decentralised authentication ans dynamic risk evaluation.

### Changes to the Startet Code

Each service was extended to integrate contextual verification and dynamic risk evaluation.

#### Enhanced Identity Provider (IdP)

The IdP was expanded with a risk-aware authentication model and newJWT claims. Each user has an associated base risk level and departmet. The updated user database is shown below:

```python
# Enhanced user database with risk profiles
USERS = {
    "analyst": {"password": "analyst", "role": "analyst", "risk_score": 0.2, "department": "analytics"},
    "contractor": {"password": "contractor", "role": "contractor", "risk_score": 0.6, "department": "external"},
    "admin": {"password": "admin", "role": "admin", "risk_score": 0.1, "department": "it"},
    "manager": {"password": "manager", "role": "manager", "risk_score": 0.3, "department": "management"},
}
```

The IdP also computes a dynamic risk score by combining several contextual dimensions such as user type, device and time. These values are stored as part of the token claims.

```python
# Multi-factor risk calculation
final_risk_score = min(1.0, base_risk + device_risk + time_risk)
```

To support contextual decisions, JWTs now include device- and risk-related data:
```json
{
  "sub": "analyst",
  "role": "analyst", 
  "department": "analytics",
  "risk_score": 0.3,
  "device_id": "mac-001",
  "device_type": "laptop",
  "device_trust_level": 0.9,
  "login_time": "2025-10-25T14:34:39.073455+00:00"
}
```

This information allows the Resource API to perform fine-grained access control based on identity, role, device trust level and access time.

#### Local Service

The Local Service provides a standalone example of decentralised authentication. It maintains its own user repository and contextual checks:


```python
# Local user database (independent from IdP)
LOCAL_USERS = {
    "local": {"password": "local", "role": "local_user", "department": "local_dept", "risk_score": 0.1},
    "admin": {"password": "admin", "role": "local_admin", "department": "local_dept", "risk_score": 0.0},
    "guest": {"password": "guest", "role": "guest", "department": "external", "risk_score": 0.8},
}
```

Each service runs in its own Docker container, which promotes micro-segmentation and isolates trust boundaries - a key concept in Zero Trust architectures.

## Additional Verification Logic

the primary extension beyond the startet code was the implementation of a contextual verification engine inside the the Resource API. This module continuously evaluates each request and adapts access decisions dynamically.

### Multi-Factor Context Evaluation

The function evaluate_request_context() integrates various contextual rules:

```python
def evaluate_request_context(claims: dict, path: str, method: str) -> Decision:
    # 1. HIGH-RISK USER CHECK
    if risk_score > HIGH_RISK_THRESHOLD:
        return "challenge"
    
    # 2. SENSITIVE ENDPOINT ACCESS
    if path in SENSITIVE_PATHS and role not in ADMIN_ROLES:
        return "deny"
    
    # 3. TIME-BASED ACCESS CONTROL
    if current_hour not in BUSINESS_HOURS:
        if role == "contractor":
            return "deny"
        elif risk_score > 0.3:
            return "challenge"
    
    # 4. DEVICE-BASED VERIFICATION
    if device_trust_level < 0.5:
        return "challenge"
```

### Implemented Contextual Factors

#### 1. Time-Based Access Control:
Requests are allowed only during business hours (07:00-19:00). Contractors are denied access outside this window.

#### 2. Device-Based Verification:
The API checks the device_trust_level claim. unknown or low-trust devices trigger step-up authentication.

#### 3. Sensitivity-Based Access:
Critical routes such as /admin are restricted to administrative roles only.

#### 4. Risk-Based Challenges:
High-risk users are prompted with MFA or additional verification befor access is granted.

### Local Contextual Verification

The Local Service follows the same principle but without external dependencies. It evaluates local device information and risk data directly, supporting resilient operation even if the IdP is unavailable.

## Trade-offs between Centralised and Decentralised Verification

Both models were implemented and compared based on security, scalability and managebility.

### Centralised Authentication (IdP + Resource API)

#### Advantages
- Unified Policy Enfordement: All services are subject to the same rules and risk logic.
- Centralised Monitoring: Simplifies auditing and detection of anomalies.
- Consistent Token Verification: Reduces policy drift across microservices.
- Easy Scalability: New services can reuse the IdP without major configuration.

#### Disadvantages
- Single Point of Failure: If the IdP becomes unavailable, all dependent services are affected.
- Increased Latency: Each request requires token validation and risk evaluation.
- Complex Configuration: Central rules must fit various service needs.

### Decentralised Authentication (Local Service)

#### Advantages
- Resilience: Service remain operational even when disconnected from the central IdP.
- Performance: Local authentication reduces networt overhead.
- Flexibility: Each service can define its own access policies.

#### Disadvantages
- Policy Inconsistency: Diffent services may drift in terms of security enforcement.
- Higher Maintenance Effort: Each service must handle authentication and risk logic.
- Limited Visibility: It is more difficult to maintain a consistent audit trail across all services.

### Evaluation
Centralised verification is ideal for environments priortising control and compliance, while decentralised authentication increases fault tolerance. A hybrid approach, centralised identity with local policy caching, could combine the strengths of both. 

## Reflection on Zero Trust Principles

The developed system effectively demonstrates the transition from implicity network trsut to continuous, evidence-based verification.
Each service applies the Zero Trust core principle: "Never trust, always verify."

### Applied Zero Trust Principles
- Continuous Verification: Every request undergoes contextual checks, independent of prior authentication.
- Least Privilege: Access is granted strictly according to usere role and resource sensitivity.
- Context-Aware Decisions: Risk, time and device trust directly influence the decision process.
- Micro-Segmentatiom: Each component runs in an isolated container with its own policies.
- Dynamic Risk Assessment: Access adapts to current risk conditions through calculated scores.

## Testing and Verification

To validate the implementation, several test scenarios were executed using `test_scenarios.sh` and manual API calls.

### Functional Scenarios

| Scenario | User | Device | Time | Expected Result |
|-----------|------|---------|------|-----------------|
| 1 | analyst | mac-001 (trusted) | Business hours | Access granted |
| 2 | contractor | unknown-device | Business hours | MFA challenge |
| 3 | admin | mac-001 | Business hours | Admin access granted |
| 4 | contractor | mac-001 | 22:00 | Access denied |
| 5 | local | local-laptop | Anytime | Local access granted |

All contextual checks behaved as intended. Time restrictions, device trust, and role-based access were enforced dynamically.

### Reflection
The experiment shows that Zero Trust can be implemented incrementally using simple architectural compomemts.
By extending JWTs with contextual data and introducing continuous evaluation at the API layser, the system achieves real-time trust decisions instead of relying on static credentials.

Further improvements such as asymmetric JWT signing, JWKS key rotation and centralised logging would enhance resilience and compliance but are beyond the inital scope.

Overall, the implementation succsessfully operationalises Zero Trust concepts in a distributed architecture and highlights the trade-offs between scalability, performance and policy consistency.









