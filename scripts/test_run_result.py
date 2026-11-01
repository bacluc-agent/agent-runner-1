import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("run_result.py")


def run(tmp_path, *, status, mode, output):
    source = tmp_path / "coordinator.out"
    result = tmp_path / "run-result.md"
    source.write_text(output)
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(source), str(result), str(status), mode],
        capture_output=True,
        text=True,
    )
    return completed, result.read_text() if result.exists() else ""


def test_substantive_output_is_saved(tmp_path):
    completed, report = run(tmp_path, status=0, mode="work", output="Review completed")
    assert completed.returncode == 0
    assert "Outcome: work produced" in report
    assert "Review completed" in report


def test_successful_no_code_change_can_have_a_result(tmp_path):
    completed, report = run(tmp_path, status=0, mode="work", output="No changes needed")
    assert completed.returncode == 0
    assert "Outcome: work produced" in report


def test_explicit_smoke_is_distinct(tmp_path):
    completed, report = run(tmp_path, status=0, mode="smoke", output="ok")
    assert completed.returncode == 0
    assert "Outcome: valid no-op/smoke" in report


def test_missing_substantive_result_fails(tmp_path):
    completed, report = run(tmp_path, status=0, mode="work", output=" \n")
    assert completed.returncode != 0
    assert "Outcome: failure" in report


def test_process_failure_is_not_success(tmp_path):
    completed, report = run(tmp_path, status=1, mode="work", output="partial")
    assert completed.returncode != 0
    assert "Outcome: failure" in report
