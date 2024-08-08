test:
	pytest tests/lending tests/catalogue

test-cov:
	pytest tests/lending tests/catalogue --cov=src/lending --cov=src/catalogue --cov-report=term-missing --cov-branch
