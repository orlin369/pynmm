# AGENTS.md

This repo contains a Python Nine Men's Morris engine + AI plus a Textual terminal UI (under `src/`).

**Working Agreements**
- Keep translations behavior-first: match rules, move generation, evaluation scoring, and API entrypoints before refactors.
- Preserve familiar naming where it helps cross-referencing (including original misspellings like `ArtifitialInteligence`).
- Prefer small, reviewable changes; avoid sweeping rewrites without tests.

**Contributing**
- Follow `CONTRIBUTING.md` for best practices and the change checklist.
- Treat `CHANGELOG.md` updates as mandatory per the rules below.
- Branching workflow is mandatory: feature work must go through `develop` via local merges (no pull requests, no direct commits to `main`).

**Change Tracking (Changelog)**
- Maintain `CHANGELOG.md` in Keep a Changelog format (`[Unreleased]` with `Added/Changed/Fixed/Removed`).
- Update `CHANGELOG.md` for every change that affects any of:
  - game rules, move generation, mill/capture logic, win detection
  - evaluation/scoring, search, time/depth behavior
  - public API surface (imports, function signatures, enums/values)
  - UI commands/rendering/help text
  - run instructions, dependencies, repo layout
- Do not merge “behavior changes” without an entry under `[Unreleased]`.
- When cutting a release, move the entries from `[Unreleased]` into `## X.Y.Z - YYYY-MM-DD`.

**Python Package Layout**
- Keep the core library isolated in `src/artifitial_inteligence/`.
- Keep `src/demo.py` as the runnable entrypoint for terminal UX.
- Keep UI code in `src/morris_textual.py` so the library can be used headless.

**Textual Terminal UI Practices**
- Keep the UI command-driven and deterministic: validate moves by matching against `Board.get_moves()` output rather than re-implementing legality.
- Keep rendering stable: fixed ASCII layout and show each node with occupant suffix (e.g. `A1W`, `D1.`).
- Fail gracefully on optional deps: if `textual` is missing, print an install hint and exit cleanly.

**Testing And Sanity Checks**
- Quick import check: `python -c "import sys; sys.path.insert(0,'src'); import artifitial_inteligence"`
- Quick UI run (after installing Textual): `python src\\demo.py`
- Core behavior to spot-check after changes: move generation per stage, mill detection + capture legality, win detection (opponent < 3 pieces after stage 1, and blocked opponent).

**Repo Hygiene**
- Prefer `rg` for searching.
- Avoid destructive git commands unless explicitly requested.
- Don't introduce dependencies into the core library; keep UI dependencies optional and isolated.
