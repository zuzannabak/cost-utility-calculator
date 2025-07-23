"""
Module entry-point so you can run:

    python -m cucal.validate dragut --budget 1500 --time 24

It simply dispatches to the corresponding script and forwards CLI flags.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _usage() -> None:
    print(
        "Usage: python -m cucal.validate <case> [--budget ... --time ... --eff ...]\n"
        "Currently supported cases:  dragut"
    )
    sys.exit(1)


def main() -> None:  # noqa: D401  (simple main wrapper)
    if len(sys.argv) < 2:
        _usage()

    case = sys.argv[1].lower()

    if case == "dragut":
        # Remove the case token so validate_dragut.py sees only its own flags
        sys.argv = [sys.argv[0]] + sys.argv[2:]

        script = (
            Path(__file__).resolve().parents[2]
            / "scripts"
            / "validate_dragut.py"
        )
        runpy.run_path(str(script), run_name="__main__")

    else:
        print(f"Unknown validation case '{case}'\n")
        _usage()


if __name__ == "__main__":  # pragma: no cover
    main()
