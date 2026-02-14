# Changelog

All notable changes to this project will be documented in this file.

The format is based on *Keep a Changelog* and this project aims to follow *Semantic Versioning*.

## [Unreleased]

### Added
- Python Nine Men's Morris engine + AI search under `src/artifitial_inteligence/`.
- Textual terminal UI under `src/morris_textual.py` and runnable entrypoint `src/demo.py`.
- Packaging for `pip install` (PEP 517/518) via `pyproject.toml`, plus `pynmm` wrapper package and `pynmm-tui` entrypoint.

### Changed
- Refactored code organization: enums moved into `artifitial_inteligence/enums/` and dataclasses into `artifitial_inteligence/models/` (with compatibility shims for old imports). TUI code split across `pynmm/tui_*.py`.

### Fixed
- Textual TUI crash on startup when running `src/demo.py` due to dataclass mutable defaults (`GameSession.eval_settings` / `GameSession.board`).
- Textual TUI side log now scrolls and auto-scrolls as new lines are appended.

### Removed

