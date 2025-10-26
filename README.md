# 🔐 Zero Trust Authentication Starter Repository

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Built with Docker](https://img.shields.io/badge/built%20with-Docker-blue.svg)](https://www.docker.com/)

---

## 💡 Overview

This repository provides the **baseline for the group assignment** in the module  
**Software Design & Architecture – Zero Trust Authentication in Distributed Systems.**

It includes a working prototype illustrating the transition from **perimeter-based security** to **Zero Trust verification** using authentication, identity, and contextual checks.

Students will extend this code to explore:

- Centralised vs. decentralised authentication  
- Token-based identity verification  
- Context-aware access control (device, time, sensitivity)

---

## 🧩 Architecture Overview

```mermaid
flowchart LR
    A[User / Client] -->|Login request| B[IdP Service]
    B -->|JWT token| C[Resource API]
    C -->|Access decision| A
    A -->|Direct auth| D[Local Service]
    D -->|Local session token| A

    %% Styling
    classDef idp fill:#009688,stroke:#00695c,color:#fff;
    classDef resource fill:#03a9f4,stroke:#0277bd,color:#fff;
    classDef local fill:#8bc34a,stroke:#558b2f,color:#fff;

    class B idp;
    class C resource;
    class D local;

    %% Caption
    %% The diagram illustrates centralised vs. local authentication flows in a Zero Trust setup.
```

**Services**

- **IdP (`/idp`)** – Issues signed JWT tokens for authenticated users  
- **Resource API (`/resource_api`)** – Verifies tokens and enforces contextual rules  
- **Local Service (`/local_service`)** – Demonstrates standalone local authentication

Each service is packaged as a **Docker container** and orchestrated via `docker-compose.yml`.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/bfh-architecture/zt-starter.git
cd zt-starter
```

### 2. Start the environment

```bash
docker compose up --build
```

### 3. Test the authentication flow

```bash
make test-curl
```

Expected result:  
A valid JWT is issued by the IdP and verified by the Resource API.

---

## 🧠 What You'll Do

In your assignment, you will:

- Extend the **IdP** to include additional claims (e.g., device, role).  
- Add **contextual verification logic** in `resource_api/context.py`.  
- Implement a **decentralised local authentication** method in `local_service/`.  
- Document and reflect on the **trade-offs** between the two approaches.

## 🔧 What Was Added

### IdP Service
- Dynamic risk scoring based on user, device, and time
- Additional JWT claims: `device_id`, `department`, `risk_score`, `device_trust_level`

### Resource API
- Time-based access control (business hours 7-19)
- Device trust verification
- Admin-only endpoints
- Risk-based MFA challenges

### Local Service
- Independent local authentication
- Cookie-based sessions
- Local risk assessment

## Testing

For testing purposes we added a **test_scenarios.sh** script that can be run. Also please see the following examples:

#### Low-Risk User (Analyst)
```bash
curl -X POST http://localhost:8001/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"analyst","password":"analyst","device_id":"mac-001"}'
```

#### High-Risk User (Contractor)
```bash
curl -X POST http://localhost:8001/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"contractor","password":"contractor","device_id":"unknown-device"}'
```

#### Admin Access
```bash
curl -X POST http://localhost:8001/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin","device_id":"mac-001"}'
```

### Testing Contextual Verification

#### Check User Status
```bash
TOKEN=$(curl -sS -X POST http://localhost:8001/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"analyst","password":"analyst","device_id":"mac-001"}' \
  | jq -er '.access_token')

curl -sS http://localhost:8002/status \
  -H "Authorization: Bearer $TOKEN" | jq .
```

#### Test Sensitive Endpoints
```bash
# Admin endpoint (requires admin role)
curl -sS http://localhost:8002/admin \
  -H "Authorization: Bearer $TOKEN" | jq .

# Sensitive data endpoint
curl -sS http://localhost:8002/sensitive \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Testing Local Authentication

#### Local Login
```bash
curl -X POST http://localhost:8003/local-login \
  -H 'Content-Type: application/json' \
  -d '{"username":"local","password":"local","device_id":"local-laptop"}' \
  -c cookies.txt
```

#### Access Local Resources
```bash
curl -sS http://localhost:8003/local-resource \
  -b cookies.txt | jq .
```

#### Check Local Status
```bash
curl -sS http://localhost:8003/local-status \
  -b cookies.txt | jq .
```

---

## 📦 Repository Structure

```
zt-starter/
│-- docker-compose.yml
│-- Makefile
│-- idp/
│   ├── app.py
│   ├── .env
│   ├── Dockerfile
│-- resource_api/
│   ├── app.py
│   ├── auth.py
│   ├── context.py
│   ├── .env
│   ├── Dockerfile
│-- local_service/
│   ├── app.py
│   ├── .env
│   ├── Dockerfile
```

All `.env` files are included intentionally for **educational transparency**.

---

## 🧾 License

This repository is distributed under the **MIT License**.  
It is intended for educational use within the  
**Bern University of Applied Sciences (BFH)** – Software Design & Architecture module.

---

## 👨‍🏫 Maintainer

**Sebastian Höhn**  
Lecturer, Bern University of Applied Sciences (BFH)  
[BFH Wirtschaft – Institut Public Sector Transformation](https://www.bfh.ch/wirtschaft)

---

## 🏁 Quick Summary

| Component | Description |
|------------|-------------|
| `idp/` | Issues and signs JWT tokens (centralised identity provider) |
| `resource_api/` | Verifies tokens, checks context and access policies |
| `local_service/` | Independent local authentication demo |
| `Makefile` | Contains sample test commands |
| `.env` files | Predefined configuration for reproducibility |

---

## 🧭 Next Steps

1. Clone this repository.  
2. Extend the authentication and verification logic.  
3. Reflect on your architecture and design decisions.  
4. Submit your repository link via Moodle by **10 November 2025**.

> 🧩 *In this project, you will experience how trust becomes contextual — moving from network borders to evidence-based access decisions.*
