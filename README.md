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

3. In-game commands:

- `help`
- `new ai` (play vs machine)
- `new pvp` (two players on one computer)
- `drop A1` or `drop A1 cap D1`
- `move A1 D1` or `move A1 D1 cap B2`
- `moves`

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


