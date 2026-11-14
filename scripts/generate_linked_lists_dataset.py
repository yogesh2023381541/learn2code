import json
from pathlib import Path


TASKS = [
    ("List Length", "list-length", "Easy", "Return the number of nodes in a singly linked list.", "4 3 8 1 6", "4", "1 9", "1"),
    ("List Sum", "list-sum", "Easy", "Return the sum of every node value.", "5 2 4 -1 7 3", "15", "3 -4 0 9", "5"),
    ("List Search", "list-search", "Easy", "Return the first zero-based index containing target, or -1.", "5 4 8 2 8 1|8", "1", "3 5 6 7|4", "-1"),
    ("Reverse Chain", "reverse-chain", "Easy", "Reverse a singly linked list and print its values.", "5 1 2 3 4 5", "5 4 3 2 1", "3 9 0 -2", "-2 0 9"),
    ("Middle Node Value", "middle-node-value", "Easy", "Return the middle value; for even length choose the second middle node.", "5 1 2 3 4 5", "3", "4 8 6 2 0", "2"),
    ("Remove First Target", "remove-first-target", "Easy", "Remove only the first node equal to target and print the remaining list.", "5 2 4 2 7 9|2", "4 2 7 9", "3 1 2 3|8", "1 2 3"),
    ("Remove All Targets", "remove-all-targets", "Easy", "Remove every node equal to target.", "6 1 3 3 2 3 4|3", "1 2 4", "4 5 5 5 5|5", ""),
    ("Insert At Position", "insert-at-position", "Easy", "Insert a value before the node at zero-based position; position n appends.", "4 4 6 8 10|2|7", "4 6 7 8 10", "2 1 2|0|9", "9 1 2"),
    ("Delete At Position", "delete-at-position", "Easy", "Delete the node at a valid zero-based position.", "5 7 8 9 10 11|3", "7 8 9 11", "1 4|0", ""),
    ("Merge Sorted Chains", "merge-sorted-chains", "Easy", "Merge two non-decreasing lists into one non-decreasing list.", "3 1 4 7|4 2 3 8 9", "1 2 3 4 7 8 9", "0 |3 -2 0 5", "-2 0 5"),
    ("Remove Consecutive Duplicates", "remove-consecutive-duplicates", "Easy", "In a sorted list, keep one node from each equal-value run.", "7 1 1 2 2 2 4 5", "1 2 4 5", "4 9 9 9 9", "9"),
    ("Palindrome Chain", "palindrome-chain", "Easy", "Determine whether the list values read identically from both ends.", "5 1 2 3 2 1", "true", "4 1 2 2 3", "false"),
    ("Cycle Entry Index", "cycle-entry-index", "Medium", "The final node points to the node at index entry; return entry, or -1 for no cycle.", "5 10 20 30 40 50|1", "1", "4 3 6 9 12|-1", "-1"),
    ("Cycle Presence", "cycle-presence", "Easy", "Determine whether a next-pointer cycle exists.", "3 7 8 9|0", "true", "3 7 8 9|-1", "false"),
    ("Intersection Index", "intersection-index", "Medium", "Two lists share a suffix beginning at the supplied value; return its first index in list A, or -1.", "5 1 2 8 9 10|4 3 4 8 9 10", "2", "3 1 2 3|2 4 5", "-1"),
    ("Nth From End", "nth-from-end", "Easy", "Return the value n positions from the end, where n is one-based.", "5 4 8 1 6 3|2", "6", "3 9 5 2|3", "9"),
    ("Rotate Chain", "rotate-chain", "Medium", "Rotate a list to the right by k positions.", "5 1 2 3 4 5|2", "4 5 1 2 3", "4 7 8 9 0|5", "9 0 7 8"),
    ("Pairwise Swap", "pairwise-swap", "Easy", "Swap adjacent nodes in pairs without changing node values.", "5 1 2 3 4 5", "2 1 4 3 5", "4 8 7 6 5", "7 8 5 6"),
    ("Reverse Fixed Groups", "reverse-fixed-groups", "Medium", "Reverse every complete group of k nodes; leave a short final group unchanged.", "7 1 2 3 4 5 6 7|3", "3 2 1 6 5 4 7", "5 9 8 7 6 5|2", "8 9 6 7 5"),
    ("Sort Linked Values", "sort-linked-values", "Medium", "Rearrange nodes into non-decreasing value order.", "5 4 1 5 2 3", "1 2 3 4 5", "4 0 -1 -1 2", "-1 -1 0 2"),
    ("Add Number Chains", "add-number-chains", "Medium", "Each list stores one digit per node in forward order; print their sum in forward order.", "3 7 2 4|4 5 6 4", "1 2 8 8", "2 9 9|1 1", "1 0 0"),
    ("Odd Even Node Order", "odd-even-node-order", "Medium", "Place nodes at odd positions first, followed by nodes at even positions.", "6 1 2 3 4 5 6", "1 3 5 2 4 6", "5 9 8 7 6 5", "9 7 5 8 6"),
    ("Partition Around Pivot", "partition-around-pivot", "Medium", "Move values below pivot before values at least pivot while preserving order inside both groups.", "6 1 4 3 2 5 2|3", "1 2 2 4 3 5", "4 5 1 8 0|4", "1 0 5 8"),
    ("Remove Zero-Sum Runs", "remove-zero-sum-runs", "Medium", "Repeatedly remove contiguous runs whose values sum to zero.", "5 1 2 -3 3 1", "3 1", "4 1 -1 2 2", "2 2"),
    ("Duplicate Chain", "duplicate-chain", "Easy", "Create a list containing each input value twice consecutively.", "3 4 1 9", "4 4 1 1 9 9", "1 -5", "-5 -5"),
    ("Split Alternating Chains", "split-alternating-chains", "Easy", "Print nodes at odd positions, then nodes at even positions.", "5 1 2 3 4 5", "1 3 5|2 4", "4 8 6 4 2", "8 4|6 2"),
    ("Compare Chains", "compare-chains", "Easy", "Compare two lists lexicographically by values and return -1, 0, or 1.", "3 1 4 6|3 1 5 0", "-1", "2 7 8|2 7 8", "0"),
    ("Flatten Sorted Levels", "flatten-sorted-levels", "Hard", "Merge k sorted linked lists supplied as pipe-separated rows.", "2 1 4|3 0 2 5|1 3", "0 1 2 3 4 5", "2 -1 7|2 0 8", "-1 0 7 8"),
    ("Reverse Between Bounds", "reverse-between-bounds", "Medium", "Reverse nodes from one-based position left through right, leaving the rest unchanged.", "5 1 2 3 4 5|2|4", "1 4 3 2 5", "4 7 8 9 0|1|2", "8 7 9 0"),
    ("Twin Sum Maximum", "twin-sum-maximum", "Medium", "For an even-length list, pair node i with node n-1-i and return the largest pair sum.", "6 5 4 3 2 1 0", "5", "4 8 1 9 2", "10"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().splitlines()\n    # Parse the documented linked-list input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\r?\\n/);\n// Parse the documented linked-list input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));\n        // Parse the documented linked-list input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented linked-list input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    return {
        "title": title,
        "slug": f"linked-lists-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": "Linked Lists",
        "topic": "Linked Lists",
        "tags": ["linked-list", slug.split("-")[0]],
        "description": (
            f"{operation} Inputs use the pipe-separated notation shown in the examples for parameters or multiple "
            "lists. Values are integers and output values must be separated by single spaces."
        ),
        "input_format": "The input is a whitespace- or pipe-separated record; the examples show the exact token order and list boundaries.",
        "output_format": "Print the requested value or linked-list sequence on one line.",
        "constraints": "1 <= list length <= 100000; -1000000000 <= node value <= 1000000000; parameters are valid.",
        "examples": [{"input": public_input, "output": public_output}, {"input": hidden_input, "output": hidden_output}],
        "hints": [
            "Use a dummy node when an operation may change the head.",
            "For two-ended operations, compare a forward traversal with a reversed or fast/slow traversal.",
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
    path = Path(__file__).parents[1] / "datasets" / "linked_lists.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"problems": [make_problem(i, task) for i, task in enumerate(TASKS, 1)]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(TASKS)} problems to {path}")


if __name__ == "__main__":
    main()
