#!/usr/bin/env python3
from __future__ import annotations
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
  python3 agent.py llm-generate       # Generate implementation through configured LLM
  python3 agent.py scan               # Just security scan
  python3 agent.py test               # Just run tests
  python3 agent.py track              # Just update progress + dashboard
"""
import sys
import os
import argparse
from pathlib import Path

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
    print(f"  Output gaps:     {stats['output_sanitization_gaps']}")
    if report["issues"]:
        print("\n  ISSUES:")
        for issue in report["issues"]:
            print(f"    [{issue['severity'].upper():8s}] {issue['pillar']:20s} {issue['file']}:{issue['line']} — {issue['description']}")
    print("━" * 50)
    return report


def run_tests(test_dir: str) -> dict:
    """Phase 4: Run evaluation tests."""
    from src.evaluation_runner import run_pytest

    print("\n🧪 PHASE 4: EVALUATION")
    print("━" * 50)
    result = run_pytest(test_dir)
    lines = result["output"].strip().splitlines()
    for line in lines[-20:]:
        print(f"  {line}")
    if result["error"]:
        print(f"  [!] {result['error']}")
    print(
        f"\n  Result: {len(result['passed'])} passed, {len(result['failed'])} failed, "
        f"{len(result['errors'])} errors"
    )
    print("━" * 50)
    return result


def run_track(
    spec_path: str,
    progress_path: str,
    test_dir: str,
    scenario_map_path: str,
    test_results: dict | None = None,
) -> dict:
    """Phase 5: Update progress and show dashboard."""
    from src.progress_tracker import update_progress, get_dashboard
    print("\n📊 PHASE 5: PROGRESS TRACKING")
    print("━" * 50)
    progress = update_progress(
        spec_path,
        progress_path,
        test_dir=test_dir,
        scenario_map_path=scenario_map_path,
        test_results=test_results,
    )
    if "update_skipped" in progress:
        print(f"  [!] Progress was not updated: {progress['update_skipped']['reason']}")
    dashboard = get_dashboard(progress_path)
    print(dashboard)
    return {"dashboard": dashboard, "updated": "update_skipped" not in progress}


def run_generate(spec_path: str, output_path: str, overwrite: bool = False) -> dict:
    """Phase 2: Generate a safe, traceable implementation scaffold."""
    from src.code_generator import generate_scaffold

    print("\n📝 PHASE 2: CODE GENERATION")
    print("━" * 50)
    result = generate_scaffold(spec_path, output_path, overwrite=overwrite)
    print(f"  Feature:     {result['feature']}")
    print(f"  Scenarios:   {result['scenarios']}")
    print(f"  Actions:     {', '.join(result['actions']) or 'scenario handlers'}")
    print(f"  Generated:   {result['output']}")
    print("━" * 50)
    return result


def run_llm_generate(
    spec_path: str,
    output_path: str,
    *,
    overwrite: bool = False,
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    dry_run: bool = False,
    output_contract: str | None = None,
    response_file: str | None = None,
) -> dict:
    """Generate reviewed implementation code through an environment-configured LLM."""
    from src.llm_core import (
        LLMError,
        LLMConfig,
        build_implementation_prompt,
        create_client,
        generate_with_llm,
        ReplayClient,
    )

    print("\n🧠 PHASE 2: LLM CODE GENERATION")
    print("━" * 50)
    selected_provider = provider or os.environ.get("SPEC_GUARD_LLM_PROVIDER", "gemini")
    selected_model = model or os.environ.get("SPEC_GUARD_LLM_MODEL", "gemini-2.5-flash")

    if dry_run:
        plan, prompt = build_implementation_prompt(spec_path, output_contract=output_contract)
        print("  Mode:        dry run (no provider request)")
        print(f"  Provider:    {selected_provider}")
        print(f"  Model:       {selected_model}")
        print(f"  Feature:     {plan['feature']}")
        print(f"  Scenarios:   {plan['scenarios_count']}")
        print(f"  Prompt size: {len(prompt)} characters")
        print(f"  Output:      {output_path}")
        print("  Guardrails:  fenced Python → parse → static security scan → atomic write")
        print("━" * 50)
        return {"success": True, "dry_run": True, "feature": plan["feature"]}

    try:
        if response_file:
            response_path = Path(response_file)
            client = ReplayClient(response_path.read_text(encoding="utf-8"), response_path.name)
        else:
            config = LLMConfig.from_environment(
                provider=provider,
                model=model,
                base_url=base_url,
            )
            client = create_client(config)
        result = generate_with_llm(
            spec_path,
            output_path,
            client,
            overwrite=overwrite,
            output_contract=output_contract,
        )
    except (LLMError, FileExistsError) as error:
        print(f"  [!] {error}")
        print("━" * 50)
        return {"success": False, "error": str(error)}

    print(f"  Provider:    {result['provider']}")
    print(f"  Model:       {result['model']}")
    print(f"  Feature:     {result['feature']}")
    print(f"  Scenarios:   {result['scenarios']}")
    print(f"  Warnings:    {result['security_warnings']}")
    print(f"  Generated:   {result['output']}")
    print("━" * 50)
    return {"success": True, **result}


def run_full_pipeline(
    spec_path: str,
    src_dir: str,
    test_dir: str,
    progress_path: str,
    scenario_map_path: str,
    check_packages: bool = True,
    generate: bool = False,
    output_path: str = "generated/feature_scaffold.py",
    overwrite: bool = False,
) -> int:
    """Run the full SpecGuard pipeline."""
    print()
    print("╔" + "═" * 50 + "╗")
    print("║" + "  SpecGuard — Spec-Driven Development Agent".center(50) + "║")
    print("╚" + "═" * 50 + "╝")

    # Phase 1: Analyze
    analyze_result = run_analyze(spec_path)

    if generate:
        run_generate(spec_path, output_path, overwrite=overwrite)
    else:
        print("\n📝 PHASE 2: CODE GENERATION")
        print("━" * 50)
        print("  Skipped by default to avoid overwriting implementation code.")
        print("  Run with --generate to create a traceable scaffold.")
        print("━" * 50)

    # Phase 3: Security scan. When a scaffold was just generated, scan that
    # artifact rather than accidentally reporting on unrelated framework code.
    scan_target = output_path if generate else src_dir
    scan_result = run_scan(scan_target, check_packages=check_packages)

    # Phase 4: Evaluation
    test_result = run_tests(test_dir)

    # Phase 5: Progress tracking
    track_result = run_track(spec_path, progress_path, test_dir, scenario_map_path, test_result)

    # Summary
    print("\n" + "╔" + "═" * 50 + "╗")
    print("║" + "  SUMMARY".center(50) + "║")
    print("╠" + "═" * 50 + "╣")
    print(f"║  Spec:       {analyze_result['scenarios_count']} scenarios".ljust(52) + "║")
    print(f"║  Warnings:   {len(analyze_result['warnings'])}".ljust(52) + "║")
    print(f"║  Security:   {scan_result['verdict']}".ljust(52) + "║")
    test_summary = (
        f"║  Tests:       {len(test_result['passed'])} passed, "
        f"{len(test_result['failed']) + len(test_result['errors'])} failed"
    )
    print(test_summary.ljust(52) + "║")
    print("╚" + "═" * 50 + "╝")
    print()
    return int(
        scan_result["verdict"] == "fail"
        or not test_result["available"]
        or not test_result["successful"]
        or not track_result["updated"]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="SpecGuard — Spec-Driven Development Agent")
    parser.add_argument("command", nargs="?", default="full",
                        choices=["full", "analyze", "generate", "llm-generate", "scan", "test", "track"],
                        help="Pipeline phase to run (default: full)")
    parser.add_argument("--spec", default="specs/task-manager.feature",
                        help="Path to Gherkin .feature file")
    parser.add_argument("--src", default="src/",
                        help="Source directory to scan")
    parser.add_argument("--tests", default="evals/",
                        help="Test directory")
    parser.add_argument("--progress", default="memory/progress.json",
                        help="Progress file path")
    parser.add_argument("--scenario-map", default="evals/scenario_map.json",
                        help="Explicit JSON mapping from scenarios to pytest node IDs")
    parser.add_argument("--generate", action="store_true",
                        help="Generate a safe implementation scaffold during the full pipeline")
    parser.add_argument("--output", default="generated/feature_scaffold.py",
                        help="Output path for the generated scaffold")
    parser.add_argument("--overwrite", action="store_true",
                        help="Allow the generate command to replace an existing output file")
    parser.add_argument("--llm-provider", choices=["gemini", "openai"],
                        help="LLM provider (default: SPEC_GUARD_LLM_PROVIDER or gemini)")
    parser.add_argument("--llm-model",
                        help="LLM model (default: SPEC_GUARD_LLM_MODEL or provider default)")
    parser.add_argument("--llm-base-url",
                        help="Override the provider API base URL; useful for compatible gateways")
    parser.add_argument("--dry-run", action="store_true",
                        help="For llm-generate: build and validate the request without an API call")
    parser.add_argument("--llm-contract",
                        help="Additional output contract for llm-generate, such as a required public API")
    parser.add_argument("--llm-response-file",
                        help="Offline replay response for deterministic demos; skips the provider request")
    parser.add_argument("--no-packages", action="store_true",
                        help="Skip PyPI package verification (offline mode)")

    args = parser.parse_args()

    check_pkgs = not args.no_packages

    if args.command == "full":
        return run_full_pipeline(
            args.spec,
            args.src,
            args.tests,
            args.progress,
            args.scenario_map,
            check_pkgs,
            generate=args.generate,
            output_path=args.output,
            overwrite=args.overwrite,
        )
    elif args.command == "analyze":
        run_analyze(args.spec)
        return 0
    elif args.command == "generate":
        run_generate(args.spec, args.output, overwrite=args.overwrite)
        return 0
    elif args.command == "llm-generate":
        output_path = args.output if args.output != "generated/feature_scaffold.py" else "generated/feature_llm.py"
        result = run_llm_generate(
            args.spec,
            output_path,
            overwrite=args.overwrite,
            provider=args.llm_provider,
            model=args.llm_model,
            base_url=args.llm_base_url,
            dry_run=args.dry_run,
            output_contract=args.llm_contract,
            response_file=args.llm_response_file,
        )
        return int(not result["success"])
    elif args.command == "scan":
        return int(run_scan(args.src, check_packages=check_pkgs)["verdict"] == "fail")
    elif args.command == "test":
        result = run_tests(args.tests)
        return int(not result["available"] or not result["successful"])
    elif args.command == "track":
        result = run_track(args.spec, args.progress, args.tests, args.scenario_map)
        return int(not result["updated"])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
