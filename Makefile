.PHONY: start test build

start:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=. pytest

build:
	docker build -t farmdoc .
