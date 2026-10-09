#!/usr/bin/env python3
"""
Test runner script to execute tests for all 7 Brain libraries in isolation.
"""
import os
import subprocess
import sys

LIBRARIES = [
    "brain_core",
    "brain_store",
    "brain_decorrelator",
    "brain_options",
    "brain_sentiment",
    "brain_risk_model",
    "brain_synthesis",
]

def main() -> int:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable

    print("\n=======================================================")
    print("      BRAIN ALPHA PIPELINE — 7 LIBRARIES TEST RUN      ")
    print("=======================================================\n")

    overall_success = True
    summary = []

    all_lib_paths = [os.path.join(base_dir, lib) for lib in LIBRARIES]
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(all_lib_paths) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")

    for lib in LIBRARIES:
        lib_path = os.path.join(base_dir, lib)
        if not os.path.isdir(lib_path):
            print(f"[-] Skipping {lib}: directory not found")
            continue

        cmd = [python_exe, "-m", "pytest", "tests/", "-q"]
        result = subprocess.run(cmd, cwd=lib_path, env=env, capture_output=True, text=True)

        lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        last_line = lines[-1] if lines else result.stderr.strip()

        status = "PASS" if result.returncode == 0 else "FAIL"
        if result.returncode != 0:
            overall_success = False

        summary.append((lib, status, last_line))
        print(f"[{status}] {lib:<20} -> {last_line}")

    print("\n=======================================================")
    print("                      SUMMARY                          ")
    print("=======================================================")
    for lib, status, last_line in summary:
        print(f"  {lib:<20} : {status} ({last_line})")
    print("=======================================================\n")

    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
