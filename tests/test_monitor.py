
import subprocess
import sys
from pathlib import Path

MONITOR = Path(__file__).resolve().parents[1] / "monitor.py"


def run_monitor(directory, baseline, command):
    return subprocess.run(
        [
            sys.executable,
            str(MONITOR),
            command,
            "--directory",
            str(directory),
            "--baseline",
            str(baseline),
        ],
        capture_output=True,
        text=True,
    )


def setup_monitor(tmp_path):
    watched = tmp_path / "watched"
    watched.mkdir()

    example = watched / "example.txt"
    example.write_text("Original content", encoding="utf-8")

    baseline = tmp_path / "baseline.json"
    result = run_monitor(watched, baseline, "init")

    assert result.returncode == 0, result.stderr
    return watched, example, baseline


def test_unchanged_file(tmp_path):
    watched, example, baseline = setup_monitor(tmp_path)

    result = run_monitor(watched, baseline, "check")

    assert result.returncode == 0
    assert "PASS: No file changes detected" in result.stdout


def test_modified_file(tmp_path):
    watched, example, baseline = setup_monitor(tmp_path)

    example.write_text("Modified content", encoding="utf-8")
    result = run_monitor(watched, baseline, "check")

    assert result.returncode == 1
    assert "CHANGED: example.txt" in result.stdout


def test_added_file(tmp_path):
    watched, example, baseline = setup_monitor(tmp_path)

    new_file = watched / "new_file.txt"
    new_file.write_text("New file", encoding="utf-8")
    result = run_monitor(watched, baseline, "check")

    assert result.returncode == 1
    assert "ADDED: new_file.txt" in result.stdout


def test_deleted_file(tmp_path):
    watched, example, baseline = setup_monitor(tmp_path)

    example.unlink()
    result = run_monitor(watched, baseline, "check")

    assert result.returncode == 1
    assert "REMOVED: example.txt" in result.stdout
