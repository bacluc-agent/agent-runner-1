import sys
from pathlib import Path


def main() -> int:
    source, destination = map(Path, sys.argv[1:3])
    status, mode = int(sys.argv[3]), sys.argv[4]
    output = source.read_text(errors="replace").strip() if source.exists() else ""
    if mode not in {"work", "smoke"}:
        status = status or 1
        mode = "invalid"
    succeeded = status == 0 and (mode == "smoke" or bool(output))
    outcome = "valid no-op/smoke" if succeeded and mode == "smoke" else "work produced" if succeeded else "failure"
    report = f"# Agent run result\n\nOutcome: {outcome}\n\nCoordinator exit status: {status}\n\nCoordinator output is not retained because it may contain tool output or credentials.\n"
    destination.write_text(report)
    return 0 if succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
