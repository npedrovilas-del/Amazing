from __future__ import annotations
from .cell import Cell
import random


# Códigos de cor ANSI (para usar no terminal).
# Formato: "\033[XXm" liga a cor, "\033[0m" repõe a cor normal.
# 31 = vermelho   32 = verde     33 = amarelo   34 = azul
# 35 = magenta    36 = cyan      37 = branco
COLOR_RESET = "\033[0m"
COLORS: dict[str, str] = {
    "1": "31",  # vermelho
    "2": "32",  # verde
    "3": "34",  # azul
    "4": "33",  # amarelo
    "5": "36",  # cyan
    "6": "37",  # branco
}


class MazeGenerator:
    """Generates and manages a maze grid.

    Provides maze generation via the recursive backtracker algorithm,
    wall management, pathfinding (BFS), loop injection, the "42" pattern,
    and output in hex / ASCII-art formats.

    Attributes:
        seed: Random seed used for reproducible generation.
        width: Number of columns in the grid.
        height: Number of rows in the grid.
        grid: 2D list of Cell objects.
        pattern_42: List of (col, row) tuples forming the "42" pattern.
    """

    def __init__(self, width: int, height: int, seed: int) -> None:
        """Create a new grid of cells and set the random seed.

        Args:
            width: Number of columns.
            height: Number of rows.
            seed: Integer seed for reproducible randomness.
        """
        random.seed(seed)
        self.seed: int = seed
        self.width: int = width
        self.height: int = height
        self.grid: list[list[Cell]] = []
        for y in range(height):
            row: list[Cell] = []
            for x in range(width):
                row.append(Cell(x, y))
            self.grid.append(row)
        self.pattern_42: list[tuple[int, int]] = []

    def get_neighbors(self, cell: Cell) -> list[Cell]:
        """Return all orthogonally adjacent cells (up to 4).

        Args:
            cell: The cell whose neighbours to look up.

        Returns:
            List of adjacent Cell objects within grid bounds.
        """
        neighbors: list[Cell] = []
        if cell.y - 1 >= 0:
            neighbor = self.grid[cell.y - 1][cell.x]
            neighbors.append(neighbor)
        if cell.y + 1 < self.height:
            neighbor = self.grid[cell.y + 1][cell.x]
            neighbors.append(neighbor)
        if cell.x + 1 < self.width:
            neighbor = self.grid[cell.y][cell.x + 1]
            neighbors.append(neighbor)
        if cell.x - 1 >= 0:
            neighbor = self.grid[cell.y][cell.x - 1]
            neighbors.append(neighbor)
        return neighbors

    def remove_wall_east(self, current: Cell, neighbor: Cell) -> None:
        """Remove the east wall of current and the west wall of neighbour.

        Args:
            current: The cell whose east wall is removed.
            neighbor: The cell whose west wall is removed.
        """
        current.wall_east = False
        neighbor.wall_west = False

    def remove_wall_north(self, current: Cell, neighbor: Cell) -> None:
        """Remove the north wall of current and the south wall of neighbour.

        Args:
            current: The cell whose north wall is removed.
            neighbor: The cell whose south wall is removed.
        """
        current.wall_north = False
        neighbor.wall_south = False

    def remove_wall_south(self, current: Cell, neighbor: Cell) -> None:
        """Remove the south wall of current and the north wall of neighbour.

        Args:
            current: The cell whose south wall is removed.
            neighbor: The cell whose north wall is removed.
        """
        current.wall_south = False
        neighbor.wall_north = False

    def remove_wall_west(self, current: Cell, neighbor: Cell) -> None:
        """Remove the west wall of current and the east wall of neighbour.

        Args:
            current: The cell whose west wall is removed.
            neighbor: The cell whose east wall is removed.
        """
        current.wall_west = False
        neighbor.wall_east = False

    def remove_wall_between(self, current: Cell, neighbor: Cell) -> None:
        """Remove the wall shared by two adjacent cells.

        Automatically detects the relative position and delegates to the
        correct directional removal method.

        Args:
            current: One of the two adjacent cells.
            neighbor: The other adjacent cell.
        """
        if neighbor.y < current.y:
            self.remove_wall_north(current, neighbor)
        if neighbor.y > current.y:
            self.remove_wall_south(current, neighbor)
        if neighbor.x < current.x:
            self.remove_wall_west(current, neighbor)
        if neighbor.x > current.x:
            self.remove_wall_east(current, neighbor)

    def add_wall_east(self, current: Cell, neighbor: Cell) -> None:
        """Add the east wall of current and the west wall of neighbour.

        Args:
            current: The cell whose east wall is added.
            neighbor: The cell whose west wall is added.
        """
        current.wall_east = True
        neighbor.wall_west = True

    def add_wall_north(self, current: Cell, neighbor: Cell) -> None:
        """Add the north wall of current and the south wall of neighbour.

        Args:
            current: The cell whose north wall is added.
            neighbor: The cell whose south wall is added.
        """
        current.wall_north = True
        neighbor.wall_south = True

    def add_wall_south(self, current: Cell, neighbor: Cell) -> None:
        """Add the south wall of current and the north wall of neighbour.

        Args:
            current: The cell whose south wall is added.
            neighbor: The cell whose north wall is added.
        """
        current.wall_south = True
        neighbor.wall_north = True

    def add_wall_west(self, current: Cell, neighbor: Cell) -> None:
        """Add the west wall of current and the east wall of neighbour.

        Args:
            current: The cell whose west wall is added.
            neighbor: The cell whose east wall is added.
        """
        current.wall_west = True
        neighbor.wall_east = True

    def add_wall_between(self, current: Cell, neighbor: Cell) -> None:
        """Add the wall shared by two adjacent cells.

        Automatically detects the relative position and delegates to the
        correct directional addition method.

        Args:
            current: One of the two adjacent cells.
            neighbor: The other adjacent cell.
        """
        if neighbor.y < current.y:
            self.add_wall_north(current, neighbor)
        if neighbor.y > current.y:
            self.add_wall_south(current, neighbor)
        if neighbor.x < current.x:
            self.add_wall_west(current, neighbor)
        if neighbor.x > current.x:
            self.add_wall_east(current, neighbor)

    def get_unvisited_neighbors(self, cell: Cell) -> list[Cell]:
        """Return neighbours that have not been visited during generation.

        Args:
            cell: The cell whose unvisited neighbours to retrieve.

        Returns:
            List of unvisited adjacent Cell objects.
        """
        neighbors = self.get_neighbors(cell)
        unvisited: list[Cell] = []
        for neighbor in neighbors:
            if not neighbor.visited:
                unvisited.append(neighbor)
        return unvisited

    def get_accessible_neighbors(self, cell: Cell) -> list[Cell]:
        """Return neighbours reachable through an open wall.

        Args:
            cell: The cell whose accessible neighbours to retrieve.

        Returns:
            List of Cell objects reachable without crossing a wall.
        """
        neighbors = self.get_neighbors(cell)
        accessible: list[Cell] = []
        for neighbor in neighbors:
            is_open = False
            if neighbor.y < cell.y:
                is_open = not cell.wall_north
            elif neighbor.y > cell.y:
                is_open = not cell.wall_south
            elif neighbor.x < cell.x:
                is_open = not cell.wall_west
            elif neighbor.x > cell.x:
                is_open = not cell.wall_east
            if is_open:
                accessible.append(neighbor)
        return accessible

    def generate(self, start_x: int, start_y: int) -> None:
        """Generate a perfect maze using the recursive backtracker.

        Starts at (start_x, start_y) and carves passages by randomly
        visiting unvisited neighbours until every cell is reachable.

        Args:
            start_x: Column index of the starting cell.
            start_y: Row index of the starting cell.
        """
        start = self.grid[start_y][start_x]
        start.visited = True
        stack: list[Cell] = [start]
        while len(stack) > 0:
            current = stack[-1]
            unvisited = self.get_unvisited_neighbors(current)
            if len(unvisited) > 0:
                neighbor = random.choice(unvisited)
                self.remove_wall_between(current, neighbor)
                neighbor.visited = True
                stack.append(neighbor)
            else:
                stack.pop()

    def is_block_open(self, x: int, y: int) -> bool:
        """Check whether a 2x2 block starting at (x, y) is fully open.

        A block is open when all four cells share no walls between them,
        which is forbidden by the maze rules.

        Args:
            x: Column index of the top-left cell.
            y: Row index of the top-left cell.

        Returns:
            True if the 2x2 block has no internal walls, False otherwise.
        """
        if x + 1 >= self.width or y + 1 >= self.height:
            return False
        a = self.grid[y][x]
        b = self.grid[y][x + 1]
        c = self.grid[y + 1][x]
        return (not a.wall_east and not c.wall_east
                and not a.wall_south and not b.wall_south)

    def has_any_open_block(self) -> bool:
        """Check whether any 2x2 open block exists in the grid.

        Returns:
            True if at least one 2x2 open block is found, False otherwise.
        """
        for y in range(self.height - 1):
            for x in range(self.width - 1):
                if self.is_block_open(x, y):
                    return True
        return False

    def add_loops(self, attempts: int) -> None:
        """Add extra passages to create loops in the maze.

        Each attempt picks a random cell and neighbour, removes the wall
        between them, and re-adds it if doing so creates a 2x2 open block.

        Args:
            attempts: Number of random wall-removal attempts to try.
        """
        for i in range(attempts):
            row = random.choice(self.grid)
            cell = random.choice(row)
            neighbors = self.get_neighbors(cell)
            neighbor = random.choice(neighbors)
            is_open = False
            if neighbor.y < cell.y:
                is_open = not cell.wall_north
            elif neighbor.y > cell.y:
                is_open = not cell.wall_south
            elif neighbor.x < cell.x:
                is_open = not cell.wall_west
            elif neighbor.x > cell.x:
                is_open = not cell.wall_east
            if is_open:
                continue
            self.remove_wall_between(cell, neighbor)
            if self.has_any_open_block():
                self.add_wall_between(cell, neighbor)

    def is_connected(self, start: Cell, end: Cell) -> bool:
        """Check whether two cells are reachable from each other.

        Uses BFS to traverse accessible neighbours.

        Args:
            start: The origin cell.
            end: The destination cell.

        Returns:
            True if a path exists between start and end, False otherwise.
        """
        fila: list[Cell] = [start]
        visitados: set[Cell] = {start}
        while len(fila) > 0:
            atual = fila.pop(0)
            if atual == end:
                return True
            vizinhos = self.get_accessible_neighbors(atual)
            for vizinho in vizinhos:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
        return False

    def bfs(self, start: Cell, end: Cell) -> list[Cell]:
        """Find the shortest path between two cells using BFS.

        Args:
            start: The origin cell.
            end: The destination cell.

        Returns:
            Ordered list of Cell objects from start to end (inclusive).
        """
        fila: list[Cell] = [start]
        came_from: dict[Cell, Cell | None] = {start: None}
        while len(fila) > 0:
            atual = fila.pop(0)
            if atual == end:
                break
            vizinhos = self.get_accessible_neighbors(atual)
            for vizinho in vizinhos:
                if vizinho not in came_from:
                    came_from[vizinho] = atual
                    fila.append(vizinho)
        caminho: list[Cell] = []
        current: Cell | None = end
        while current is not None:
            caminho.append(current)
            current = came_from[current]
        caminho.reverse()
        return caminho

    def path_to_directions(self, caminho: list[Cell]) -> str:
        """Convert a cell path into a direction string.

        Args:
            caminho: Ordered list of Cell objects forming a path.

        Returns:
            A string of N/E/S/W characters representing the moves.
        """
        direcoes = ""
        for i in range(len(caminho) - 1):
            atual = caminho[i]
            seguinte = caminho[i + 1]
            if seguinte.y < atual.y:
                direcoes += "N"
            if seguinte.y > atual.y:
                direcoes += "S"
            if seguinte.x < atual.x:
                direcoes += "W"
            if seguinte.x > atual.x:
                direcoes += "E"
        return direcoes

    def hexa(self, cell: Cell) -> str:
        """Encode a cell's walls as a single hexadecimal character.

        Bit layout: 0=N, 1=E, 2=S, 3=W. A set wall sets the bit to 1.

        Args:
            cell: The cell to encode.

        Returns:
            Uppercase hex character ('0'-'F') representing the walls.
        """
        valor = 0
        if cell.wall_north:
            valor += 1
        if cell.wall_east:
            valor += 2
        if cell.wall_south:
            valor += 4
        if cell.wall_west:
            valor += 8
        return f"{valor:X}"

    def print_maze(self, entry: tuple[int, int], exit: tuple[int, int],
                   caminho: list[Cell], cor: str = "37",
                   cor_42: str = "35") -> None:
        """Desenha o labirinto no terminal.

        Args:
            entry: tuplo (x, y) da entrada.
            exit: tuplo (x, y) da saida.
            caminho: lista de Cell do caminho a marcar (pode ser vazia).
            cor: codigo ANSI (string) usado para as paredes normais.
            cor_42: codigo ANSI (string) usado para as celulas do padrao 42.
        """
        for row in self.grid:
            top_line = ""
            for cell in row:
                if (cell.x, cell.y) in self.pattern_42:
                    top_line += f"\033[{cor_42}m+"
                else:
                    top_line += f"\033[{cor}m+"
                if cell.wall_north:
                    top_line += "--"
                else:
                    top_line += "  "
                top_line += COLOR_RESET
            print(top_line + f"\033[{cor}m+{COLOR_RESET}")

            mid_line = ""
            for cell in row:
                if (cell.x, cell.y) in self.pattern_42:
                    wall_color = cor_42
                else:
                    wall_color = cor
                if cell.wall_west:
                    mid_line += f"\033[{wall_color}m|{COLOR_RESET}"
                else:
                    mid_line += " "
                if (cell.x, cell.y) == entry:
                    mid_line += f"\033[32mEN{COLOR_RESET}"
                elif (cell.x, cell.y) == exit:
                    mid_line += f"\033[31mEX{COLOR_RESET}"
                elif cell in caminho:
                    mid_line += f"\033[33m* {COLOR_RESET}"
                else:
                    mid_line += "  "
            print(mid_line + f"\033[{cor}m|{COLOR_RESET}")

        under_line = ""
        for cell in row:
            if (cell.x, cell.y) in self.pattern_42:
                under_line += f"\033[{cor_42}m+"
            else:
                under_line += f"\033[{cor}m+"
            if cell.wall_south:
                under_line += "--"
            else:
                under_line += "  "
            under_line += COLOR_RESET
        print(under_line + f"\033[{cor}m+{COLOR_RESET}")

    def apply_42_pattern(self, entry: tuple[int, int],
                         exit: tuple[int, int]) -> None:
        """Carve the visually closed "42" pattern into the maze.

        Fully closes a set of cells in the shape of "42" at the top-left
        corner. If this would block the entry, exit, or disconnect the
        maze, the pattern is reverted.

        Args:
            entry: (x, y) coordinates of the maze entry.
            exit: (x, y) coordinates of the maze exit.
        """
        pattern: list[tuple[int, int]] = [
            (0, 0), (0, 1), (0, 2),
            (1, 2), (2, 2), (3, 2), (4, 2),
            (4, 0), (4, 1), (4, 2), (4, 3), (4, 4),
            (6, 0), (7, 0), (8, 0), (9, 0),
            (9, 1),
            (6, 2), (7, 2), (8, 2), (9, 2),
            (6, 3),
            (6, 4), (7, 4), (8, 4), (9, 4)
        ]
        if entry in pattern or exit in pattern:
            print(
                "Cannot apply 42 pattern: it would block "
                "the entry or exit."
            )
            return
        if self.width < 10 or self.height < 5:
            print("The maze needs to be 10x5 atleast to aplly the 42 pattern")
            return

        entry_x, entry_y = entry
        entry_cell = self.grid[entry_y][entry_x]
        exit_x, exit_y = exit
        exit_cell = self.grid[exit_y][exit_x]

        affected: set[tuple[int, int]] = set()
        for col, row in pattern:
            affected.add((col, row))
            if col + 1 < self.width:
                affected.add((col + 1, row))
            if row + 1 < self.height:
                affected.add((col, row + 1))

        snapshot: dict[tuple[int, int], tuple[bool, bool, bool, bool]] = {}
        for (c, r) in affected:
            cell = self.grid[r][c]
            snapshot[(c, r)] = (
                cell.wall_north, cell.wall_south,
                cell.wall_east, cell.wall_west,
            )

        for col, row in pattern:
            cell = self.grid[row][col]
            if col + 1 < self.width:
                self.grid[row][col + 1].wall_west = True
            cell.wall_north = True
            if row + 1 < self.height:
                self.grid[row + 1][col].wall_north = True
            cell.wall_west = True
            cell.wall_east = True
            cell.wall_south = True

        if not self.is_connected(entry_cell, exit_cell):
            for (c, r), (n, s, e, w) in snapshot.items():
                cell = self.grid[r][c]
                cell.wall_north = n
                cell.wall_south = s
                cell.wall_east = e
                cell.wall_west = w
            print(
                "Cannot apply 42 pattern: it would block "
                "the entry or exit."
            )
            return

        self.pattern_42 = pattern

    def write_output(self, path: str, entry: tuple[int, int],
                     exit: tuple[int, int]) -> None:
        """Write the maze to a file in hex encoding format.

        The file contains one hex digit per cell (row by row), followed
        by an empty line, the entry coordinates, the exit coordinates,
        and the shortest path as N/E/S/W directions.

        Args:
            path: Filesystem path for the output file.
            entry: (x, y) coordinates of the maze entry.
            exit: (x, y) coordinates of the maze exit.

        Raises:
            ValueError: If entry and exit are not connected.
        """
        with open(path, "w") as f:
            for row in self.grid:
                line = ""
                for cell in row:
                    line += self.hexa(cell)
                f.write(line + "\n")
            f.write("\n")
            entry_x, entry_y = entry
            entry_cell = self.grid[entry_y][entry_x]
            exit_x, exit_y = exit
            exit_cell = self.grid[exit_y][exit_x]
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit[0]},{exit[1]}\n")
            try:
                caminho = self.bfs(entry_cell, exit_cell)
            except KeyError:
                raise ValueError(
                    "Entry and exit are not connected "
                    "(likely due to the 42 pattern blocking the path)."
                )
            directions = self.path_to_directions(caminho)
            f.write(directions + "\n")

# if __name__ == "__main__":
#     m = MazeGenerator(20, 20, seed=42)
#     entry = (0, 19)
#     exit_ = (19, 19)
#     m.generate(entry[0], entry[1])
#     m.apply_42_pattern(entry, exit_)
#     entry_cell = m.grid[entry[1]][entry[0]]
#     exit_cell = m.grid[exit_[1]][exit_[0]]
#     caminho = m.bfs(entry_cell, exit_cell)
#     m.print_maze(entry, exit_, caminho, cor="34", cor_42="35")
