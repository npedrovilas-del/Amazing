*This project has been created as part of the 42 curriculum by pneto-vi, nfardim.*

# A-Maze-ing

## Warning
The dependencies in the Makefile are configured for Ubuntu (sudo apt). If you are using a different operating system, please update the installation commands accordingly before running the setup.

## Description

A-Maze-ing is a Python maze generator. Given a simple configuration file,
it generates a maze (perfect or with loops), validates it against a set
of structural rules (no walls wider than 2x2, coherent walls between
neighbouring cells, a visible "42" pattern), computes the shortest path
between the entry and the exit, and writes everything to an output file
using a compact hexadecimal wall representation. The program also
provides an interactive ASCII visualisation of the maze in the terminal.

The maze generation logic itself is implemented as a standalone,
reusable Python module (`mazegen`) that can be installed independently
and imported into other projects.

## Instructions

### Requirements

- Python 3.10 or later
- `flake8` and `mypy` (for linting, installed via `make install`)
- `build` (for packaging the `mazegen` module, installed via `make install`)

### Running the project

```bash
make install     # installs flake8, mypy and build
make run          # runs the program with the default config.txt
make debug        # runs the program under pdb
make clean        # removes __pycache__ and .mypy_cache
make lint         # runs flake8 and mypy
make lint-strict  # runs flake8 and mypy --strict
make mlx          # compiles the MLX display (mlx_display)
```

You can also run it manually:

```bash
python3 a_maze_ing.py config.txt
```

`config.txt` can be replaced by any configuration file following the
format described below.

### Building the reusable `mazegen` package

```bash
make build
```

This generates `mazegen-1.0.0-py3-none-any.whl` (and a `.tar.gz`) at the
root of the repository, ready to be installed with `pip install
mazegen-1.0.0-py3-none-any.whl` in any other project.

### MLX display

`make mlx` compiles `mlx_display.c` into `mlx_display` using the bundled
`minilibx_linux` (requires the X11 development libraries on the system).
The MLX display is not a Python dependency and is not installed via pip.

From the menu, option `4. Launch MLX display` runs it with the generated
maze file. The window shows the maze with the entry/exit highlighted and
the shortest path overlaid; it hot-reloads when the maze file changes and
reads `maze.txt.show` / `maze.txt.color` to toggle the path and change
the wall color.

## Configuration file format

The configuration file is a plain text file with one `KEY=VALUE` pair
per line. Lines starting with `#` are treated as comments and ignored.

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width, in cells | `WIDTH=20` |
| `HEIGHT` | Maze height, in cells | `HEIGHT=15` |
| `ENTRY` | Entry coordinates `x,y` | `ENTRY=0,0` |
| `EXIT` | Exit coordinates `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | Name of the output file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | `True` for a perfect maze (single path), `False` to add extra loops | `PERFECT=True` |
| `SEED` (optional) | Integer seed for reproducible generation. Defaults to `42` if omitted | `SEED=42` |

Example:

```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

All values are validated: `WIDTH`/`HEIGHT` must be positive, `ENTRY` and
`EXIT` must lie inside the maze and be different from each other, and
`PERFECT` must be exactly `True` or `False`. Any invalid or missing
value raises a clear error message instead of crashing.

## Maze generation algorithm

