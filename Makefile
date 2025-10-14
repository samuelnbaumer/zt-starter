
up:
	docker compose up --build

down:
	docker compose down

test-curl:
	@set -euo pipefail; \
	TOKEN=$$(curl -sS -X POST http://localhost:8001/login \
	  -H 'Content-Type: application/json' \
	  -d '{"username":"analyst","password":"analyst","device_id":"mac-001"}' \
	  | jq -er '.access_token'); \
	printf 'Token: %s\n' "$$TOKEN"; \
	curl -sS http://localhost:8002/resource \
	  -H "Authorization: Bearer $$TOKEN" | jq .
