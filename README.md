# NineMensMorrisAI Python Port

This repo contains a Python translation of the C# library in `NineMensMorrisAI/`.
Repo:
```text
https://github.com/orlin369/NineManMorris
```

## Textual terminal game

Inspired by the Textual TUI framework:
```text
https://textual.textualize.io/
```

1. Install Textual:

   ```powershell
   python -m pip install textual
   ```

2. Run the game:

   ```powershell
   python src\demo.py
   ```

## How To Play (Terminal UI)

1. Start a new game:
- `new ai` (you vs AI)
- `new pvp` (two players on one computer)

2. Place a piece (stage 1):
- `drop A1`
- If it forms a mill and you must capture: `drop A1 cap D1`

3. Move a piece (stage 2, and stage 3 flying):
- `move A1 D1`
- If it forms a mill and you must capture: `move A1 D1 cap B2`

4. Other useful commands:
- `moves` shows legal moves (use this when unsure what is allowed)
- `set depth 3` (AI search depth, ai mode)
- `set time 200` (AI time limit ms, ai mode)
- `help`
- `quit`

5. Position names:
`A1 D1 G1 / B2 D2 F2 / C3 D3 E3 / A4 B4 C4 E4 F4 G4 / C5 D5 E5 / B6 D6 F6 / A7 D7 G7`

## In-game commands (quick)

- `help`
- `new ai` (play vs machine)
- `new pvp` (two players on one computer)
- `drop A1` or `drop A1 cap D1`
- `move A1 D1` or `move A1 D1 cap B2`
- `moves`

## Install from git (library)

Install from GitHub:

```powershell
python -m pip install "pynmm @ git+https://github.com/orlin369/pynmm.git@dev"
```

Optional Textual UI:

```powershell
python -m pip install "pynmm[tui] @ git+https://github.com/orlin369/pynmm.git@dev"
```

Run the UI after install:

```powershell
pynmm-tui
```

## Library usage (direct)

```python
from artifitial_inteligence import GameController

positions = [0] * 24
white_id = 1
black_id = 2

ai = GameController(time_limit_ms=200, depth=3)
move = ai.pass_board(positions, white=white_id, black=black_id)
print(move)
```


