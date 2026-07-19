class Cell:
    """Represents a position with its walls"""
    def __init__(self, x: int, y: int) -> None:
        self.visited: bool = False
        self.x: int = x
        self.y: int = y
        self.wall_north: bool = True
        self.wall_south: bool = True
        self.wall_east: bool = True
        self.wall_west: bool = True
