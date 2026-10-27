# Chain Reaction

A 2-8 player Chain Reaction game built with Python and [Arcade](https://api.arcade.academy/) 3.

## Download

Get the latest build from [Releases](https://github.com/tanximsiam/Chain-Reaction/releases/latest), or from the [game page](https://tanximsiam.github.io/Chain-Reaction/).

- **Windows**: download `ChainReaction-windows.exe` and run it. SmartScreen may warn because the exe is unsigned: choose *More info → Run anyway*.
- **Linux**: download `ChainReaction-linux.tar.gz`, then `tar -xzf ChainReaction-linux.tar.gz && ./ChainReaction`. Needs OpenGL 3.3.

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

Open http://localhost:8765 to play the game in a browser. It restarts whenever a `.py` file changes.

## Controls

| Where | Input | Action |
|---|---|---|
| Menu | Click / Left, Right / 2-8 | Choose player count |
| Menu | Enter or Space | Start |
| Game | Click a cell | Place an atom |
| Game | R | Restart |
| Game | Esc or P | Pause / resume (pause menu: Resume, Main menu, Exit to desktop, Sound, Music) |

## Code layout

| File | Responsibility |
|---|---|
| `board.py` | Game rules only: board, explosion waves, turns, elimination |
| `board_sprites.py` | `BoardSprites`: tiles, atoms and explosion animation for any Board, at any size |
| `game_view.py` | Game flow, HUD and game-over panel |
| `menu_view.py` | Start menu (players, Play, sound/music, How to play, Quit) |
| `manual_view.py` | How to play, with looping demo boards (critical mass, capture, chain) |
| `ui_theme.py` | Fonts, colours and rounded nine-patch textures |
| `widgets.py` | `BevelButton` (animated bevelled button) and rounded panels |
| `audio.py` | Sound effects, music and their on/off settings |
| `icons.py` | Stroke icon set rendered once with PIL |
| `constants.py` | Board size, layout and colours |

## Build

```bash
venv/bin/pip install pyinstaller
venv/bin/pyinstaller --noconfirm ChainReaction.spec   # one-file binary in dist/
```

Pushing a tag like `v1.0.0` runs `.github/workflows/release.yml`, which builds Windows and Linux binaries and attaches them to a GitHub release.

## Tests

```bash
python -m unittest test_board
```
