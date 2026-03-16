# **A-Maze-ing**

_This project has been created as part of the 42 curriculum by &lt;azmubara&gt;, &lt;dujuraev&gt;._

# **Description**

**A-Maze-ing** is a Python project that generates and visualizes mazes based on a configuration file.

The program reads parameters such as maze size, entry/exit coordinates, and generation mode from a configuration file, generates a maze using different algorithms, finds the shortest path between entry and exit, and displays the result visually.

The maze is also exported to a file using a hexadecimal encoding format representing the walls of each cell.

This project demonstrates the use of:

- graph algorithms
- procedural maze generation
- pathfinding algorithms
- graphical rendering
- modular and reusable Python architecture

# **Features**

### **Maze generation**

The program supports multiple maze generation algorithms:

- **DFS (Recursive Backtracking)**
- **Prim's Algorithm**
- **Kruskal's Algorithm**

The algorithm can be switched dynamically during execution.

### **Perfect / Imperfect mazes**

The maze can be generated as:

- **Perfect maze** → exactly one path between entry and exit
- **Imperfect maze** → additional walls removed to create loops

### **Pathfinding**

The shortest path between entry and exit is calculated using **Breadth-First Search (BFS)**.

### **Visual interface**

The maze is rendered using **MiniLibX (MLX)** and supports:

- maze generation animation
- path display
- theme switching
- algorithm switching
- maze regeneration

### **Output file**

The generated maze is exported using a **hexadecimal wall encoding**, as required by the subject.

# **Installation**

### **Requirements**

- Python **3.10+**
- MiniLibX Python bindings
- Linux / macOS environment

### **Clone repository**

git clone &lt;repository_url&gt;

cd a-maze-ing

# **Running the project**

The program is executed using a configuration file.

python3 a_maze_ing.py config.txt

The configuration file defines all maze generation parameters.

# **Configuration File Format**

The configuration file contains one KEY=VALUE pair per line.

Example configuration:

WIDTH=50

HEIGHT=50

ENTRY=0,0

EXIT=49,49

OUTPUT_FILE=maze.txt

PERFECT=False

SEED=12345

(Default configuration example from the project: )

### **Parameters**

| **Key**     | **Description**                  |
| ----------- | -------------------------------- |
| WIDTH       | Maze width (cells)               |
| ---         | ---                              |
| HEIGHT      | Maze height                      |
| ---         | ---                              |
| ENTRY       | Entry coordinates (x,y)          |
| ---         | ---                              |
| EXIT        | Exit coordinates (x,y)           |
| ---         | ---                              |
| OUTPUT_FILE | Output file name                 |
| ---         | ---                              |
| PERFECT     | Whether the maze must be perfect |
| ---         | ---                              |
| SEED        | Optional random seed             |
| ---         | ---                              |

Comments starting with # are ignored.

# **Output File Format**

The maze is exported using **one hexadecimal digit per cell**.

Each bit represents a wall:

| **Bit** | **Direction** |
| ------- | ------------- |
| 0       | North         |
| ---     | ---           |
| 1       | East          |
| ---     | ---           |
| 2       | South         |
| ---     | ---           |
| 3       | West          |
| ---     | ---           |

Example:

A = 1010 → East and West walls closed

3 = 0011 → North and East walls closed

The output file also contains:

&lt;maze grid&gt;

entry_x,entry_y

exit_x,exit_y

&lt;shortest_path&gt;

Where the path is encoded with:

N E S W

# **Controls**

During execution the following keys are available:

| **Key** | **Action**                  |
| ------- | --------------------------- |
| R       | Regenerate maze             |
| ---     | ---                         |
| P       | Toggle shortest path        |
| ---     | ---                         |
| T       | Change visual theme         |
| ---     | ---                         |
| A       | Change generation algorithm |
| ---     | ---                         |
| ESC     | Quit                        |
| ---     | ---                         |

# **Maze Generation Algorithm**

The project supports three algorithms:

### **DFS (Recursive Backtracking)**

- Uses a stack
- Carves paths by visiting unvisited neighbours
- Produces long corridors and fewer branches

Advantages:

- Simple implementation
- Generates visually interesting mazes

### **Prim's Algorithm**

- Uses a frontier list
- Randomly connects frontier cells to the maze

Advantages:

- Produces balanced maze density
- Avoids long corridors

### **Kruskal's Algorithm**

- Treats the maze as a graph
- Uses a **Union-Find structure**
- Randomly removes walls while preventing cycles

Advantages:

- Guarantees perfect maze generation
- Based on classic graph theory

# **Pathfinding Algorithm**

The shortest path between entry and exit is computed using **Breadth-First Search (BFS)**.

This algorithm:

- guarantees the shortest path
- works efficiently on grid graphs
- reconstructs the path using parent tracking

# **Special Maze Constraints**

The generator ensures that:

- entry and exit are valid
- maze cells remain connected
- walls between adjacent cells are consistent
- corridors do not form large open areas
- a visible **"42" pattern** appears in the maze using blocked cells when the maze size allows it.

# **Reusable Module**

The maze generation logic is implemented in the MazeGenerator class.

It can be reused independently from the graphical interface.

Example usage:

from maze_generator import MazeGenerator

from helpers import MazeConfig

config = MazeConfig(

width=20,

height=20,

entry=(0,0),

exit=(19,19),

output_file="maze.txt",

perfect=True,

seed=42

)

generator = MazeGenerator(config, algorithm="DFS")

while not generator.carving_finished:

generator.carve_step()

maze = generator.maze

The generated maze structure can then be used for visualization or exported to file.

# **Project Architecture**

.

├── a_maze_ing.py

├── maze_app.py

├── maze_generator.py

├── find_path.py

├── helpers.py

├── config.txt

└── README.md

### **File overview**

| **File**          | **Description**                           |
| ----------------- | ----------------------------------------- |
| a_maze_ing.py     | Main entry point                          |
| ---               | ---                                       |
| maze_app.py       | Graphical interface and user interactions |
| ---               | ---                                       |
| maze_generator.py | Maze generation algorithms                |
| ---               | ---                                       |
| find_path.py      | BFS shortest path algorithm               |
| ---               | ---                                       |
| helpers.py        | Configuration parsing and utilities       |
| ---               | ---                                       |
| config.txt        | Example configuration                     |
| ---               | ---                                       |

# **Team & Project Management**

### **Roles**

Example:

| **Member** | **Responsibilities**                                           |
| ---------- | -------------------------------------------------------------- |
| Member 1   | Maze generation algorithms                                     |
| ---        | ---                                                            |
| Member 2   | Visualization and MLX interface, Pathfinding and output system |
| ---        | ---                                                            |

### **Planning**

Initial plan:

- Configuration parsing
- Maze generator implementation
- Pathfinding
- Visualization
- Output file export

### **What worked well**

- modular architecture
- algorithm abstraction
- reusable generator module

### **Improvements**

- better performance for very large mazes
- additional visualization modes
- improved animation controls

# **Tools Used**

- Python 3.10
- MiniLibX
- flake8
- mypy
- Git

# **Resources**

Maze generation algorithms:

- <https://en.wikipedia.org/wiki/Maze_generation_algorithm>
- <https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap>
- <https://en.wikipedia.org/wiki/Breadth-first_search>

# **AI Usage**

AI tools were used to assist with:

- README drafting
- algorithm explanations
- code documentation improvements

All generated content was reviewed and validated before integration into the project.