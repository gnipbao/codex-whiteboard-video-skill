#!/usr/bin/env python3
"""Run the installed whiteboard-video-engine CLI.

This Codex skill intentionally does not vendor the engine. Install the engine
first, then this wrapper forwards all arguments to `whiteboard_skill.cli`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


INSTALL_HELP = """
whiteboard-video-engine is not installed.

Install the engine first:

  python3 -m pip install "git+https://github.com/gnipbao/whiteboard-video-engine.git"

For local development:

  python3 -m pip install -e /path/to/whiteboard-video-engine

If the engine is installed in a virtual environment, invoke this wrapper with
that environment's Python or set WHITEBOARD_ENGINE_PYTHON.

Then retry this skill command.
""".strip()


def main() -> int:
    configured_python = os.getenv("WHITEBOARD_ENGINE_PYTHON")
    if configured_python:
        # Keep the virtual-environment symlink intact: resolving it to the base
        # interpreter would discard the venv's site-packages.
        candidate = Path(configured_python).expanduser().absolute()
        current = Path(sys.executable).absolute()
        if candidate != current:
            if not candidate.is_file():
                print(f"WHITEBOARD_ENGINE_PYTHON does not exist: {candidate}", file=sys.stderr)
                return 1
            os.execv(str(candidate), [str(candidate), str(Path(__file__).resolve()), *sys.argv[1:]])
    try:
        from whiteboard_skill.cli import main as engine_main
    except ModuleNotFoundError as exc:
        if exc.name == "whiteboard_skill":
            print(INSTALL_HELP, file=sys.stderr)
            return 1
        raise
    return int(engine_main())


if __name__ == "__main__":
    raise SystemExit(main())
