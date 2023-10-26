pretty:
	isort src
	black src
	pylint src
	mypy src
install:
	pip install pipenv
	pipenv install
up:
	docker compose up -d --build
down:
	docker compose down
