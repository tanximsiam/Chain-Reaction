# Chain Reaction

A 2-8 player Chain Reaction game built with Python and [Arcade](https://api.arcade.academy/) 3.

## Rules

- Players take turns adding an atom to an empty cell or one of their own.
- A cell explodes when it holds as many atoms as it has neighbours (corner 2, edge 3, middle 4),
  sending one atom to each neighbour and capturing those cells.
- Explosions chain. A player with no atoms left (after their first move) is out.
- The last player with atoms wins.

## Run

```bash
python -m venv venv
venv/bin/pip install -r requirements.txt   # Windows: venv\Scripts\pip
venv/bin/python main.py
```

### Live preview (development)

```bash
venv/bin/python tools/live_preview.py
```

Open http://localhost:8765 to play the game in a browser. It restarts whenever a `.py` file changes and shows the current branch and uncommitted files.

## Controls

| Where | Input | Action |
|---|---|---|
| Menu | Click / Left, Right / 2-8 | Choose player count |
| Menu | Enter or Space | Start |
| Game | Click a cell | Place an atom |
| Game | R | Restart |
| Game | Esc | Back to menu |

## Code layout

| File | Responsibility |
|---|---|
| `board.py` | Game rules only: board, explosion waves, turns, elimination |
| `game_view.py` | Sprite board, explosion animation, HUD and game-over panel |
| `menu_view.py` | Start menu |
| `ui_theme.py` | Fonts and `arcade.gui` button styles |
| `constants.py` | Board size, layout and colours |

## Tests

```bash
python -m unittest test_board
```
