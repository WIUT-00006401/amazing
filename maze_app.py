from maze_generator import MazeGenerator
from helpers import path_to_coords, write_output, MazeConfig

from mlx import Mlx
from typing import Dict, List, Set, Any, Tuple


class MazeApp:
    """
    The main application class for the A-Maze-ing generator.

    This class handles the MiniLibX window initialization, rendering loops,
    event hooks (keyboard/mouse), and coordinates the animation between the
    generator and the display.

    Attributes:
        config (MazeConfig): Configuration object containing maze parameters.
        themes (List[Dict]): List of color schemes for the UI.
        theme (Dict): The currently active color theme.
        mlx (Mlx): The MiniLibX wrapper instance.
        win (Any): The window pointer created by MiniLibX.
        gen (MazeGenerator): The logic engine for carving the maze.
        animating (bool): Flag to control the real-time carving animation.
    """

    def __init__(self, config: MazeConfig, themes: List[Dict],
                 constants: Dict) -> None:
        """
        Initializes the MLX window and sets up the application state.

        Args:
            config (MazeConfig): The maze settings (width, height, entry, etc).
            themes (List[Dict]): Available color themes.
            constants (Dict): Window layout constants (padding, dimensions).
        """
        self.config = config
        self.themes = themes
        self.theme_idx = 0
        self.theme = themes[self.theme_idx]
        self.C = constants

        self.algorithms = ["DFS", "PRIM", "KRUSKAL"]
        self.algorithm_idx = 0
        self.algorithm = self.algorithms[self.algorithm_idx]

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_w = self.C['WIN_W'] + self.C['EXTRA_W']
        self.win_h = (self.C['TOP_PADDING'] + self.C['WIN_H']
                      + self.C['LEGEND_HEIGHT'] + self.C['BOTTOM_PADDING'])
        self.win = self.mlx.mlx_new_window(self.mlx_ptr, self.win_w,
                                           self.win_h, "A-Maze-ing")
        self.mlx.mlx_hook(self.win, 33, 0, self.on_close, None)

        self.cell_size = min(self.C['WIN_W'] // config.width,
                             self.C['WIN_H'] // config.height)
        self.offset_x = (self.win_w - (config.width * self.cell_size)) // 2
        self.offset_y = self.C['TOP_PADDING']

        self.show_path = True
        self.path_coords: Set[Tuple[int, int]] = set()
        self.regenerate()

    def regenerate(self) -> None:
        """Resets the generator with current settings and starts a new maze."""
        self.gen = MazeGenerator(
            width=self.config.width,
            height=self.config.height,
            entry=self.config.entry,
            exit=self.config.exit,
            seed=self.config.seed,
            perfect=self.config.perfect,
            algorithm=self.algorithm)
        self.animating = True
        self.path_coords = set()
        self.clear_screen()

    def clear_screen(self) -> None:
        """
        Fills the entire window with the current theme's background color.
        """
        self.fill_rect(0, 0, self.win_w, self.win_h, self.theme["BLOCK"])
        self.draw_legend()

    def animation_loop(self, _: Any = None) -> int:
        """The main loop hook called by MLX to animate maze carving.

        This method processes 5 steps of the generator per frame. It handles
        both single-step carving (tuples) and batch imperfect removals (lists).

        Args:
            _: Unused parameter passed by the MLX loop hook.

        Returns:
            int: Always 0 to keep the loop running.
        """
        if self.animating:
            for _ in range(5):
                change = self.gen.carve_step()

                if isinstance(change, list):
                    for pos in change:
                        if pos:
                            self.draw_cell(*pos)
                    self.animating = False
                    self.finalize()
                    return 0

                elif isinstance(change, tuple):
                    # Normal step-by-step carving
                    for pos in change:
                        if pos:
                            self.draw_cell(*pos)

                elif change is None and self.gen.carving_finished:
                    self.animating = False
                    self.finalize()
                    break
        return 0

    def on_close(self, _: Any = None) -> int:
        """Callback to handle the window close button (X) event."""
        self.mlx.mlx_loop_exit(self.mlx_ptr)
        return 0

    def draw_cell(self, x: int, y: int) -> None:
        """
        Draws a single maze cell including its floor and walls.

        Args:
            x (int): The X coordinate in the maze grid.
            y (int): The Y coordinate in the maze grid.
        """
        x0 = self.offset_x + x * self.cell_size
        y0 = self.offset_y + y * self.cell_size

        entry = self.config.entry
        exit = self.config.exit

        color = (self.theme["BLOCK"] if (x, y) in self.gen.blocked
                 else self.theme["OPEN"])
        if self.show_path and (x, y) in self.path_coords:
            color = self.theme["PATH"]

        if (x, y) == entry:
            color = self.theme["ENTRY"]
        elif (x, y) == exit:
            color = self.theme["EXIT"]

        self.fill_rect(x0, y0, self.cell_size, self.cell_size, color)

        if (x, y) not in self.gen.blocked:
            self.draw_walls(x, y, x0, y0)

    def fill_rect(self, x: int, y: int, w: int, h: int, color: int) -> None:
        """
        Draws a filled rectangle of a specific color to the window.

        Args:
            x (int): Starting X pixel.
            y (int): Starting Y pixel.
            w (int): Width in pixels.
            h (int): Height in pixels.
            color (str): Hexadecimal color value.
        """
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.mlx.mlx_pixel_put(self.mlx_ptr, self.win, xx, yy, color)

    def draw_walls(self, x: int, y: int, x0: int, y0: int) -> None:
        """
        Renders the walls for a specific cell based on its connectivity.

        Args:
            x (int): Maze X coordinate.
            y (int): Maze Y coordinate.
            x0 (int): Pixel X offset.
            y0 (int): Pixel Y offset.
        """
        cell = self.gen.maze[x][y]
        s = self.cell_size
        t = max(1, s // 10)

        if cell["N"]:
            self.fill_rect(x0, y0, s, t, self.theme["WALL"])
        if cell["S"]:
            self.fill_rect(x0, y0 + s - t, s, t, self.theme["WALL"])
        if cell["W"]:
            self.fill_rect(x0, y0, t, s, self.theme["WALL"])
        if cell["E"]:
            self.fill_rect(x0 + s - t, y0, t, s, self.theme["WALL"])

    def draw_maze(self) -> None:
        """Iterates through the entire grid and repaints every cell."""
        for x in range(self.config.width):
            for y in range(self.config.height):
                self.draw_cell(x, y)

    def finalize(self) -> None:
        """
        Handles post-generation logic including imperfect walls and solving.

        This is called once the primary carving algorithm finishes. It triggers
        the solver and saves the result to the output file.
        """
        try:
            path_str = self.gen.get_solution()
            self.path_coords = path_to_coords(path_str, self.config)
            write_output(self.gen.maze, self.config, path_str)

        except Exception as e:
            raise e

        finally:
            self.draw_maze()

    def draw_legend(self) -> None:
        """Renders the status text and control instructions at the bottom."""
        y_txt = self.win_h - self.C['BOTTOM_PADDING'] - 20
        status: str = (
            f"ENTRY:{self.config.entry}  EXIT:{self.config.exit}  "
            f"WIDTH:{self.config.width}  HEIGHT:{self.config.height}  "
            f"SEED:{self.config.seed}  PERFECT:{self.config.perfect}"
        )
        self.mlx.mlx_string_put(self.mlx_ptr, self.win, self.offset_x,
                                y_txt - 20, 0xFFFFFF, status)
        self.mlx.mlx_string_put(self.mlx_ptr, self.win, self.offset_x, y_txt,
                                0xFFFFFF,
                                "R: Re-generate | P: Path | T: Theme | A: Algo"
                                f" ({self.algorithm}) | ESC: Quit")

    def on_key(self, key: int, _: Any) -> int:
        """
        Handles keyboard input for app controls.

        Args:
            key (int): The keycode of the pressed key.
            _: Unused metadata.

        Returns:
            int: 0 on success.
        """
        
        if key == 65307:
            self.mlx.mlx_loop_exit(self.mlx_ptr)
        elif key in (114, 82):
            self.regenerate()
        elif key in (112, 80):
            self.show_path = not self.show_path
            self.draw_maze()
        elif key in (116, 84):
            self.theme_idx = (self.theme_idx + 1) % len(self.themes)
            self.theme = self.themes[self.theme_idx]
            self.mlx.mlx_clear_window(self.mlx_ptr, self.win)

            self.fill_rect(0, 0, self.win_w, self.offset_y,
                           self.theme["BLOCK"])
            y_bottom = self.offset_y + (self.config.height * self.cell_size)
            self.fill_rect(0, y_bottom, self.win_w, self.win_h - y_bottom,
                           self.theme["BLOCK"])
            self.fill_rect(0, self.offset_y, self.offset_x,
                           self.win_h - self.offset_y, self.theme["BLOCK"])
            x_right = self.offset_x + (self.config.width * self.cell_size)
            self.fill_rect(x_right, self.offset_y, self.win_w - x_right,
                           self.win_h - self.offset_y, self.theme["BLOCK"])
            self.draw_maze()
            self.draw_legend()
        elif key in (97, 65):
            self.algorithm_idx = ((self.algorithm_idx + 1)
                                  % len(self.algorithms))
            self.algorithm = self.algorithms[self.algorithm_idx]
            self.mlx.mlx_clear_window(self.mlx_ptr, self.win)
            self.regenerate()
        return 0
