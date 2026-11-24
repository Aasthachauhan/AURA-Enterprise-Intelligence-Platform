.PHONY: help install dev backend-run frontend-run test test-backend test-e2e build docker-up docker-down

help:
	@echo "AURA Platform - Development Commands"
	@echo "  make install        Install backend and frontend dependencies"
	@echo "  make backend-run    Start FastAPI backend server on port 8000"
	@echo "  make frontend-run   Start Vite frontend server on port 5173"
	@echo "  make test           Run full pytest and end-to-end verification"
	@echo "  make build          Build production frontend bundle"
	@echo "  make docker-up      Start complete multi-container stack via Docker Compose"
	@echo "  make docker-down    Stop Docker Compose containers"

install:
	python -m pip install -r backend/requirements.txt
	cd frontend && npm install

backend-run:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

frontend-run:
	cd frontend && npm run dev

test:
	pytest backend/tests -v
	python scripts/run_e2e_journey.py

build:
	cd frontend && npm run build

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down
