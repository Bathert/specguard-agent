#!/usr/bin/env python3
"""
SpecGuard CLI — Spec-Driven Development Agent

Full pipeline:
  1. Analyze Gherkin spec → plan
  2. Run security scan on generated code
  3. Run evaluation tests
  4. Update progress tracker
  5. Print dashboard

Usage:
  python3 agent.py                    # Full pipeline with defaults
  python3 agent.py --spec specs/X.feature
  python3 agent.py analyze            # Just analyze spec
  python3 agent.py scan               # Just security scan
  python3 agent.py test               # Just run tests
  python3 agent.py track              # Just update progress + dashboard
"""
import sys
import os
import json
import argparse
import subprocess

# Ensure src/ is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_analyze(spec_path: str) -> dict:
    """Phase 1: Parse and validate spec."""
    from src.spec_analyzer import analyze_spec
    print("\n📋 PHASE 1: SPEC ANALYSIS")
    print("━" * 50)
    result = analyze_spec(spec_path)
    print(f"  Feature:     {result['feature']}")
    print(f"  Scenarios:   {result['scenarios_count']}")
    print(f"  Warnings:    {len(result['warnings'])}")
    if result["warnings"]:
        for w in result["warnings"]:
            print(f"    [!] {w}")
    print(f"  Tasks:       {len(result['tasks'])}")
    print("━" * 50)
    return result


def run_scan(src_dir: str, check_packages: bool = True) -> dict:
    """Phase 3: Security scan."""
    from src.security_scanner import scan_directory
    print("\n🔒 PHASE 3: SECURITY SCAN")
    print("━" * 50)
    report = scan_directory(src_dir, check_packages=check_packages)
    stats = report["stats"]
    print(f"  Verdict:         {report['verdict']}")
    print(f"  Files scanned:   {report['files_scanned']}")
    print(f"  Critical:        {stats['critical']}")
    print(f"  High:            {stats['high']}")
    print(f"  Medium:          {stats['medium']}")
    print(f"  Low:             {stats['low']}")
    print(f"  Secrets:         {stats['secrets_found']}")
    print(f"  Injections:      {stats['injections_found']}")
    print(f"  Validation gaps: {stats['validation_gaps']}")
    if report["issues"]:
        print("\n  ISSUES:")
        for issue in report["issues"]:
            print(f"    [{issue['severity'].upper():8s}] {issue['pillar']:20s} {issue['file']}:{issue['line']} — {issue['description']}")
    print("━" * 50)
    return report


def run_tests(test_dir: str) -> dict:
    """Phase 4: Run evaluation tests."""
    print("\n🧪 PHASE 4: EVALUATION")
    print("━" * 50)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_dir, "-v", "--tb=short"],
            capture_output=True, text=True, timeout=30,
        )
        output = result.stdout + result.stderr
        # Print last 20 lines of test output
        lines = output.strip().splitlines()
        for line in lines[-20:]:
            print(f"  {line}")
        passed = sum(1 for l in lines if " PASSED" in l)
        failed = sum(1 for l in lines if " FAILED" in l)
        print(f"\n  Result: {passed} passed, {failed} failed")
        print("━" * 50)
        return {"passed": passed, "failed": failed, "output": output}
    except FileNotFoundError:
        print("  [!] pytest not found. Install: pip3 install pytest")
        print("━" * 50)
        return {"passed": 0, "failed": 0, "error": "pytest not found"}
    except Exception as e:
        print(f"  [!] Error: {e}")
        print("━" * 50)
        return {"passed": 0, "failed": 0, "error": str(e)}


def run_track(spec_path: str, progress_path: str) -> dict:
    """Phase 5: Update progress and show dashboard."""
    from src.progress_tracker import update_progress, get_dashboard
    print("\n📊 PHASE 5: PROGRESS TRACKING")
    print("━" * 50)
    update_progress(spec_path, progress_path)
    dashboard = get_dashboard(progress_path)
    print(dashboard)
    return {"dashboard": dashboard}


def run_full_pipeline(spec_path: str, src_dir: str, test_dir: str, progress_path: str, check_packages: bool = True):
    """Run the full SpecGuard pipeline."""
    print()
    print("╔" + "═" * 50 + "╗")
    print("║" + "  SpecGuard — Spec-Driven Development Agent".center(50) + "║")
    print("╚" + "═" * 50 + "╝")

    # Phase 1: Analyze
    analyze_result = run_analyze(spec_path)

    # Phase 2: Code generation status (check if src/ exists)
    print("\n📝 PHASE 2: CODE STATUS")
    print("━" * 50)
    py_files = []
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache", ".git")]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    print(f"  Source files: {len(py_files)}")
    for f in py_files:
        size = os.path.getsize(f)
        print(f"    {f} ({size} bytes)")
    print("━" * 50)

    # Phase 3: Security scan
    scan_result = run_scan(src_dir, check_packages=check_packages)

    # Phase 4: Evaluation
    test_result = run_tests(test_dir)

    # Phase 5: Progress tracking
    track_result = run_track(spec_path, progress_path)

    # Summary
    print("\n" + "╔" + "═" * 50 + "╗")
    print("║" + "  SUMMARY".center(50) + "║")
    print("╠" + "═" * 50 + "╣")
    print(f"║  Spec:       {analyze_result['scenarios_count']} scenarios".ljust(52) + "║")
    print(f"║  Warnings:   {len(analyze_result['warnings'])}".ljust(52) + "║")
    print(f"║  Security:   {scan_result['verdict']}".ljust(52) + "║")
    print(f"║  Tests:       {test_result['passed']} passed, {test_result['failed']} failed".ljust(52) + "║")
    print("╚" + "═" * 50 + "╝")
    print()


def main():
    parser = argparse.ArgumentParser(description="SpecGuard — Spec-Driven Development Agent")
    parser.add_argument("command", nargs="?", default="full",
                        choices=["full", "analyze", "scan", "test", "track"],
                        help="Pipeline phase to run (default: full)")
    parser.add_argument("--spec", default="specs/task-manager.feature",
                        help="Path to Gherkin .feature file")
    parser.add_argument("--src", default="src/",
                        help="Source directory to scan")
    parser.add_argument("--tests", default="evals/",
                        help="Test directory")
    parser.add_argument("--progress", default="memory/progress.json",
                        help="Progress file path")
    parser.add_argument("--no-packages", action="store_true",
                        help="Skip PyPI package verification (offline mode)")

    args = parser.parse_args()

    check_pkgs = not args.no_packages

    if args.command == "full":
        run_full_pipeline(args.spec, args.src, args.tests, args.progress, check_pkgs)
    elif args.command == "analyze":
        run_analyze(args.spec)
    elif args.command == "scan":
        run_scan(args.src, check_packages=check_pkgs)
    elif args.command == "test":
        run_tests(args.tests)
    elif args.command == "track":
        run_track(args.spec, args.progress)


if __name__ == "__main__":
    main()