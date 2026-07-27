class Cell:
    """Represents a single cell in the maze grid.

    Each cell stores its grid position and the state of its four walls
    (north, south, east, west). All walls start as closed.

    Attributes:
        x: Column index in the grid.
        y: Row index in the grid.
        visited: Whether the cell has been visited during generation.
        wall_north: True if the north wall is closed.
        wall_south: True if the south wall is closed.
        wall_east: True if the east wall is closed.
        wall_west: True if the west wall is closed.
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialise a cell at the given grid position.

        Args:
            x: Column index.
            y: Row index.
        """
        self.visited: bool = False
        self.x: int = x
        self.y: int = y
        self.wall_north: bool = True
        self.wall_south: bool = True
        self.wall_east: bool = True
        self.wall_west: bool = True
