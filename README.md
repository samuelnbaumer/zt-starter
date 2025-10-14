# Goal: Compare centralised (IdP/JWT) vs decentralised (local auth) and add at least one context control.

- Run: make up; test: make test-curl.
  
# Implement:
  - Context checks in resource_api/context.py. 
  - A decentralised path in local_service (already scaffolded).
  - Document: 2–3 pages on design, context choice, trade-offs (latency, failure, UX).

# ⚙️ Configuration transparency

Normally .env files are excluded from repositories for security reasons.
Here, they are intentionally provided so you can inspect how environment variables influence services.
When deploying real systems, these values must be stored securely and never committed to version control.
