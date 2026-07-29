from mazegen import MazeGenerator


def test_same_seed_gives_same_maze() -> None:
    m1 = MazeGenerator(10, 10, seed=42)
    m1.generate(0, 0)
    m2 = MazeGenerator(10, 10, seed=42)
    m2.generate(0, 0)
    for row1, row2 in zip(m1.grid, m2.grid):
        for c1, c2 in zip(row1, row2):
            assert c1.wall_north == c2.wall_north
            assert c1.wall_east == c2.wall_east


def test_perfect_maze_has_no_open_block() -> None:
    m = MazeGenerator(10, 10, seed=1)
    m.generate(0, 0)
    assert m.has_any_open_block() is False


def test_perfect_maze_all_cells_visited() -> None:
    m = MazeGenerator(5, 5, seed=1)
    m.generate(0, 0)
    for row in m.grid:
        for cell in row:
            assert cell.visited is True


def test_bfs_finds_path_between_corners() -> None:
    m = MazeGenerator(10, 10, seed=7)
    m.generate(0, 0)
    start = m.grid[0][0]
    end = m.grid[9][9]
    path = m.bfs(start, end)
    assert path[0] == start
    assert path[-1] == end


def test_add_loops_never_creates_open_block() -> None:
    m = MazeGenerator(10, 10, seed=3)
    m.generate(0, 0)
    m.add_loops(200)
    assert m.has_any_open_block() is False


def test_apply_42_centered_on_large_maze() -> None:
    m = MazeGenerator(30, 20, seed=42)
    m.apply_42_pattern((1, 1), (28, 18))
    m.generate(1, 1)
    assert len(m.pattern_42) > 0
    min_x = min(c[0] for c in m.pattern_42)
    max_x = max(c[0] for c in m.pattern_42)
    min_y = min(c[1] for c in m.pattern_42)
    max_y = max(c[1] for c in m.pattern_42)
    assert min_x > 0
    assert min_y > 0
    assert max_x < m.width - 1
    assert max_y < m.height - 1


def test_apply_42_skipped_when_entry_in_pattern() -> None:
    m = MazeGenerator(10, 10, seed=42)
    m.apply_42_pattern((0, 2), (9, 9))
    assert len(m.pattern_42) == 0


def test_apply_42_never_blocks_path() -> None:
    for seed in range(10):
        m = MazeGenerator(30, 20, seed=seed)
        m.apply_42_pattern((1, 1), (28, 18))
        m.generate(1, 1)
        start = m.grid[1][1]
        end = m.grid[18][28]
        path = m.bfs(start, end)
        assert path[0] == start
        assert path[-1] == end
