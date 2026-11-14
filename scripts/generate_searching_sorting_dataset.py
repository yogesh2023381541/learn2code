import json
from pathlib import Path


TASKS = [
    ("Binary Search Index", "binary-search-index", "Easy", "Return the index of target in a sorted array, or -1.", "5 1 3 5 7 9|7", "3", "4 2 4 6 8|5", "-1"),
    ("Lower Bound Position", "lower-bound-position", "Easy", "Return the first index whose value is at least target.", "5 1 3 3 7 9|3", "1", "4 2 4 6 8|5", "2"),
    ("Upper Bound Position", "upper-bound-position", "Easy", "Return the first index whose value is greater than target.", "5 1 3 3 7 9|3", "3", "4 2 4 6 8|9", "4"),
    ("First And Last Target", "first-and-last-target", "Easy", "Return the first and last index of target in a sorted array.", "7 1 2 2 2 3 4 5|2", "1 3", "4 1 3 5 7|4", "-1 -1"),
    ("Rotated Search", "rotated-search", "Medium", "Find target in a sorted array rotated at an unknown pivot.", "7 4 5 6 7 0 1 2|0", "4", "5 6 7 1 2 3 4|5", "-1"),
    ("Rotated Minimum", "rotated-minimum", "Medium", "Return the minimum value in a rotated sorted array.", "5 4 5 1 2 3", "1", "4 2 2 2 2", "2"),
    ("Peak Array Index", "peak-array-index", "Medium", "Return an index of a value greater than its available neighbours.", "5 1 3 5 4 2", "2", "4 4 3 2 1", "0"),
    ("Integer Square Root", "integer-square-root", "Easy", "Return floor square root of non-negative x without floating-point square root.", "27", "5", "1", "1"),
    ("Kth Missing Positive", "kth-missing-positive", "Medium", "Return the k-th positive integer absent from a strictly increasing array.", "5 2 3 4 7 11|5", "9", "3 1 2 3|2", "6"),
    ("Search In Matrix", "search-in-matrix", "Medium", "Find target in a row-major matrix whose rows and columns are sorted.", "3 4 1 4 7 11 2 5 8 12 3 6 9 16|8", "true", "2 2 1 3 2 4|5", "false"),
    ("Merge Sort Values", "merge-sort-values", "Easy", "Sort integer values in non-decreasing order using merge sort.", "6 5 1 4 2 8 0", "0 1 2 4 5 8", "4 -1 -3 -2 0", "-3 -2 -1 0"),
    ("Quick Sort Values", "quick-sort-values", "Easy", "Sort integer values in non-decreasing order using partitioning.", "5 3 1 2 3 0", "0 1 2 3 3", "3 9 8 7", "7 8 9"),
    ("Counting Sort Range", "counting-sort-range", "Easy", "Sort non-negative values whose maximum is small.", "7 4 2 2 8 3 3 1", "1 2 2 3 3 4 8", "4 0 0 1 0", "0 0 0 1"),
    ("Dutch Flag Sort", "dutch-flag-sort", "Medium", "Sort an array containing only 0, 1, and 2 in one pass.", "6 2 0 2 1 1 0", "0 0 1 1 2 2", "4 1 2 0 1", "0 1 1 2"),
    ("Sort By Parity", "sort-by-parity", "Easy", "Move even values before odd values, preserving order within each group.", "6 3 2 4 1 5 6", "2 4 6 3 1 5", "4 1 3 5 7", "1 3 5 7"),
    ("Inversion Count", "inversion-count", "Hard", "Count pairs i<j with values[i] greater than values[j].", "5 2 4 1 3 5", "3", "4 4 3 2 1", "6"),
    ("Kth Largest Selection", "kth-largest-selection", "Medium", "Return the k-th largest value using one-based k.", "6 3 2 1 5 6 4|2", "5", "4 -1 -2 -3 -4|4", "-1"),
    ("Median Of Two Sorted", "median-of-two-sorted", "Hard", "Return the median of two sorted arrays; print .5 when needed.", "2 1 3|3 2 4 6", "3.00", "1 1|1 2", "1.50"),
    ("Closest Pair Sum", "closest-pair-sum", "Medium", "Find a pair with sum closest to target and print the smaller pair first.", "5 1 4 7 10 12|15", "4 12", "4 -5 0 8 20|7", "0 8"),
    ("Three Sum Zero", "three-sum-zero", "Medium", "Print the number of distinct value triples with sum zero.", "6 -1 0 1 2 -1 -4", "2", "4 1 2 3 4", "0"),
    ("Merge Intervals", "merge-intervals", "Medium", "Merge overlapping inclusive intervals and print them in order.", "4 1-3 2-6 8-10 9-12", "1-6 8-12", "2 1-1 2-2", "1-1 2-2"),
    ("Insert Interval", "insert-interval", "Medium", "Insert an interval into sorted disjoint intervals and merge overlaps.", "2 1-3 6-9|2-5", "1-5 6-9", "1 5-7|1-2", "1-2 5-7"),
    ("Meeting Rooms", "meeting-rooms", "Easy", "Determine whether all intervals can be attended without overlap.", "3 0-30 5-10 15-20", "false", "2 7-10 2-4", "true"),
    ("Minimum Meeting Rooms", "minimum-meeting-rooms", "Medium", "Return the minimum number of rooms needed for intervals.", "3 0-30 5-10 15-20", "2", "2 7-10 2-4", "1"),
    ("Job Sequencing Profit", "job-sequencing-profit", "Medium", "Schedule unit jobs before deadlines for maximum profit.", "4 2:100 1:19 2:27 1:25", "127", "3 1:10 1:20 1:5", "20"),
    ("Radix Sort Values", "radix-sort-values", "Medium", "Sort non-negative integers using least-significant-digit passes.", "5 170 45 75 90 802", "45 75 90 170 802", "3 3 30 300", "3 30 300"),
    ("External Run Merge", "external-run-merge", "Medium", "Merge sorted runs represented as pipe-separated rows.", "2 1 4 7|0 2 8", "0 1 2 4 7 8", "3 -2 0|1|2 3 5", "-2 0 1 2 3 5"),
    ("Range Frequency Query", "range-frequency-query", "Medium", "Return how many values in inclusive index range l..r equal target.", "6 1 2 1 3 1 4|1|4|1", "2", "4 5 5 5 5|0|2|5", "3"),
    ("Sorted Squares", "sorted-squares", "Easy", "Return squares in non-decreasing order from a sorted array.", "5 -7 -3 -1 4 8", "1 9 16 49 64", "3 -2 0 3", "0 4 9"),
    ("Minimum Increments To Unique", "minimum-increments-to-unique", "Medium", "Increment values until all are unique with minimum total increments.", "5 3 2 1 2 1", "6", "4 0 0 0 0", "6"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # Parse the documented searching/sorting input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/);\n// Parse the documented searching/sorting input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        Scanner scanner = new Scanner(System.in);\n        // Parse the documented searching/sorting input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented searching/sorting input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    return {
        "title": title,
        "slug": f"searching-sorting-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": "Searching and Sorting",
        "topic": "Searching and Sorting",
        "tags": ["searching" if "search" in slug or "bound" in slug else "sorting", slug.split("-")[0]],
        "description": (
            f"{operation} Inputs use the pipe-separated notation shown in examples for separate parameters. "
            "Return indexes, values, intervals, or counts in the requested ordering."
        ),
        "input_format": "The input is a whitespace- or pipe-separated record; the examples show the exact parameter order.",
        "output_format": "Print the requested result on one line with single spaces between sequence items.",
        "constraints": "1 <= n <= 200000; values fit signed 32-bit integers; arrays are sorted where the statement says so.",
        "examples": [{"input": public_input, "output": public_output}, {"input": hidden_input, "output": hidden_output}],
        "hints": [
            "Check whether the input ordering lets you discard half the search space.",
            "When output order is constrained, choose a stable partition or define a tie-break rule explicitly.",
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
    path = Path(__file__).parents[1] / "datasets" / "searching_sorting.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"problems": [make_problem(i, task) for i, task in enumerate(TASKS, 1)]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(TASKS)} problems to {path}")


if __name__ == "__main__":
    main()
