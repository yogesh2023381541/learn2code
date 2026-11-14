import json
from pathlib import Path


TASKS = [
    ("Tree Node Count", "tree-node-count", "Easy", "Return the number of nodes in a binary tree encoded in level order.", "7 1 2 3 4 5 6 7", "7", "3 9 4 2", "3"),
    ("Tree Height", "tree-height", "Easy", "Return the number of nodes on the longest root-to-leaf path.", "7 1 2 3 4 5 6 7", "3", "1 9 0", "2"),
    ("Tree Leaf Count", "tree-leaf-count", "Easy", "Count nodes with no children.", "7 1 2 3 4 5 6 7", "4", "5 1 2 3 4 5", "3"),
    ("Preorder Walk", "preorder-walk", "Easy", "Print a binary tree in root-left-right order.", "7 1 2 3 4 5 6 7", "1 2 4 5 3 6 7", "3 9 4 2", "9 4 2"),
    ("Inorder Walk", "inorder-walk", "Easy", "Print a binary tree in left-root-right order.", "7 1 2 3 4 5 6 7", "4 2 5 1 6 3 7", "3 9 4 2", "4 9 2"),
    ("Postorder Walk", "postorder-walk", "Easy", "Print a binary tree in left-right-root order.", "7 1 2 3 4 5 6 7", "4 5 2 6 7 3 1", "3 9 4 2", "4 2 9"),
    ("Level Order Walk", "level-order-walk", "Easy", "Print values level by level from left to right.", "7 1 2 3 4 5 6 7", "1 2 3 4 5 6 7", "5 8 4 10 2 6", "8 4 10 2 6"),
    ("Right Edge View", "right-edge-view", "Medium", "Print the last visible node at every depth when viewed from the right.", "7 1 2 3 4 5 6 7", "1 3 7", "5 1 2 3 4 5", "1 2 5"),
    ("Left Edge View", "left-edge-view", "Medium", "Print the first visible node at every depth when viewed from the left.", "7 1 2 3 4 5 6 7", "1 2 4", "5 1 2 3 4 5", "1 2 4"),
    ("Tree Width", "tree-width", "Medium", "Return the largest number of nodes appearing at one depth.", "7 1 2 3 4 5 6 7", "4", "5 1 2 3 4 5", "2"),
    ("Balanced Tree Check", "balanced-tree-check", "Easy", "Check whether every node has left and right subtree heights differing by at most one.", "7 1 2 3 4 5 6 7", "true", "5 1 2 3 4 5", "true"),
    ("Tree Diameter Edges", "tree-diameter-edges", "Medium", "Return the greatest number of edges on a path between any two nodes.", "7 1 2 3 4 5 6 7", "4", "5 1 2 3 4 5", "3"),
    ("Mirror Tree Check", "mirror-tree-check", "Easy", "Determine whether the tree is symmetric around its root.", "7 1 2 2 3 4 4 3", "true", "5 1 2 2 3 3", "false"),
    ("Invert Tree", "invert-tree", "Easy", "Swap left and right children at every node and print level order.", "7 1 2 3 4 5 6 7", "1 3 2 7 6 5 4", "3 8 4 2", "8 4 2"),
    ("Root To Leaf Sum", "root-to-leaf-sum", "Easy", "Determine whether some root-to-leaf path has the target sum.", "7 5 4 8 11 7 2 13|22", "true", "3 1 2 3|9", "false"),
    ("Path Sum Count", "path-sum-count", "Medium", "Count root-to-leaf paths whose values sum to target.", "7 5 4 8 11 7 2 13|22", "1", "5 1 2 3 4 5|6", "2"),
    ("All Root Leaf Paths", "all-root-leaf-paths", "Easy", "Print every root-to-leaf path in preorder, joining values with arrows.", "3 1 2 3", "1->2|1->3", "1 9", "9"),
    ("Lowest Common Ancestor", "lowest-common-ancestor", "Medium", "Return the value of the lowest common ancestor of two values in a binary tree.", "7 3 5 1 6 2 4 0|1|4", "5", "5 1 2 3 4 5|3|5", "1"),
    ("Distance Between Nodes", "distance-between-nodes", "Medium", "Return the number of edges on the shortest path between two present values.", "7 1 2 3 4 5 6 7|4|7", "4", "3 9 4 2|4|2", "2"),
    ("BST Search", "bst-search", "Easy", "Search a binary search tree and report whether target exists.", "7 5 3 7 2 4 6 8|6", "true", "5 5 3 7 2 4 6 8|1", "false"),
    ("BST Insert", "bst-insert", "Easy", "Insert a value into a BST and print its inorder traversal.", "5 4 2 6 1 3|5", "1 2 3 4 5 6", "3 10 5 15|1", "1 5 10 15"),
    ("BST Validate", "bst-validate", "Medium", "Check whether a level-order tree satisfies strict BST ordering.", "7 5 3 7 2 4 6 8", "true", "3 5 4 6", "false"),
    ("BST Kth Smallest", "bst-kth-smallest", "Medium", "Return the k-th smallest value in a BST using one-based k.", "7 5 3 7 2 4 6 8|4", "5", "3 2 1 3|2", "2"),
    ("BST Range Sum", "bst-range-sum", "Easy", "Sum all BST values within inclusive low and high bounds.", "7 5 3 7 2 4 6 8|4|7", "22", "3 10 5 15|6|20", "25"),
    ("Sorted Array To BST", "sorted-array-to-bst", "Medium", "Build a height-balanced BST from a sorted array and print its level order.", "5 1 2 3 4 5", "3 1 4 2 5", "3 -2 0 2", "0 -2 2"),
    ("Tree Serialization", "tree-serialization", "Medium", "Serialize a level-order tree by retaining null markers for missing children.", "3 1 2 3", "1,2,3", "5 1 2 null 4 5", "1,2,null,4,5"),
    ("Tree Deserialization", "tree-deserialization", "Medium", "Deserialize a comma-separated level record and print preorder values.", "1,2,3", "1 2 3", "1,2,null,4,5", "1 2 4 5"),
    ("Vertical Column Order", "vertical-column-order", "Hard", "Print columns from left to right, and nodes top to bottom within each column.", "7 1 2 3 4 5 6 7", "4 2 1 5 6 3 7", "3 9 4 2", "4 9 2"),
    ("Diagonal Tree Sum", "diagonal-tree-sum", "Medium", "Return the sum of values on the requested root-right diagonal.", "7 1 2 3 4 5 6 7|1", "10", "5 1 2 3 4 5|0", "1"),
    ("Boundary Walk", "boundary-walk", "Hard", "Print root, left boundary, leaves, and reversed right boundary without duplicates.", "7 1 2 3 4 5 6 7", "1 2 4 5 6 7 3", "5 1 2 3 4 5", "1 2 4 5 3"),
    ("Maximum Path Sum", "maximum-path-sum", "Hard", "Return the maximum sum of a non-empty path between any two nodes.", "7 -10 9 20 null null 15 7", "42", "3 1 2 3", "6"),
    ("Duplicate Subtree Signatures", "duplicate-subtree-signatures", "Hard", "Count distinct subtree shapes with identical value structure appearing at least twice.", "7 1 2 3 4 5 4 3", "1", "5 1 2 3 4 5", "0"),
    ("Complete Tree Check", "complete-tree-check", "Medium", "Check whether every level is full except possibly the last, which is filled left to right.", "7 1 2 3 4 5 6 7", "true", "5 1 2 3 null 5", "false"),
    ("Full Tree Check", "full-tree-check", "Easy", "Check whether every node has either zero or two children.", "7 1 2 3 4 5 6 7", "true", "5 1 2 3 4 5", "false"),
    ("Nodes At Distance K", "nodes-at-distance-k", "Medium", "Print values exactly k edges from target, sorted ascending.", "7 3 5 1 6 2 4 0|5|2", "1 4", "7 1 2 3 4 5 6 7|3|1", "2 4"),
    ("Tree Right Link Levels", "tree-right-link-levels", "Medium", "Connect nodes across each level and print each level using next links.", "7 1 2 3 4 5 6 7", "1|2 3|4 5 6 7", "3 8 4 2", "8|4 2"),
    ("Expression Tree Value", "expression-tree-value", "Medium", "Evaluate a binary expression tree whose leaves are integers and internal nodes are operators.", "5 + 2 * 3 4", "11", "3 - 10 4", "6"),
    ("Tree Color Frequency", "tree-color-frequency", "Medium", "Return the most frequent value in a tree, choosing the smallest value on ties.", "7 2 1 2 3 1 2 3", "2", "3 5 4 5", "5"),
    ("Forest After Deletion", "forest-after-deletion", "Hard", "Delete listed values from a tree and print the roots of resulting trees in ascending order.", "7 1 2 3 4 5 6 7|3 5", "1 6", "3 1 2 3|1", "2 3"),
    ("Tree Level Averages", "tree-level-averages", "Easy", "Print the average value at each depth, rounded to two decimal places.", "7 1 2 3 4 5 6 7", "1.00 2.50 5.50", "3 9 4 2", "9.00 3.00"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # Parse the documented tree input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/);\n// Parse the documented tree input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        Scanner scanner = new Scanner(System.in);\n        // Parse the documented tree input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented tree input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    return {
        "title": title,
        "slug": f"trees-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": "Trees",
        "topic": "Trees",
        "tags": ["trees", "binary-tree" if "bst" not in slug else "bst"],
        "description": (
            f"{operation} Trees use level-order notation with `null` for an absent child when needed. "
            "Node values are integers unless an expression or serialization task states otherwise."
        ),
        "input_format": "The input is a whitespace-separated level-order record; the examples show optional parameters and null markers.",
        "output_format": "Print the requested value or traversal using single spaces, pipes, or commas exactly as described.",
        "constraints": "1 <= number of nodes <= 100000; -1000000000 <= node value <= 1000000000; referenced values exist when required.",
        "examples": [{"input": public_input, "output": public_output}, {"input": hidden_input, "output": hidden_output}],
        "hints": [
            "Choose BFS for level-based views and DFS for path, height, and subtree properties.",
            "For BST tasks, use the ordering invariant to prune entire subtrees.",
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
    path = Path(__file__).parents[1] / "datasets" / "trees.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"problems": [make_problem(i, task) for i, task in enumerate(TASKS, 1)]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(TASKS)} problems to {path}")


if __name__ == "__main__":
    main()
