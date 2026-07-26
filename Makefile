.PHONY: test build up down verify reset

test:
	python -m pytest -q

build:
	docker compose build --no-cache

up:
	docker compose up -d --build

down:
	docker compose down --remove-orphans

verify:
	curl --fail --silent http://localhost:8080/health

reset:
	git checkout -- app/app.py tests/test_app.py 2>/dev/null || true
	docker compose down --remove-orphans
