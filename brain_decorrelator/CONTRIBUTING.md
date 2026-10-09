# Contributing to brain-decorrelator

## Setup

```bash
git clone https://github.com/Xtley001/brain-libraries.git
cd brain-alpha-pipeline/brain_libraries/brain_decorrelator
python -m venv venv && source venv/bin/activate
pip install -e .[dev]
pytest
```

## Adding Axes

To add a new orthogonal transformation axis, subclass `AxisPlugin` and annotate with `@register_axis`.
Include unit tests covering variant generation, invalid input handling, and expression deduplication.

## Standards

- Format: `black .`
- Lint: `flake8`
- Types: `mypy .`
- Coverage: >= 80%

## Pull Requests

Open against `main`. All CI checks must pass. At least one maintainer must approve.
