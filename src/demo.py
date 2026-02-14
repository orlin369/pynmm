from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    # Ensure `src/` is importable even if executed from repo root with a different CWD.
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    try:
        from morris_textual import MorrisApp
    except Exception as e:
        print("Textual UI not available.")
        print("Install Textual: python -m pip install textual")
        print(f"Error: {e}")
        return

    MorrisApp().run()


if __name__ == "__main__":
    main()
