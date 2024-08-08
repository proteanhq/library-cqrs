# library

Protean example implementation

|                 |                                                                         |
|-----------------|-------------------------------------------------------------------------|
| Source          | [DDD by Examples - Library](https://github.com/ddd-by-examples/library) |
| Pattern         | CQRS                                                                    |
| Protean Version | 0.12.1                                                                  |
| Build Status    | [Build Status](https://github.com/proteanhq/library-cqrs/actions/workflows/ci.yml/badge.svg) |
| Coverage        | [![codecov](https://codecov.io/github/proteanhq/library-cqrs/graph/badge.svg?token=onIFcl4Dg5)](https://codecov.io/github/proteanhq/library-cqrs)|

## Contributing

- Clone this repository:

`git clone git@github.com:proteanhq/library-cqrs.git`

- Set up and activate Python virtual environment:

`python3 -m venv .venv`

`source .venv/bin/activate`

- Install [poetry](https://python-poetry.org/docs/#installation)

- Install dependencies:

`poetry install`

- Install pre-commit hooks:

`pre-commit install`

## Running Tests

- Basic: `make test`

- With coverage: `make test-cov`