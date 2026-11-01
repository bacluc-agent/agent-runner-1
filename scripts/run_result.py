import re
import sys
from pathlib import Path


def main() -> int:
    source, destination = map(Path, sys.argv[1:3])
    status, mode = int(sys.argv[3]), sys.argv[4]
    output = source.read_text(errors="replace").strip() if source.exists() else ""
    succeeded = status == 0 and (mode == "smoke" or bool(output))
    outcome = "valid no-op/smoke" if succeeded and mode == "smoke" else "work produced" if succeeded else "failure"
    fence = "`" * max(3, max((len(match.group()) for match in re.finditer(r"`+", output)), default=0) + 1)
    report = f"# Agent run result\n\nOutcome: {outcome}\n\nCoordinator exit status: {status}\n\n## Coordinator output\n\n{fence}text\n{output or '(no output)'}\n{fence}\n"
    destination.write_text(report)
    return 0 if succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
