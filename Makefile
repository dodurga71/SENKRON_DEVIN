.PHONY: install test lint run
install:
python -m pip install -U pip
pip install -r requirements.txt
test:
pytest -q --cov=app --cov-branch --cov-report=term-missing
lint:
python -m ruff check .
run:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
