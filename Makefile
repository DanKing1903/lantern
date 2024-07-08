install:
		poetry install --no-root
		poetry run pre-commit install

dev:
	  poetry run fastapi dev src/main.py

test:
	  poetry run python -m pytest

.PHONY: install dev
