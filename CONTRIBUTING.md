# Contributing

This repo is a Python Nine Men's Morris engine + AI with a Textual terminal UI under `src/`.

## Quick Start

- Python version: 3.12+ is recommended (the project currently runs on 3.12).
- Optional UI dependency: `python -m pip install textual`
- Run the terminal UI: `python src\demo.py`

## Project Conventions

- Keep behavior parity first.
- If you refactor, do it only after rules, move generation, evaluation scoring, and API entrypoints are correct.
- Preserve familiar naming when it helps cross-referencing (including original misspellings like `artifitial_inteligence`).
- Keep UI logic deterministic.
- The UI should validate moves by matching against `Board.get_moves()` output, not by re-implementing legality.
- Keep optional dependencies optional.
- `textual` should remain isolated to `src/morris_textual.py` and fail gracefully when missing.

## Branching And Git Workflow (Required)

- Do not commit directly to `main`.
- Use a long-lived integration branch named `develop`.
- Create feature work from `develop`:
- `feature/<short-topic>` for new work
- `fix/<short-topic>` for bug fixes
- `chore/<short-topic>` for non-behavioral maintenance
- Keep branches short-lived and scoped (one topic per branch).
- Open a PR into `develop` for review.
- Keep `develop` green and releasable.
- Release flow:
- Merge `develop` into `main` via PR when you are ready to release.
- Tag releases (optional but recommended): `vX.Y.Z`.

Suggested commands:

```powershell
git checkout develop
git pull
git checkout -b feature/your-topic
```

Update branch with latest `develop` (pick one approach and be consistent):

```powershell
# Rebase onto latest develop (clean history)
git fetch
git rebase origin/develop

# Or merge develop into your branch (preserve merge commits)
git fetch
git merge origin/develop
```

## Change Tracking (Required)

- Update `CHANGELOG.md` for every user-facing change (rules, AI behavior, public API, UI commands, run instructions, dependencies, layout).
- Put changes in `## [Unreleased]` under one of: `Added`, `Changed`, `Fixed`, `Removed`.
- For a release, move `[Unreleased]` items into `## X.Y.Z - YYYY-MM-DD`.

## Testing And Sanity Checks

- Import check: `python -c "import sys; sys.path.insert(0,'src'); import artifitial_inteligence"`
- Smoke run (after installing Textual): `python src\demo.py`
- Manual spot-check after changes:
- Stage transitions: stage 1 if any unplaced > 0; stage 3 if either player placed < 4; else stage 2
- Mill detection and capture legality (including the "all opponent pieces are in mills" exception)
- Win detection (opponent has < 3 pieces after placement is finished, and/or opponent is blocked)
- `moves` output matches the moves the command parser accepts

## Pull Request Checklist

- `CHANGELOG.md` updated (required for behavior/API/UI/docs changes).
- No new hard dependencies added to the core library (`src/artifitial_inteligence/`).
- If you changed rules or move generation: include at least one reproducible example position and expected move(s) in the PR description.
- Avoid committing generated files (`__pycache__/`, `*.pyc`).
- Keep changes small and reviewable; avoid sweeping rewrites without tests.

## Commit Guidance

- Keep commits focused and descriptive.
- Prefer imperative subject lines like: `Fix capture exception rule in stage 2`.
- If a commit changes behavior, it must also update `CHANGELOG.md`.
