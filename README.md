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

```
[ User / Client ]
        |
        v
   [ IdP Service ] --(JWT)--> [ Resource API ] --(allow/deny/challenge)--> [ User ]
        \
         \-- optional (no IdP) --> [ Local Service ] --(local session)--> [ User ]
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

## 🧠 What You’ll Do

In your assignment, you will:

- Extend the **IdP** to include additional claims (e.g., device, role).  
- Add **contextual verification logic** in `resource_api/context.py`.  
- Implement a **decentralised local authentication** method in `local_service/`.  
- Document and reflect on the **trade-offs** between the two approaches.

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
