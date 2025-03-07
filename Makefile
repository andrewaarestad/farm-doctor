.PHONY: run test build

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=. pytest

build:
	docker build -t myapp .

docker-run:
	docker run -p 8000:8000 myapp