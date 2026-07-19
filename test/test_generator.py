from mazegen import MazeGenerator


def test_same_seed_gives_same_maze():
    m1 = MazeGenerator(10, 10, seed=42)
    m1.generate(0, 0)
    m2 = MazeGenerator(10, 10, seed=42)
    m2.generate(0, 0)
    for row1, row2 in zip(m1.grid, m2.grid):
        for c1, c2 in zip(row1, row2):
            assert c1.wall_north == c2.wall_north
            assert c1.wall_east == c2.wall_east


def test_perfect_maze_has_no_open_block():
    m = MazeGenerator(10, 10, seed=1)
    m.generate(0, 0)
    assert m.has_any_open_block() is False


def test_perfect_maze_all_cells_visited():
    m = MazeGenerator(5, 5, seed=1)
    m.generate(0, 0)
    for row in m.grid:
        for cell in row:
            assert cell.visited is True


def test_bfs_finds_path_between_corners():
    m = MazeGenerator(10, 10, seed=7)
    m.generate(0, 0)
    start = m.grid[0][0]
    end = m.grid[9][9]
    path = m.bfs(start, end)
    assert path[0] == start
    assert path[-1] == end


def test_add_loops_never_creates_open_block():
    m = MazeGenerator(10, 10, seed=3)
    m.generate(0, 0)
    m.add_loops(200)
    assert m.has_any_open_block() is False