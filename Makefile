test:
	pytest

test-cov:
	pytest --cov=src/lending --cov-report=term-missing --cov-branch
