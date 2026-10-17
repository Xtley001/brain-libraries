"""
Root pytest configuration for brain-libraries monorepo.
Ensures all 7 library sources are added to sys.path during test runs.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Add each package directory to sys.path
for pkg in [
    "brain_core",
    "brain_decorrelator",
    "brain_options",
    "brain_sentiment",
    "brain_risk_model",
    "brain_store",
    "brain_synthesis",
]:
    pkg_path = ROOT / pkg
    if pkg_path.is_dir() and str(pkg_path) not in sys.path:
        sys.path.insert(0, str(pkg_path))
