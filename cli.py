"""
Brain Alpha Pipeline — Unified Cross-Domain CLI entrypoint.
"""
from brain_synthesis.cli import main, build_parser

if __name__ == "__main__":
    import sys
    sys.exit(main())
