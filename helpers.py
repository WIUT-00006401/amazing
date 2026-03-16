from typing import Dict, Tuple, List, Set


class MazeConfig:
    """Configuration data for maze generation and solving.

    Attributes:
        width (int): Width of the maze in cells.
        height (int): Height of the maze in cells.
        entry (Tuple[int, int]): Starting (x, y) coordinates.
        exit (Tuple[int, int]): Ending (x, y) coordinates.
        output_file (str): Path to save the hex representation of the maze.
        perfect (bool): Whether the maze should have a unique path.
        seed (int | None): Seed for the random number generator.
    """

    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], output_file: str, perfect: bool,
                 seed: int | None) -> None:
        """Initializes MazeConfig with specified parameters."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect
        self.seed = seed


def parse_config(path: str) -> MazeConfig:
    """
    Parses a configuration file to create a MazeConfig object.

    Args:
        path (str): The path to the config.txt file.

    Returns:
        MazeConfig: An object containing the parsed maze settings.

    Raises:
        ValueError: If the file is missing, line format is invalid, or
            mandatory keys are missing.
    """
    config: Dict[str, str] = {}

    try:
        with open(path, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(f"Invalid config line: {line}")
                key, value = line.split("=", 1)
                config[key.strip().upper()] = value.strip()
    except FileNotFoundError:
        raise ValueError(f"Configuration file not found: {path}")

    def parse_coord(string: str) -> Tuple[int, int]:
        x_str, y_str = string.split(",")

        return int(x_str), int(y_str)

    return MazeConfig(
        width=int(config["WIDTH"]),
        height=int(config["HEIGHT"]),
        entry=parse_coord(config["ENTRY"]),
        exit=parse_coord(config["EXIT"]),
        output_file=config["OUTPUT_FILE"],
        perfect=config["PERFECT"].lower() == "true",
        seed=int(config["SEED"]) if "SEED" in config else None
    )


def config_validator(config: MazeConfig) -> None:
    """
    Validates maze parameters to ensure they meet minimum requirements.

    Args:
        config (MazeConfig): The configuration to validate.

    Raises:
        ValueError: If dimensions are too small, entry/exit are out of
            bounds, or entry and exit are identical.
    """
    if config.width < 7:
        raise ValueError("WIDTH cannot be smaller than 7")
    if config.height < 5:
        raise ValueError("WIDTH cannot be smaller than 5")
    if not (0 <= config.entry[0] < config.width
            and 0 <= config.entry[1] < config.height):
        raise ValueError("ENTRY out of bounds")
    if not (0 <= config.exit[0] < config.width
            and 0 <= config.exit[1] < config.height):
        raise ValueError("EXIT out of bounds")
    if config.entry == config.exit:
        raise ValueError("ENTRY and EXIT must be different")


def path_to_coords(path_str: str, config: MazeConfig) -> Set[Tuple[int, int]]:
    """
    Converts a direction string into a set of (x, y) coordinates.

    Args:
        path_str (str): String of directions (e.g., 'NNESW').
        config (MazeConfig): Maze configuration to get the starting entry.

    Returns:
        Set[Tuple[int, int]]: All coordinates visited along the path.
    """
    x, y = config.entry
    coords = {(x, y)}

    moves = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0),
    }

    for d in path_str:
        dx, dy = moves[d]
        x += dx
        y += dy
        coords.add((x, y))

    return coords


def cell_to_hex(cell: Dict[str, bool]) -> str:
    """
    Converts a maze cell's wall configuration into a single hex digit.

    Binary mapping: North=1, East=2, South=4, West=8.

    Args:
        cell (Dict[str, bool]): Dictionary of wall states
                                (True if wall exists).

    Returns:
        str: A single uppercase hexadecimal character (0-F).
    """
    value = 0
    if cell["N"]:
        value |= 1 << 0
    if cell["E"]:
        value |= 1 << 1
    if cell["S"]:
        value |= 1 << 2
    if cell["W"]:
        value |= 1 << 3
    return format(value, "X")


def write_output(maze: List[List[Dict[str, bool]]], config: MazeConfig,
                 path_str: str) -> None:
    """
    Writes the maze structure and solution path to the output file.

    Args:
        maze (List[List[Dict]]): The 2D grid of maze cells.
        config (MazeConfig): Configuration for output path and metadata.
        path_str (str): The solved path direction string.
    """
    with open(config.output_file, "w", encoding="utf-8") as file:
        for y in range(config.height):
            line = "".join(cell_to_hex(maze[x][y])
                           for x in range(config.width))
            file.write(line + "\n")

        file.write("\n")
        file.write(f"{config.entry[0]},{config.entry[1]}\n")
        file.write(f"{config.exit[0]},{config.exit[1]}\n")
        file.write(path_str + "\n")
