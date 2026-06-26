#!/usr/bin/env python3
"""Run the installed whiteboard-video-engine CLI.

This Codex skill intentionally does not vendor the engine. Install the engine
first, then this wrapper forwards all arguments to `whiteboard_skill.cli`.
"""

from __future__ import annotations

import sys


INSTALL_HELP = """
whiteboard-video-engine is not installed.

Install the engine first:

  python3 -m pip install "git+https://github.com/gnipbao/whiteboard-video-engine.git"

For local development:

  python3 -m pip install -e /path/to/whiteboard-video-engine

Then retry this skill command.
""".strip()


def main() -> int:
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
