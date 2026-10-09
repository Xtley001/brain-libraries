# Contributing to brain-store

## Setup

```bash
git clone https://github.com/Xtley001/brain-libraries.git
cd brain-alpha-pipeline/brain_libraries/brain_store
python -m venv venv && source venv/bin/activate
pip install -e .[dev]
pytest
```

PostgreSQL is not required for offline file-mode unit tests.

## Standards

- Format: `black .`
- Lint: `flake8`
- Types: `mypy .`
- Coverage: >= 80%

## Pull Requests

Open against `main`. All CI checks must pass. At least one maintainer must approve.
