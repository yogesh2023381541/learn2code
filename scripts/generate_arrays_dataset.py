import json
from pathlib import Path


TASKS = [
    ("Array Sum Beacon", "sum", "Easy", "Return the sum of all values in an integer array.", "3 5 2", "10", "4 0 -2 9", "11"),
    ("Alternating Sign Total", "alternating-sign-total", "Easy", "Add values at even indexes and subtract values at odd indexes.", "4 7 3 2", "5", "5 10 1 4 2", "-6"),
    ("Count Above Threshold", "count-above-threshold", "Easy", "Count how many array values are strictly greater than a supplied threshold.", "5 2 7 1 8 3", "2", "4 0 -1 0 2", "1"),
    ("First Valley Position", "first-valley-position", "Easy", "Find the first index whose value is smaller than both immediate neighbours, or return -1.", "5 8 4 6 7 3", "1", "4 1 2 3 4", "-1"),
    ("Stable Zero Shift", "stable-zero-shift", "Easy", "Move every zero to the end while preserving the relative order of non-zero values.", "6 0 4 0 2 7 0", "4 2 7 0 0 0", "5 0 0 1 0 3", "1 3 0 0 0"),
    ("Unique Run Length", "unique-run-length", "Easy", "Return the length of the longest contiguous run containing no repeated value.", "7 1 2 1 3 4 3 5", "3", "5 9 9 9 2 3", "2"),
    ("Nearest Greater Distance", "nearest-greater-distance", "Medium", "For each position, report the distance to the first strictly greater value on its right, or 0.", "5 2 1 3 2 4", "0 1 1 0 0", "4 4 3 2 1", "0 0 0 0"),
    ("Peak Count", "peak-count", "Easy", "Count positions that are greater than both neighbours; endpoints are never peaks.", "7 1 4 2 5 3 6 2", "3", "5 2 2 2 2 2", "0"),
    ("Circular Rotation", "circular-rotation", "Easy", "Rotate an array to the right by k positions and print the resulting sequence.", "5 1 2 3 4 5 2", "4 5 1 2 3", "4 9 8 7 6 6", "7 6 9 8"),
    ("Minimum Window Sum", "minimum-window-sum", "Medium", "Return the smallest sum among all contiguous windows of width k.", "5 4 6 1 3 8 2", "10", "4 2 -1 5 0 3", "4"),
    ("Maximum Window Sum", "maximum-window-sum", "Easy", "Return the largest sum among all contiguous windows of width k.", "5 3 4 -2 7 1 2", "10", "4 -3 -1 -4 -2 2", "-3"),
    ("Prefix Balance Index", "prefix-balance-index", "Medium", "Return the first index where the sum on the left equals the sum on the right.", "5 1 3 2 4 1", "2", "4 2 1 1 2", "1"),
    ("Pair Difference Count", "pair-difference-count", "Medium", "Count index pairs with i less than j whose absolute difference equals d.", "5 1 5 3 4 2 2", "3", "4 1 1 1 1 0", "0"),
    ("Three-Way Partition", "three-way-partition", "Medium", "Partition values into those below, equal to, and above pivot, preserving order inside each group.", "7 4 2 5 3 5 1 5 4", "2 3 1 4 5 5 5 4", "5 3 0 2 3 1 3 2", "0 2 1 3 3"),
    ("Duplicate Distance", "duplicate-distance", "Easy", "Return the minimum distance between equal values, or -1 when every value is unique.", "6 8 3 8 2 3 5", "2", "4 1 2 3 4", "-1"),
    ("Longest Increasing Streak", "longest-increasing-streak", "Easy", "Find the longest contiguous strictly increasing run.", "8 1 2 2 3 4 1 5 6", "3", "5 5 4 3 2 1", "1"),
    ("Rain Basin Total", "rain-basin-total", "Hard", "Given bar heights, calculate total trapped water between bars.", "8 0 2 0 3 0 1 0 2", "7", "6 3 0 2 0 4 1", "7"),
    ("Product Except Position", "product-except-position", "Medium", "For every index, output the product of all values except the value at that index; do not use division.", "4 1 2 3 4", "24 12 8 6", "3 0 4 5", "20 0 0"),
    ("Majority Candidate", "majority-candidate", "Medium", "Return the value occurring more than half the time, or -1 if no such value exists.", "7 2 2 1 2 3 2 2", "2", "4 1 2 1 2", "-1"),
    ("Sorted Merge", "sorted-merge", "Easy", "Merge two already sorted arrays into one sorted array.", "3 1 4 7 4 2 3 8 9", "1 2 3 4 7 8 9", "2 -2 5 3 -1 0 6", "-2 -1 0 5 6"),
    ("Interval Coverage Length", "interval-coverage-length", "Medium", "Given inclusive integer intervals, return the number of covered integer points after merging overlaps.", "3 1 3 2 5 8 9", "7", "2 4 4 6", "3"),
    ("Subarray Product Limit", "subarray-product-limit", "Medium", "Count positive contiguous subarrays whose product is at most limit.", "4 10 5 2 6 5", "6", "3 3 1 2 10", "5"),
    ("Equal Parity Blocks", "equal-parity-blocks", "Easy", "Count contiguous blocks in which the number of even and odd values is equal.", "6 1 2 4 3 5 6", "3", "4 2 4 6 8", "0"),
    ("Valley Fill Height", "valley-fill-height", "Medium", "For each inner position, compute the smaller boundary maximum minus its height, summed over all positions.", "7 3 0 2 0 4 1 2", "9", "5 1 0 2 1 4", "5"),
    ("Adjacent Difference Maximum", "adjacent-difference-maximum", "Easy", "Return the largest absolute difference between neighbouring values.", "5 4 10 3 8 1", "7", "3 -5 -1 -9", "8"),
    ("Target Pair Indices", "target-pair-indices", "Easy", "Return the first pair of zero-based indices whose values add to target, or -1 -1.", "5 4 7 1 9 2 10", "0 3", "4 5 6 7 8 20", "0 2"),
    ("Triplet Target Count", "triplet-target-count", "Medium", "Count distinct index triples whose values sum to target.", "5 0 1 2 3 4 3", "2", "4 -1 0 1 2 1", "2"),
    ("Merge Alternating Halves", "merge-alternating-halves", "Easy", "Interleave the first half and second half of an even-length array.", "6 1 2 3 10 20 30", "1 10 2 20 3 30", "4 4 5 8 9", "4 8 5 9"),
    ("Missing Range Values", "missing-range-values", "Easy", "For values in 0 through n, return the missing values in ascending order.", "5 0 1 3 4 5 2", "[]", "4 0 1 3 4", "[2]"),
    ("Local Minimum Index", "local-minimum-index", "Medium", "Return any index whose value is no greater than its available neighbours, preferring the smallest index.", "6 3 2 4 1 5 6", "1", "4 1 2 3 4", "0"),
    ("Duplicate-Free Window Count", "duplicate-free-window-count", "Medium", "Count contiguous subarrays that contain no repeated value.", "4 1 2 1 3", "7", "3 5 5 5", "3"),
    ("Sign Segment Count", "sign-segment-count", "Easy", "Count maximal contiguous segments of equal sign; zero starts its own sign segment.", "7 -2 -1 0 0 4 3 -1", "4", "5 1 2 3 4 5", "1"),
    ("Kth Smallest Value", "kth-smallest-value", "Easy", "Return the k-th smallest value using one-based k.", "5 7 1 5 3 9 3", "3", "4 -2 8 0 4 2", "2"),
    ("Range Additions", "range-additions", "Medium", "Apply inclusive range additions to an initially zero array and print the final values.", "5 2 1 3 4 2 5 1 5", "0 4 4 5 1", "4 1 0 2 3", "0 0 3 3"),
    ("Circular Local Peaks", "circular-local-peaks", "Medium", "Count values greater than both circular neighbours; a length-one array has zero peaks.", "5 1 3 2 4 1 2", "2", "4 5 1 2 3 4", "1"),
    ("Stable Absolute Sort", "stable-absolute-sort", "Easy", "Sort values by absolute value while preserving original order for equal absolute values.", "6 -3 2 -2 1 3 -1", "1 -1 2 -2 -3 3", "4 -4 2 -2 1 0", "0 1 -2 2 -4"),
    ("Longest Bounded Segment", "longest-bounded-segment", "Medium", "Find the longest contiguous segment whose maximum minus minimum is at most limit.", "6 1 3 6 4 2 5 3", "4", "5 1 10 2 9 3 1", "1"),
    ("Alternating Parity Run", "alternating-parity-run", "Easy", "Find the longest contiguous run where neighbouring values have opposite parity.", "7 2 5 8 3 7 4 6", "5", "5 1 3 5 7 9", "1"),
    ("Array Wave Form", "array-wave-form", "Easy", "Rearrange values so adjacent values alternate low-high, starting with a low value.", "6 3 1 5 2 4 6", "1 3 2 5 4 6", "4 4 3 2 1", "1 4 2 3"),
    ("Circular Distance Sum", "circular-distance-sum", "Medium", "For each position, sum circular distances to every other position with the same value.", "5 1 2 1 3 1", "2 0 2 0 4", "4 7 7 8 7", "4 2 4 0"),
    ("Best Single Trade", "best-single-trade", "Easy", "Choose one earlier value to buy and a later value to sell for maximum positive gain, or return 0.", "6 7 1 5 3 6 4", "5", "5 5 4 3 2 1", "0"),
    ("Two-Color Balance", "two-color-balance", "Easy", "Find the longest prefix where counts of values marked 0 and 1 are equal.", "6 0 1 0 0 1 1", "6", "4 0 0 1 0", "0"),
    ("Subarray Sum Target Count", "subarray-sum-target-count", "Medium", "Count contiguous subarrays whose sum equals target; values may be negative.", "5 1 2 1 2 1 3", "4", "4 1 -1 1 -1 0", "4"),
    ("Maximum Circular Sum", "maximum-circular-sum", "Hard", "Return the largest sum of a non-empty contiguous circular subarray.", "5 5 -3 5 1 -2 4", "12", "4 -2 -3 -1 -5", "-1"),
    ("Matrix Diagonal Flatten", "matrix-diagonal-flatten", "Easy", "Read a square matrix stored row-wise and print its main diagonal.", "3 1 2 3 4 5 6 7 8 9", "1 5 9", "2 -1 4 7 3", "-1 3"),
    ("Row Rotation Check", "row-rotation-check", "Easy", "Determine whether the second array is a circular rotation of the first.", "5 1 2 3 4 5 4 5 1 2 3", "true", "3 1 2 3 3 1 3 2", "false"),
    ("Dominant Suffix Values", "dominant-suffix-values", "Medium", "Print values that are strictly greater than every value to their right, preserving left-to-right order.", "6 16 17 4 3 5 2", "17 5 2", "4 1 2 3 4", "4"),
    ("Index Gap Maximum", "index-gap-maximum", "Medium", "Return the maximum j-i where i is before j and values[i] is no greater than values[j].", "6 6 0 8 2 1 5 7", "5", "4 9 8 7 6 5", "0"),
    ("Three Segment Equal Sum", "three-segment-equal-sum", "Medium", "Determine whether an array can be split into three non-empty contiguous parts with equal sums.", "6 1 2 3 0 3 3 0", "true", "4 1 1 1 3", "false"),
    ("Frequency Sorted Array", "frequency-sorted-array", "Medium", "Sort by increasing frequency, then by increasing value when frequencies tie.", "7 4 4 1 2 2 2 3 3", "1 3 3 4 4 2 2 2", "5 5 1 1 2 3", "2 3 5 5 1 1"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # Parse the documented input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/);\n// Parse the documented input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        Scanner scanner = new Scanner(System.in);\n        // Parse the documented input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    category = "Arrays"
    return {
        "title": title,
        "slug": f"arrays-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": category,
        "topic": "Arrays",
        "tags": ["arrays", operation.split()[0].lower()],
        "description": (
            f"{operation} Read the values using the input format below and produce exactly the requested result. "
            "Do not change the order of values unless the statement explicitly asks for a rearrangement. "
            "Solutions should handle negative values and repeated values where the constraints permit them."
        ),
        "input_format": "The first line contains n followed by the required integer parameters and n integer values, as described by the examples.",
        "output_format": "Print the requested value or sequence on one line. Separate sequence values with single spaces.",
        "constraints": "1 <= n <= 100000; -1000000000 <= value <= 1000000000; all extra parameters are valid for the described operation.",
        "examples": [
            {"input": public_input, "output": public_output},
            {"input": hidden_input, "output": hidden_output},
        ],
        "hints": [
            "Write down the invariant that must remain true after processing each value.",
            "Consider whether a prefix, suffix, frequency map, two pointers, or a monotonic structure removes repeated work.",
        ],
        "test_cases": [
            {"input": public_input, "expected_output": public_output, "is_hidden": False, "time_limit_ms": 3000, "memory_limit_mb": 256},
            {"input": hidden_input, "expected_output": hidden_output, "is_hidden": True, "time_limit_ms": 3000, "memory_limit_mb": 256},
        ],
        "starter_code": {
            "python": starter("python"),
            "java": starter("java"),
            "cpp": starter("cpp"),
            "javascript": starter("javascript"),
        },
        "time_limit_ms": 3000,
        "memory_limit_mb": 256,
        "is_published": False,
    }


def main() -> None:
    output = {"problems": [make_problem(index, task) for index, task in enumerate(TASKS, 1)]}
    path = Path(__file__).parents[1] / "datasets" / "arrays.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(output['problems'])} problems to {path}")


if __name__ == "__main__":
    main()
