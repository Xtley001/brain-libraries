"""
Brain Alpha Pipeline — Unified Cross-Domain CLI entrypoint.
"""
import os
import sys

# Ensure local packages are on sys.path when running from repository scripts directory
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _lib in (
    "brain_core",
    "brain_store",
    "brain_decorrelator",
    "brain_options",
    "brain_sentiment",
    "brain_risk_model",
    "brain_synthesis",
):
    _pkg_path = os.path.join(_base_dir, _lib)
    if os.path.isdir(_pkg_path) and _pkg_path not in sys.path:
        sys.path.insert(0, _pkg_path)

from brain_synthesis.cli import main, build_parser

if __name__ == "__main__":
    sys.exit(main())
