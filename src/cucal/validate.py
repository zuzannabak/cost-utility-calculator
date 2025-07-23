"""
Python module entry-point so users can run:

    python -m cucal.validate dragut
"""
import importlib, sys

def _usage() -> None:
    print("Usage: python -m cucal.validate dragut [--budget ... --time ... --eff ...]")
    sys.exit(1)

def main() -> None:        # noqa: D401  (simple main wrapper)
    if len(sys.argv) < 2:
        _usage()

    case = sys.argv[1].lower()
    if case == "dragut":
        from pathlib import Path
        # defer import until needed (keeps deps light)
        script = Path("scripts/validate_dragut.py")
        # Forward all flags after the case name
        import runpy
        runpy.run_path(str(script), run_name="__main__")
    else:
        print(f"Unknown validation case '{case}'")
        _usage()

if __name__ == "__main__":  # pragma: no cover
    main()
