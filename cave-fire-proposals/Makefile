# Convenience Makefile for common development tasks
PY=python
PIP=${PY} -m pip
UVICORN=${PY} -m uvicorn

.PHONY: install install-dev start-api start-static start-servers e2e gen-exports

install:
	${PIP} install --upgrade pip
	${PIP} install -r requirements.txt

install-dev: install
	${PIP} install -r requirements-dev.txt
	${PY} -m playwright install

start-api:
	${UVICORN} app.server:app --reload --port 8003

start-static:
	python -m http.server 8002

start-servers:
	# start both servers (API on 8003 and static on 8002) in separate terminals
	@echo "Start the API in one terminal: make start-api"
	@echo "Start the static server in another: make start-static"

e2e:
	${PY} -m pytest tests/e2e -q

gen-exports:
	${PY} scripts/ci/generate_exports.py artifacts

# ============================================
# Deployment Commands
# ============================================

.PHONY: docker-build docker-run docker-test deploy-local deploy-prod

docker-build:
	docker build -t cave-fire-proposals:latest .

docker-run: docker-build
	docker run -p 8000:8000 cave-fire-proposals:latest

docker-test: docker-build
	docker run --rm cave-fire-proposals:latest ${PY} -m pytest tests/ -q

deploy-local:
	docker-compose up -d
	@echo "API available at http://localhost:8000"
	@echo "Run 'make deploy-logs' to view logs"

deploy-logs:
	docker-compose logs -f api

deploy-stop:
	docker-compose down

deploy-prod:
	docker-compose -f deployment/docker-compose.prod.yml up -d
	@echo "Production deployment started"

deploy-health:
	@bash deployment/healthcheck.sh

# Include additional deployment commands
-include Makefile.deploy
