import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("run_result.py")


def run(tmp_path, *, status, mode, output=None):
    source = tmp_path / "coordinator.out"
    result = tmp_path / "run-result.md"
    if output is not None:
        source.write_text(output)
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(source), str(result), str(status), mode],
        capture_output=True,
        text=True,
    )
    return completed, result.read_text() if result.exists() else ""


def test_substantive_output_is_saved(tmp_path):
    completed, report = run(
        tmp_path,
        status=0,
        mode="work",
        output=events(
            text("msg-earlier", "Earlier assistant text"),
            finish("msg-earlier"),
            tool("msg-tool", "tool content should not persist"),
            text("msg-final", "Review completed"),
            finish("msg-final"),
        ),
    )
    assert completed.returncode == 0
    assert "Outcome: work produced" in report
    assert "Review completed" in report
    assert "Earlier assistant text" not in report
    assert "tool content should not persist" not in report


def test_successful_no_code_change_can_have_a_result(tmp_path):
    completed, report = run(
        tmp_path,
        status=0,
        mode="work",
        output=events(text("msg-final", "No changes needed"), finish("msg-final")),
    )
    assert completed.returncode == 0
    assert "Outcome: work produced" in report
    assert "No changes needed" in report


def test_explicit_smoke_is_distinct(tmp_path):
    completed, report = run(tmp_path, status=0, mode="smoke", output="")
    assert completed.returncode == 0
    assert "Outcome: valid no-op/smoke" in report


def test_missing_substantive_result_fails(tmp_path):
    completed, report = run(tmp_path, status=0, mode="work", output="")
    assert completed.returncode != 0
    assert "Outcome: failure" in report


def test_process_failure_is_not_success(tmp_path):
    completed, report = run(
        tmp_path,
        status=1,
        mode="work",
        output=events(text("msg-final", "partial"), finish("msg-final")),
    )
    assert completed.returncode != 0
    assert "Outcome: failure" in report


def test_missing_source_file_fails(tmp_path):
    completed, report = run(tmp_path, status=0, mode="work")
    assert completed.returncode != 0
    assert "Outcome: failure" in report


def test_invalid_run_mode_fails(tmp_path):
    completed, report = run(
        tmp_path,
        status=0,
        mode="workk",
        output=events(text("msg-final", "result"), finish("msg-final")),
    )
    assert completed.returncode != 0
    assert "Outcome: failure" in report


def events(*items):
    return "\n".join(json.dumps(item) for item in items)


def text(message_id, content):
    return {
        "type": "text",
        "part": {"type": "text", "messageID": message_id, "text": content},
    }


def finish(message_id):
    return {
        "type": "step_finish",
        "part": {"type": "step-finish", "messageID": message_id, "reason": "stop"},
    }


def tool(message_id, content):
    return {
        "type": "tool_use",
        "part": {"type": "tool", "messageID": message_id, "state": {"output": content}},
    }


def test_credential_like_tool_output_is_not_saved(tmp_path):
    secret_marker = "sk-test-credential-marker"
    completed, report = run(
        tmp_path,
        status=0,
        mode="work",
        output=events(tool("msg-tool", secret_marker), text("msg-final", "Task complete"), finish("msg-final")),
    )
    assert completed.returncode == 0
    assert "Task complete" in report
    assert secret_marker not in report
