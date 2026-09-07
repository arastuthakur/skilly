.PHONY: run test lint

# Run development server
run:
	uvicorn main:app --reload

# Execute test suite
test:
	pytest tests/

# Run linter
lint:
	flake8 .
