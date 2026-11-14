import json
from pathlib import Path


TASKS = [
    ("Graph Node Count", "graph-node-count", "Easy", "Return the number of distinct vertices in an edge list.", "4 0-1 1-2 2-3 3-0", "4", "3 5-6", "3"),
    ("Graph Degree List", "graph-degree-list", "Easy", "Print the degree of every vertex from 0 through n-1.", "4 0-1 1-2 2-3 3-0", "2 2 2 2", "3 0-1 1-2", "1 2 1"),
    ("Undirected Connectivity", "undirected-connectivity", "Easy", "Determine whether every vertex is reachable from vertex 0.", "4 0-1 1-2 2-3", "true", "4 0-1 2-3", "false"),
    ("Directed Reachability", "directed-reachability", "Easy", "Determine whether a directed path exists from source to target.", "4 0>1 1>2 2>3|0|3", "true", "4 0>1 2>3|0|3", "false"),
    ("Breadth First Order", "breadth-first-order", "Easy", "Print vertices in BFS order from a starting vertex.", "5 0-1 0-2 1-3 2-4|0", "0 1 2 3 4", "4 0-1 1-2 2-3|3", "3 2 1 0"),
    ("Depth First Order", "depth-first-order", "Easy", "Print vertices in recursive DFS preorder from a starting vertex.", "5 0-1 0-2 1-3 2-4|0", "0 1 3 2 4", "4 0-1 1-2 2-3|3", "3 2 1 0"),
    ("Connected Component Count", "connected-component-count", "Easy", "Return the number of connected components in an undirected graph.", "5 0-1 1-2 3-4", "2", "4 0-1", "3"),
    ("Component Sizes", "component-sizes", "Medium", "Print connected-component sizes in ascending order.", "7 0-1 1-2 3-4 5-6", "2 2 3", "4 0-1 1-2", "1 3"),
    ("Cycle In Undirected Graph", "cycle-in-undirected-graph", "Medium", "Determine whether an undirected graph contains a cycle.", "4 0-1 1-2 2-3", "false", "4 0-1 1-2 2-0", "true"),
    ("Cycle In Directed Graph", "cycle-in-directed-graph", "Medium", "Determine whether a directed graph contains a cycle.", "3 0>1 1>2", "false", "3 0>1 1>2 2>0", "true"),
    ("Bipartite Check", "bipartite-check", "Medium", "Determine whether an undirected graph can be colored with two colors.", "4 0-1 1-2 2-3 3-0", "true", "3 0-1 1-2 2-0", "false"),
    ("Topological Order", "topological-order", "Medium", "Print one lexicographically smallest topological ordering, or -1 if impossible.", "4 0>1 0>2 1>3 2>3", "0 1 2 3", "3 0>1 1>2 2>0", "-1"),
    ("Course Completion", "course-completion", "Medium", "Determine whether all courses can be completed given prerequisite edges.", "3 0>1 1>2", "true", "3 0>1 1>2 2>0", "false"),
    ("Transitive Reach Counts", "transitive-reach-counts", "Medium", "For each vertex, count distinct vertices reachable by directed paths.", "4 0>1 1>2 2>3", "3 2 1 0", "3 0>1 0>2", "2 0 0"),
    ("Shortest Unweighted Path", "shortest-unweighted-path", "Easy", "Return the number of edges in a shortest undirected path, or -1.", "5 0-1 1-2 2-3 0-4|0|3", "3", "4 0-1 2-3|0|3", "-1"),
    ("Shortest Directed Path", "shortest-directed-path", "Medium", "Return the number of edges in a shortest directed path, or -1.", "5 0>1 1>2 0>3 3>4 4>2|0|2", "2", "3 0>1 2>1|0|2", "-1"),
    ("Dijkstra Distance", "dijkstra-distance", "Medium", "Return the minimum non-negative weighted distance from source to target.", "4 0-1:4 0-2:1 2-1:2 1-3:1 2-3:5|0|3", "4", "3 0-1:7 1-2:2|0|2", "9"),
    ("Bellman Ford Distance", "bellman-ford-distance", "Medium", "Return a shortest distance allowing negative edges, or NEGATIVE_CYCLE.", "3 0>1:4 1>2:-2 0>2:5|0|2", "2", "3 0>1:1 1>2:-2 2>0:-2|0|2", "NEGATIVE_CYCLE"),
    ("Floyd Warshall Query", "floyd-warshall-query", "Hard", "Return the all-pairs shortest distance for a source-target query, or -1.", "3 0-1:3 1-2:4 0-2:10|0|2", "7", "3 0-1:3|0|2", "-1"),
    ("Minimum Spanning Tree Weight", "minimum-spanning-tree-weight", "Medium", "Return the weight of a minimum spanning tree, or -1 if disconnected.", "4 0-1:1 1-2:2 2-3:3 0-3:9", "6", "3 0-1:4 1-2:5", "9"),
    ("Kruskal Edge Count", "kruskal-edge-count", "Easy", "Return how many edges are selected by Kruskal before the graph becomes connected.", "4 0-1:1 1-2:2 2-3:3 0-3:9", "3", "3 0-1:4 1-2:5", "2"),
    ("Prim Frontier Sum", "prim-frontier-sum", "Medium", "Compute an MST weight using a growing frontier, or -1 if disconnected.", "5 0-1:2 0-2:3 1-2:1 1-3:4 2-4:5 3-4:2", "10", "3 0-1:8", "-1"),
    ("Bridge Count", "bridge-count", "Hard", "Count undirected edges whose removal increases the number of components.", "5 0-1 1-2 2-0 1-3 3-4", "2", "4 0-1 1-2 2-3 3-0", "0"),
    ("Articulation Count", "articulation-count", "Hard", "Count vertices whose removal disconnects an undirected graph.", "5 0-1 1-2 2-0 1-3 3-4", "2", "4 0-1 1-2 2-3", "2"),
    ("Strong Component Count", "strong-component-count", "Hard", "Return the number of strongly connected components in a directed graph.", "5 0>1 1>2 2>0 2>3 3>4", "3", "3 0>1 1>2 2>0", "1"),
    ("Strong Component Labels", "strong-component-labels", "Hard", "Print the component label of each vertex, with labels ordered by smallest member.", "4 0>1 1>0 1>2 2>3 3>2", "0 0 2 2", "3 0>1 1>2", "0 1 2"),
    ("Word Ladder Distance", "word-ladder-distance", "Medium", "Return the fewest one-letter changes between start and target using a supplied dictionary.", "hit|cog|hot dot dog lot log cog", "4", "cat|dog|cot cog dog", "-1"),
    ("Grid Island Count", "grid-island-count", "Medium", "Count groups of adjacent land cells in a rectangular 0/1 grid.", "3 4 1100 1100 0010", "2", "2 3 111 010", "1"),
    ("Grid Flood Fill", "grid-flood-fill", "Easy", "Change a connected region of one color to another and print the grid.", "3 3 111 101 111|1|1|2", "222 202 222", "2 2 00 01|1|1|2", "00 02"),
    ("Grid Shortest Route", "grid-shortest-route", "Medium", "Return the shortest four-direction route from top-left to bottom-right, or -1.", "3 3 010 010 000", "4", "2 2 01 10", "-1"),
    ("Grid Walls And Gates", "grid-walls-and-gates", "Medium", "Fill each empty grid cell with distance to its nearest gate, leaving walls unchanged.", "3 4 G### .##. .G..", "G### 1##2 0G1", "2 2 G. .#", "G1 1#"),
    ("Grid Bipartite Regions", "grid-bipartite-regions", "Medium", "Return whether all adjacent open cells can be colored in two colors.", "3 3 010 101 010", "true", "2 2 11 11", "true"),
    ("Network Delay", "network-delay", "Medium", "Return the time for a signal from source to reach every vertex, or -1.", "4 2 2>1:1 2>3:1 3>4:1|2", "2", "3 2 1>2:1|1", "-1"),
    ("Cheapest Flight Stops", "cheapest-flight-stops", "Hard", "Return the cheapest directed route using at most k intermediate stops, or -1.", "4 0>1:100 1>2:100 0>2:500 2>3:50|0|3|1", "250", "3 0>1:5 1>2:5|0|2|0", "-1"),
    ("Alien Alphabet Order", "alien-alphabet-order", "Hard", "Infer a valid character order from sorted alien words, or -1 if contradictory.", "3 baa abcd abca", "b a c d", "2 abc ab", "-1"),
    ("Euler Trail Check", "euler-trail-check", "Medium", "Determine whether an undirected graph has a trail using every edge exactly once.", "4 0-1 1-2 2-3", "true", "4 0-1 1-2 2-0 0-3", "false"),
    ("Hamiltonian Path Count", "hamiltonian-path-count", "Hard", "Count directed paths that visit every vertex exactly once.", "4 0>1 1>2 2>3 0>2 1>3", "1", "3 0>1 1>0 1>2 2>1", "0"),
    ("Graph Clone Labels", "graph-clone-labels", "Easy", "Clone an undirected graph and print BFS labels of the clone from the supplied start.", "4 0-1 0-2 1-3 2-3|0", "0 1 2 3", "3 0-1|1", "1 0"),
    ("Reachable Weighted Budget", "reachable-weighted-budget", "Medium", "Count vertices reachable from source with shortest distance at most budget.", "5 0-1:2 1-2:3 0-3:6 3-4:1|0|5", "3", "4 0-1:4 1-2:4 2-3:4|0|7", "2"),
    ("Grid Rotting Spread", "grid-rotting-spread", "Medium", "Return minutes needed for every fresh cell to become rotten through four-direction spread, or -1.", "3 3 210 111 011", "4", "2 2 20 01", "-1"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # Parse the documented graph input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/);\n// Parse the documented graph input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        Scanner scanner = new Scanner(System.in);\n        // Parse the documented graph input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented graph input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    weighted = any(token in slug for token in ("distance", "mst", "kruskal", "prim", "delay", "flight", "budget", "floyd"))
    return {
        "title": title,
        "slug": f"graphs-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": "Graphs",
        "topic": "Graphs",
        "tags": ["graphs", "weighted" if weighted else "traversal"],
        "description": (
            f"{operation} Vertices are numbered from 0 and edges use the notation shown in the examples. "
            "Unless stated otherwise, repeated edges do not add new vertices."
        ),
        "input_format": "The input is a whitespace-separated edge record; directed edges use >, undirected edges use -, and weights use :.",
        "output_format": "Print the requested number, boolean, ordering, or sequence on one line.",
        "constraints": "1 <= vertices <= 100000; 0 <= edges <= 200000; weights fit signed 32-bit integers.",
        "examples": [{"input": public_input, "output": public_output}, {"input": hidden_input, "output": hidden_output}],
        "hints": [
            "Choose BFS for unweighted distance and DFS for components or cycle discovery.",
            "For weighted graphs, select the algorithm whose assumptions match edge weights and direction.",
        ],
        "test_cases": [
            {"input": public_input, "expected_output": public_output, "is_hidden": False, "time_limit_ms": 3000, "memory_limit_mb": 256},
            {"input": hidden_input, "expected_output": hidden_output, "is_hidden": True, "time_limit_ms": 3000, "memory_limit_mb": 256},
        ],
        "starter_code": {language: starter(language) for language in ("python", "java", "cpp", "javascript")},
        "time_limit_ms": 3000,
        "memory_limit_mb": 256,
        "is_published": False,
    }


def main() -> None:
    path = Path(__file__).parents[1] / "datasets" / "graphs.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"problems": [make_problem(i, task) for i, task in enumerate(TASKS, 1)]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(TASKS)} problems to {path}")


if __name__ == "__main__":
    main()
