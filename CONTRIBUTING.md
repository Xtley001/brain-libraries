# Contributing

Guidelines for contributing to the `brain-alpha-pipeline` 7-package quantitative library suite.

## Development Setup

Clone the repository and install all packages in editable mode:

```bash
git clone https://github.com/Xtley001/brain-libraries.git
cd brain-libraries
python -m venv venv
venv\Scripts\activate
pip install -e ./brain_core -e ./brain_store -e ./brain_decorrelator -e ./brain_options -e ./brain_sentiment -e ./brain_risk_model -e ./brain_synthesis
```

Run the entire verification suite:

```bash
python scripts/test_all.py
```

## Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Implement your changes adhering to existing package interfaces and invariants.
3. Add unit tests under the corresponding `tests/` directory for any new logic or bug fix.
4. Verify that all 86+ test cases pass:
   ```bash
   python scripts/test_all.py
   ```
5. Ensure type annotations and docstrings are complete.
6. Commit using conventional commit format:
   ```bash
   git commit -m "feat(brain_decorrelator): add multi-regime volatility axis"
   ```
7. Open a Pull Request against `main`. All CI checks must pass prior to review.

## Code Standards

- **Formatting:** Use `black` (88 character line limit).
- **Linting:** Use `flake8` for syntax and style validation.
- **Typing:** Static typing required for all public functions and classes.
- **Determinism:** Alpha expression generators must produce deterministic ASTs.
- **Contract Adherence:** All data exchange across packages must use `brain_core.AlphaCandidate`.

## Package Releases

Versions follow Semantic Versioning (`MAJOR.MINOR.PATCH`). Releases to PyPI are tagged on `main` and published via GitHub Actions.
