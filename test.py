"""
mazegen: A standalone maze generation and solving library.

Documentation:
--------------
1. Initialization:
   gen = MazeGenerator(width=40, height=40, entry=(0,0), exit=(39,39),
                       perfect=True, seed=123, algorithm="DFS")

2. Generate Structure:
   # Call carve_step() in a loop for animation, or:
   while not gen.carving_finished or not gen.imperfect_done:
       gen.carve_step()

3. Access Structure:
   grid = gen.maze  # Access internal [x][y] structure

4. Access Solution:
   path = gen.get_solution() # Returns NESW direction string
"""

import random
from typing import Set, List, Any, Tuple, Dict


class MazeGenerator:
    """A maze generator supporting DFS, Prim, and Kruskal algorithms.

    This class generates mazes with an optional '42' blocked pattern in the
    center, supports imperfect maze generation, and provides a built-in BFS
    solver.

    Attributes:
        width (int): Width of the maze in cells.
        height (int): Height of the maze in cells.
        entry (Tuple[int, int]): (x, y) coordinates of the entry point.
        exit (Tuple[int, int]): (x, y) coordinates of the exit point.
        perfect (bool): If True, creates a maze with a unique solution.
        seed (int | None): Random seed for reproducibility.
        algorithm (str): The algorithm to use ("DFS", "PRIM", "KRUSKAL").
        maze (List[List[Dict]]): The internal grid structure.
    """

    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], perfect: bool, seed: int | None,
                 algorithm: str = "DFS") -> None:
        """Initializes the MazeGenerator with configuration parameters."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.seed = seed
        self.perfect = perfect
        self.algorithm = algorithm.upper()

        if self.seed is not None:
            random.seed(self.seed)

        self.maze = [
            [{"N": True, "S": True, "E": True, "W": True}
             for _ in range(self.height)]
            for _ in range(self.width)
        ]

        self.blocked = self._42_blocked_pattern()
        self._entry_exit_validator()

        self.imperfect_done = False
        self.carving_finished = False

        if self.algorithm == "DFS":
            self._init_dfs()
        elif self.algorithm == "PRIM":
            self._init_prim()
        elif self.algorithm == "KRUSKAL":
            self._init_kruskal()
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

    def _42_blocked_pattern(self) -> Set:
        """
        Generates a set of coordinates forming a '42' pattern in the center.

        Returns:
            Set[Tuple[int, int]]: Coordinates that should be blocked.
        """
        PH, PW = 5, 3
        blocked = set()
        if self.height >= PH and self.width >= (2 * PW + 1):
            r0 = (self.height - PH) // 2
            c4 = (self.width - (2 * PW + 1)) // 2
            c2 = c4 + PW + 1

            # 4 pattern
            for dr, dc in [(0, 0), (1, 0), (2, 0), (2, 1),
                           (2, 2), (3, 2), (4, 2)]:
                blocked.add((c4 + dc, r0 + dr))

            # 2 pattern
            for dr, dc in [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1),
                           (2, 2), (3, 0), (4, 0), (4, 1), (4, 2)]:
                blocked.add((c2 + dc, r0 + dr))

        return blocked

    def _entry_exit_validator(self) -> None:
        """
        Validates that entry and exit are not placed inside blocked areas.
        """
        if self.entry in self.blocked:
            raise ValueError("ENTRY cannot be inside of the 42 Pattern")
        if self.exit in self.blocked:
            raise ValueError("EXIT cannot be inside of the 42 Pattern")

    def _neighbors(self, x: int, y: int) -> List:
        """
        Returns a list of potential neighbor coordinates and wall identifiers.

        Args:
            x (int): Current X coordinate.
            y (int): Current Y coordinate.

        Returns:
            List[Tuple[int, int, str, str]]: List of (nx, ny, wall,
                                                      opposite_wall).
        """
        return [
            (x, y - 1, "N", "S"),
            (x, y + 1, "S", "N"),
            (x + 1, y, "E", "W"),
            (x - 1, y, "W", "E"),
        ]

    def _valid_cell(self, x: int, y: int) -> bool:
        """
        Checks if a cell is within bounds and not blocked.

        Args:
            x (int): X coordinate to check.
            y (int): Y coordinate to check.

        Returns:
            bool: True if the cell is valid for carving.
        """
        return (
            0 <= x < self.width
            and 0 <= y < self.height
            and (x, y) not in self.blocked
        )

    def _remove_wall_between(self, a: Tuple[int, int],
                             b: Tuple[int, int]) -> None:
        """
        Removes the walls between two adjacent cells.

        Args:
            a (Tuple[int, int]): First cell coordinates.
            b (Tuple[int, int]): Second cell coordinates.
        """

        ax, ay = a
        bx, by = b

        if bx == ax and by == ay - 1:
            self.maze[ax][ay]["N"] = False
            self.maze[bx][by]["S"] = False
        elif bx == ax and by == ay + 1:
            self.maze[ax][ay]["S"] = False
            self.maze[bx][by]["N"] = False
        elif bx == ax + 1 and by == ay:
            self.maze[ax][ay]["E"] = False
            self.maze[bx][by]["W"] = False
        elif bx == ax - 1 and by == ay:
            self.maze[ax][ay]["W"] = False
            self.maze[bx][by]["E"] = False

    # ---------------- DFS Algorithm ----------------

    def _init_dfs(self) -> None:
        self.stack = [self.entry]
        self.visited = {self.entry} | self.blocked

    def _carve_step_dfs(self) -> Any:
        if not self.stack:
            self.carving_finished = True
            if not self.perfect:
                return self.make_imperfect()
            return None

        curr_x, curr_y = self.stack[-1]
        directions = self._neighbors(curr_x, curr_y)
        random.shuffle(directions)

        for nx, ny, wall, opp in directions:
            if (
                0 <= nx < self.width
                and 0 <= ny < self.height
                and (nx, ny) not in self.visited
                and (nx, ny) not in self.blocked
            ):
                self.maze[curr_x][curr_y][wall] = False
                self.maze[nx][ny][opp] = False
                self.visited.add((nx, ny))
                self.stack.append((nx, ny))
                return (curr_x, curr_y), (nx, ny)

        self.stack.pop()
        return (curr_x, curr_y), None

    # ---------------- Prim Algorithm ----------------

    def _init_prim(self) -> None:
        self.visited = {self.entry} | self.blocked
        self.frontier: List = []
        self._add_frontier(self.entry)

    def _add_frontier(self, cell: Tuple[int, int]) -> None:
        x, y = cell
        for nx, ny, _, _ in self._neighbors(x, y):
            if self._valid_cell(nx, ny) and (nx, ny) not in self.visited:
                self.frontier.append((cell, (nx, ny)))

    def _carve_step_prim(self) -> Any:
        while self.frontier:
            idx = random.randrange(len(self.frontier))
            from_cell, to_cell = self.frontier.pop(idx)

            if to_cell in self.visited:
                continue

            self._remove_wall_between(from_cell, to_cell)
            self.visited.add(to_cell)
            self._add_frontier(to_cell)
            return from_cell, to_cell

        self.carving_finished = True
        if not self.perfect:
            return self.make_imperfect()
        return None

    # ---------------- Kruskal Algorithm ----------------

    def _init_kruskal(self) -> None:
        self.parent = {}
        self.rank = {}
        self.edges = []

        for x in range(self.width):
            for y in range(self.height):
                if (x, y) in self.blocked:
                    continue
                self.parent[(x, y)] = (x, y)
                self.rank[(x, y)] = 0

                if self._valid_cell(x + 1, y):
                    self.edges.append(((x, y), (x + 1, y)))
                if self._valid_cell(x, y + 1):
                    self.edges.append(((x, y), (x, y + 1)))

        random.shuffle(self.edges)

    def _find(self, cell: Tuple[int, int]) -> Tuple[int, int]:
        if self.parent[cell] != cell:
            self.parent[cell] = self._find(self.parent[cell])
        return self.parent[cell]

    def _union(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        ra = self._find(a)
        rb = self._find(b)

        if ra == rb:
            return False

        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1

        return True

    def _carve_step_kruskal(self) -> Any:
        while self.edges:
            a, b = self.edges.pop()
            if self._union(a, b):
                self._remove_wall_between(a, b)
                return a, b

        self.carving_finished = True
        if not self.perfect:
            return self.make_imperfect()
        return None

    def carve_step(self) -> Any:
        """
        Processes one step of the current generation algorithm.

        Returns:
            Any: The coordinates updated during this step, or a list of
                 coordinates if transitioning to imperfect generation,
                 or None if finished.
        """
        if self.algorithm == "DFS":
            return self._carve_step_dfs()
        if self.algorithm == "PRIM":
            return self._carve_step_prim()
        if self.algorithm == "KRUSKAL":
            return self._carve_step_kruskal()

        return None

    def _open_area_validator(self, x: int, y: int) -> bool:
        """
        Checks if a 3x3 open area exists around a specific cell.

        An 'open' cell is defined as a cell with no internal walls. This
        function scans all nine possible 3x3 grids that could contain the
        cell (x, y).

        Args:
            x (int): The X coordinate of the modified cell.
            y (int): The Y coordinate of the modified cell.

        Returns:
            bool: True if a 3x3 open area is detected, False otherwise.
        """
        for ox in range(x - 2, x + 1):
            for oy in range(y - 2, y + 1):
                is_3x3 = True
                for ix in range(ox, ox + 3):
                    for iy in range(oy, oy + 3):
                        if not self._valid_cell(ix, iy):
                            is_3x3 = False
                            break
                        cell = self.maze[ix][iy]
                        if cell["N"] or cell["S"] or cell["E"] or cell["W"]:
                            is_3x3 = False
                            break
                    if not is_3x3:
                        break
                if is_3x3:
                    return True
        return False

    def make_imperfect(self) -> List[Tuple[int, int]]:
        """
        Randomly removes walls to create loops while respecting the 3x3 rule.

        This post-processing step converts a perfect maze into an imperfect one
        by removing approximately 10% of total possible walls. It ensures that
        no 3x3 open clearings are created in the process.

        Returns:
            List[Tuple[int, int]]: A list of coordinates that were modified.
        """
        if self.imperfect_done:
            return []

        total_cells = self.width * self.height
        target_removals = int(total_cells * 0.1)
        removed_count = 0
        affected_coords = []

        opp_map = {"N": (0, -1, "S"), "S": (0, 1, "N"),
                   "E": (1, 0, "W"),  "W": (-1, 0, "E")}

        attempts = 0
        max_attempts = target_removals * 20

        while removed_count < target_removals and attempts < max_attempts:
            attempts += 1
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            if (x, y) in self.blocked:
                continue

            wall = random.choice(["N", "S", "E", "W"])
            dx, dy, opp = opp_map[wall]
            nx, ny = x + dx, y + dy

            if self._valid_cell(nx, ny) and self.maze[x][y][wall]:
                self.maze[x][y][wall] = False
                self.maze[nx][ny][opp] = False

                if (self._open_area_validator(x, y)
                        or self._open_area_validator(nx, ny)):
                    self.maze[x][y][wall] = True
                    self.maze[nx][ny][opp] = True
                else:
                    removed_count += 1
                    affected_coords.extend([(x, y), (nx, ny)])

        self.imperfect_done = True
        return affected_coords

    def get_solution(self) -> str:
        """
        Solves the maze using a Breadth-First Search (BFS) algorithm.

        Returns:
            str: A string of characters (N, E, S, W) representing the shortest
                path from entry to exit.

        Raises:
            ValueError: If no valid path is found between entry and exit.
        """
        directions = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }

        queue = [self.entry]
        prev: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}
        visited = {self.entry} | self.blocked

        while queue:
            x, y = queue.pop(0)
            if (x, y) == self.exit:
                break

            cell = self.maze[x][y]
            for d, (dx, dy) in directions.items():
                if cell[d]:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    prev[(nx, ny)] = ((x, y), d)
                    queue.append((nx, ny))

        if self.exit not in prev and self.exit != self.entry:
            raise ValueError("No path found between ENTRY and EXIT")

        path_dirs: List[str] = []
        cur = self.exit
        while cur != self.entry:
            parent, d = prev[cur]
            path_dirs.append(d)
            cur = parent
        path_dirs.reverse()
        return "".join(path_dirs)
