.PHONY: setup data prep train eval api test lint docker

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt && pip install -e .

data:
	bash scripts/download_datasets.sh

prep:
	python -m dyslexia.data.prepare_m1_handwriting
	python -m dyslexia.data.prepare_m2_speech
	python -m dyslexia.data.prepare_m3_simplify
	python -m dyslexia.data.synth_reading_errors

train:
	python -m dyslexia.training.train_m1_cnn        --config configs/m1_handwriting.yaml
	python -m dyslexia.training.train_m2_error_clf  --config configs/m2_reading_error.yaml
	python -m dyslexia.training.train_m3_simplifier --config configs/m3_simplifier.yaml
	python -m dyslexia.training.train_m7_risk       --config configs/m7_risk.yaml

eval:
	python -m dyslexia.evaluation.run_all

api:
	uvicorn dyslexia.api.main:app --reload --port 8000

test:
	pytest

lint:
	ruff check src tests && black --check src tests

docker:
	docker compose -f deployment/docker/docker-compose.yml up --build
