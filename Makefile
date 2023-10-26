pretty:
	isort src
	black src
	pylint src
	mypy src
install:
	pip install pipenv
	pipenv install
dev:
	python -m src
up:
	docker compose up -d --build
down:
	docker compose down
dev:
	pipenv run uvicorn src.modules.api.app:app
