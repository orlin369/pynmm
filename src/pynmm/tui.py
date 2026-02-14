from __future__ import annotations


def main() -> None:
    """Launch the optional Textual terminal UI.

    Install with:
      pip install "pynmm[tui]"
    """

    try:
        from morris_textual import MorrisApp
    except Exception as e:
        print("Textual UI not available.")
        print('Install with: python -m pip install "pynmm[tui]"')
        print(f"Error: {e}")
        return

    MorrisApp().run()

