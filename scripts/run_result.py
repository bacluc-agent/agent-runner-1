import json
import sys
from pathlib import Path


def main() -> int:
    source, destination = map(Path, sys.argv[1:3])
    status, mode = int(sys.argv[3]), sys.argv[4]
    output = ""
    if source.exists():
        try:
            events = [json.loads(line) for line in source.read_text().splitlines() if line.strip()]
        except (json.JSONDecodeError, OSError):
            events = []
        final_message_id = next(
            (
                event.get("part", {}).get("messageID")
                for event in reversed(events)
                if event.get("type") == "step_finish" and event.get("part", {}).get("reason") == "stop"
            ),
            None,
        )
        output = "\n".join(
            event["part"]["text"]
            for event in events
            if event.get("type") == "text"
            and event.get("part", {}).get("messageID") == final_message_id
            and isinstance(event.get("part", {}).get("text"), str)
        ).strip()
    if mode not in {"work", "smoke"}:
        status = status or 1
        mode = "invalid"
    succeeded = status == 0 and (mode == "smoke" or bool(output))
    outcome = "valid no-op/smoke" if succeeded and mode == "smoke" else "work produced" if succeeded else "failure"
    result_summary = "Coordinator produced non-empty output." if output else "Coordinator produced no output."
    report = f"# Agent run result\n\nOutcome: {outcome}\n\nCoordinator exit status: {status}\n\n{result_summary}\n"
    if succeeded and mode == "work":
        report += f"\n## Coordinator result\n\n{output}\n"
    destination.write_text(report)
    return 0 if succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
