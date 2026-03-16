from helpers import parse_config, config_validator, MazeConfig
from maze_app import MazeApp

from typing import List
import sys

CONSTANTS = {
    'WIN_W': 800, 'WIN_H': 800, 'EXTRA_W': 200,
    'TOP_PADDING': 20, 'LEGEND_HEIGHT': 60, 'BOTTOM_PADDING': 20
}

THEMES = [
    {"WALL": 0xFF0077B6, "OPEN": 0xFF90E0EF, "BLOCK": 0xFF03045E,
     "PATH": 0xFF00B4D8, "ENTRY": 0xFF00FF00, "EXIT": 0xFFFF0000},
    {"WALL": 0xFF31572C, "OPEN": 0xFF4F772D, "BLOCK": 0xFF132A13,
     "PATH": 0xFF90A955, "ENTRY": 0xFF00FF00, "EXIT": 0xFFFF0000},
    {"WALL": 0xFFDD2D4A, "OPEN": 0xFFF26A8D, "BLOCK": 0xFF880D1E,
     "PATH": 0xFFF49CBB, "ENTRY": 0xFF6BCB77, "EXIT": 0xFFEF476F},
    {"WALL": 0xFFFFD6A5, "OPEN": 0xFFFDFFB6, "BLOCK": 0xFFFFADAD,
     "PATH": 0xFFCAFFBF, "ENTRY": 0xFF00FF88, "EXIT": 0xFFFF4444}
]


def main(argv: List[str]) -> None:
    """
    Parses config, validates parameters, and launches the MazeApp.

    Args:
        argv (List[str]): Command line arguments. Expects the path to a
            configuration file as the second element.
    """
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    try:
        config_path = argv[1]
        config: MazeConfig = parse_config(config_path)

        config_validator(config)

        app = MazeApp(config, THEMES, CONSTANTS)
        app.mlx.mlx_loop_hook(app.mlx_ptr, app.animation_loop, None)
        app.mlx.mlx_key_hook(app.win, app.on_key, None)
        app.mlx.mlx_loop(app.mlx_ptr)

    except Exception as e:
        print(f"Error: {e}")
        return


if __name__ == "__main__":
    main(sys.argv)
