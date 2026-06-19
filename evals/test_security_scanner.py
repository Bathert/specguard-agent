from src.security_scanner import scan_directory, scan_injections, scan_output_sanitization


def test_output_sanitization_flags_interpolated_html():
    issues = scan_output_sanitization(
        ['return f"<div>{user_input}</div>"\n'],
        "fixture.py",
    )

    assert len(issues) == 1
    assert issues[0].pillar == "output_sanitization"
    assert issues[0].severity == "high"


def test_injection_scanner_allows_list_based_python_subprocess_calls():
    issues = scan_injections(
        [
            "command = [sys.executable, '-m', 'pytest', test_dir]\n",
            "subprocess.run(command, check=False)\n",
        ],
        "fixture.py",
    )

    assert issues == []


def test_directory_scanner_accepts_a_single_python_file(tmp_path):
    target = tmp_path / "safe.py"
    target.write_text("def safe() -> None:\n    return None\n", encoding="utf-8")

    report = scan_directory(str(target), check_packages=False)

    assert report["files_scanned"] == 1