The maze is generated using the **recursive backtracker** algorithm
(iterative version, using an explicit stack rather than recursion, to
avoid hitting Python's recursion limit on larger mazes):

1. Start at the entry cell, mark it as visited, push it onto a stack.
2. While the stack is not empty, look at the cell on top of the stack.
3. If it has unvisited neighbours, pick one at random, remove the wall
   between the two cells, mark the neighbour as visited, and push it.
4. If it has no unvisited neighbours, pop the stack (backtrack).

This produces a **perfect maze**: since every wall removal connects a
new, previously unreached cell, the resulting structure is a spanning
tree over the grid — every two cells are connected by exactly one path,
with no cycles.

### Why this algorithm

- It is simple to reason about and implement correctly, which matters
  for a first from-scratch implementation.
- It naturally guarantees full connectivity and the "no area wider than
  2x2 open cells" rule for free: a spanning tree can never contain a
  4-cell loop, since that would require a cycle.
- It produces long, winding corridors with relatively few short dead
  ends, compared to alternatives like randomized Prim's, which tends to
  produce more uniformly short branches — a stylistic preference for
  this project.

When `PERFECT=False`, extra walls are removed after the initial
generation (`add_loops`) to introduce cycles. Each candidate removal is
first tested and then verified against the "no 2x2 open area" rule
(`has_any_open_block`); if it would violate the rule, the wall is put
back.

The shortest path between entry and exit (used both in the output file
and in the visual solution overlay) is computed with a standard
**BFS** (breadth-first search), which guarantees the shortest path in
an unweighted graph such as this one.

## Reusable module

All the maze-generation logic lives in the `mazegen` package
(`mazegen/cell.py` and `mazegen/generator.py`), completely independent
from the CLI/config parsing code (`config.py`, `a_maze_ing.py`). It can
be installed as a standalone package and imported into any other Python
project.

### Basic usage

```python
from mazegen import MazeGenerator

# Create a 20x15 maze with a fixed seed (for reproducibility)
maze = MazeGenerator(width=20, height=15, seed=42)

# Generate a perfect maze starting at (0, 0)
maze.generate(start_x=0, start_y=0)

# Optionally add extra loops (turns it into a non-perfect maze)
maze.add_loops(attempts=100)

# Access the generated structure: a 2D list of Cell objects
cell = maze.grid[0][0]
print(cell.wall_north, cell.wall_east, cell.wall_south, cell.wall_west)

# Get the shortest path (a list of Cell objects) between two cells
entry_cell = maze.grid[0][0]
exit_cell = maze.grid[14][19]
path = maze.bfs(entry_cell, exit_cell)

# Convert that path into a direction string (N/E/S/W)
directions = maze.path_to_directions(path)
```

### Custom parameters

- `width`, `height`: size of the maze grid.
- `seed`: any integer; reusing the same seed with the same operations
  always reproduces the exact same maze.
- `attempts` (in `add_loops`): how many extra wall-removal attempts to
  make; not all attempts necessarily succeed, since some would break
  the "no 2x2 open area" rule.

## Resources

- [Wikipedia — Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Wikipedia — Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
- Python official docs: `random`, `collections`, `typing`

### AI usage

AI was used throughout this project as a **tutor**, not as a
code generator: it explained concepts (classes, recursion, BFS, ANSI
colors, packaging), pointed out bugs. No code was copied directly into the
project; every function was typed and debugged by hand besides the README,
which was generated as a plain template and then modified afterwards to
remove tedious work. This applied across every part of the project:
config parsing, the maze generator classes, the recursive backtracker,
the 2x2-area validation, the "42" pattern, loop generation, BFS, the
output file format, the ASCII visualisation with colors, the Makefile,
the MLX display, and the packaging setup.

## Team and project management

Both of the members contributed equally to the making of the A-Maze-ing
project and were able to share knowledge between each other on how to
proceed, making every step together through the parts of the project.
There wasn't a part where one contributed more than the other.

### What worked well and what could be improved

What could be improved is the way we searched for information: it was
difficult to understand at first the knowledge needed to make the plan
work, but with some help we were able to do it. After it started going,
it was very much a question of time.

### Planning

The project was split by module boundaries that map closely onto the
subject's own structure (config → data model → generation algorithm →
constraints → "42" pattern → non-perfect mazes → shortest path →
output file → visualisation → packaging), so that a path was made clear
on how to proceed.

### Tools used

Python 3, `flake8`, `mypy`, `build`/`setuptools`, Git.

## For the 42 patter:
WIDTH=20
HEIGHT=10
ENTRY=15,5
EXIT=19,9
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42

