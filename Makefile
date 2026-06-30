.PHONY: install dev test lint typecheck format clean examples

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pip install pre-commit
	pre-commit install

test:
	pytest -q

lint:
	ruff check .

typecheck:
	mypy src

format:
	ruff format .

examples: install
	python examples/basic-skill/run_demo.py
	python examples/mcp-integration/run_demo.py
	python examples/advanced-patterns/run_demo.py

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
