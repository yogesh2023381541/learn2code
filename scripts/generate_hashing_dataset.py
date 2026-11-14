import json
from pathlib import Path


TASKS = [
    ("Pair Sum Count", "pair-sum-count", "Easy", "Count index pairs whose values sum to target.", "5 1 5 7 -1 5|6", "2", "4 2 2 2 2|4", "6"),
    ("Pair Sum Indices", "pair-sum-indices", "Easy", "Return the first pair of indices whose values sum to target, or -1 -1.", "5 2 7 11 15 1|9", "0 1", "3 1 2 3|10", "-1 -1"),
    ("First Repeated Value", "first-repeated-value", "Easy", "Return the first value encountered whose second occurrence appears earliest.", "6 5 1 3 5 2 3", "5", "4 1 2 3 4", "-1"),
    ("Unique Value", "unique-value", "Easy", "Return the value occurring once when every other value occurs twice.", "5 4 1 2 1 2", "4", "3 9 9 8", "8"),
    ("Frequency Table", "frequency-table", "Easy", "Print each distinct value and its frequency ordered by value.", "6 3 1 3 2 1 3", "1:2 2:1 3:3", "4 5 5 4 5", "4:1 5:2"),
    ("Majority Vote", "majority-vote", "Easy", "Return the value appearing more than half the time, or -1.", "7 2 2 1 2 3 2 2", "2", "4 1 2 1 2", "-1"),
    ("Anagram Groups", "anagram-groups", "Medium", "Group words by anagram signature and print group sizes descending.", "5 eat tea tan ate nat", "3 2", "3 abc cab xyz", "2 1"),
    ("Longest Consecutive Set", "longest-consecutive-set", "Medium", "Return the length of the longest run of consecutive integer values.", "6 100 4 200 1 3 2", "4", "5 9 1 4 7 3", "2"),
    ("Subarray Sum Zero", "subarray-sum-zero", "Medium", "Determine whether any non-empty contiguous subarray sums to zero.", "5 4 2 -3 1 6", "true", "3 1 2 3", "false"),
    ("Subarray Sum Count", "subarray-sum-count", "Medium", "Count contiguous subarrays whose sum equals target.", "5 1 2 1 2 1|3", "4", "4 1 -1 1 -1|0", "6"),
    ("Longest Zero Sum Range", "longest-zero-sum-range", "Medium", "Return the length of the longest contiguous subarray with sum zero.", "6 15 -2 2 -8 1 7 10", "5", "4 1 2 3 4", "0"),
    ("Longest Equal Zero One", "longest-equal-zero-one", "Medium", "Return the longest subarray containing equal counts of 0 and 1.", "7 0 1 0 0 1 1 0", "6", "4 0 0 0 1", "2"),
    ("Duplicate Within Distance", "duplicate-within-distance", "Easy", "Determine whether equal values occur within k indices.", "5 1 2 3 1 4|3", "true", "4 1 2 3 1|2", "false"),
    ("Nearby Almost Duplicate", "nearby-almost-duplicate", "Hard", "Determine whether two values within k indices differ by at most t.", "5 1 5 9 1 5|2|3", "true", "4 1 5 9 1|2|2", "false"),
    ("Isomorphic Mapping", "isomorphic-mapping", "Easy", "Check whether two strings have a consistent one-to-one character mapping.", "egg add", "true", "foo bar", "false"),
    ("Word Pattern", "word-pattern", "Easy", "Check whether pattern symbols map one-to-one to sentence words.", "abba|dog cat cat dog", "true", "abba|dog cat cat fish", "false"),
    ("Ransom Construction", "ransom-construction", "Easy", "Determine whether a note can be formed from magazine characters without reuse.", "aa|aab", "true", "aa|ab", "false"),
    ("Common Characters", "common-characters", "Medium", "Print characters shared by every word, including multiplicity.", "3 bella label roller", "e l l", "2 cool lock", "c o"),
    ("Longest Palindrome Build", "longest-palindrome-build", "Easy", "Return the longest palindrome length constructible from character counts.", "abccccdd", "7", "a", "1"),
    ("Happy Number", "happy-number", "Easy", "Determine whether repeatedly replacing a number by squared-digit sum reaches 1.", "19", "true", "2", "false"),
    ("Fraction To Decimal", "fraction-to-decimal", "Medium", "Convert numerator divided by denominator and wrap repeating digits in parentheses.", "1|3", "0.(3)", "4|2", "2"),
    ("Pattern Repetition", "pattern-repetition", "Medium", "Return whether a string can be formed by repeating a shorter block.", "abab", "true", "aba", "false"),
    ("Four Sum Count", "four-sum-count", "Medium", "Count quadruples, one value from each array, whose sum is zero.", "2 1 2|2 -2 -1|2 -1 2|2 0 2", "2", "1 0|1 0|1 0|1 1", "0"),
    ("Triplet Zero Count", "triplet-zero-count", "Medium", "Count distinct value triples that sum to zero.", "6 -1 0 1 2 -1 -4", "2", "4 1 2 3 4", "0"),
    ("Subarray Divisible Count", "subarray-divisible-count", "Medium", "Count subarrays whose sum is divisible by k.", "6 4 5 0 -2 -3 1|5", "7", "3 1 2 3|2", "2"),
    ("Longest Arithmetic Span", "longest-arithmetic-span", "Hard", "Return the length of the longest arithmetic subsequence.", "6 3 6 9 12 15 20", "5", "4 1 3 5 8", "3"),
    ("Equal Difference Pairs", "equal-difference-pairs", "Easy", "Count pairs of values with absolute difference k.", "5 1 5 3 4 2|2", "3", "4 1 1 1 1|0", "6"),
    ("Distinct Window Counts", "distinct-window-counts", "Medium", "Print the number of distinct values in each window of width k.", "7 1 2 1 3 4 2 3|4", "3 4 4 4", "4 5 5 5 5|2", "1 1 1"),
    ("Top Frequent Values", "top-frequent-values", "Medium", "Print k most frequent values, breaking ties by smaller value.", "6 1 1 1 2 2 3|2", "1 2", "5 4 4 5 5 6|1", "5"),
    ("Cache Simulation", "cache-simulation", "Medium", "Simulate an LRU cache and count cache misses for an access stream.", "3 1 2 1 3 4 1|2", "5", "2 a b a b c|2", "3"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # Parse the documented hashing input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/);\n// Parse the documented hashing input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        Scanner scanner = new Scanner(System.in);\n        // Parse the documented hashing input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented hashing input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    return {
        "title": title,
        "slug": f"hashing-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": "Hashing",
        "topic": "Hashing",
        "tags": ["hashing", slug.split("-")[0]],
        "description": (
            f"{operation} Inputs use the pipe-separated notation shown in examples for separate parameters. "
            "Preserve the requested tie-breaking and output order exactly."
        ),
        "input_format": "The input is a whitespace- or pipe-separated record; the examples show the exact parameter order.",
        "output_format": "Print the requested count, boolean, value, or sequence on one line.",
        "constraints": "1 <= n and string length <= 200000; values fit signed 32-bit integers; k is valid when supplied.",
        "examples": [{"input": public_input, "output": public_output}, {"input": hidden_input, "output": hidden_output}],
        "hints": [
            "Store the information needed for a future lookup rather than comparing every pair.",
            "For contiguous ranges, prefix information plus a frequency map often turns a quadratic scan into one pass.",
        ],
        "test_cases": [
            {"input": public_input, "expected_output": public_output, "is_hidden": False, "time_limit_ms": 3000, "memory_limit_mb": 256},
            {"input": hidden_input, "expected_output": hidden_output, "is_hidden": True, "time_limit_ms": 3000, "memory_limit_mb": 256},
        ],
        "starter_code": {language: starter(language) for language in ("python", "java", "cpp", "javascript")},
        "time_limit_ms": 3000,
        "memory_limit_mb": 256,
        "is_published": True,
    }


def main() -> None:
    path = Path(__file__).parents[1] / "datasets" / "hashing.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"problems": [make_problem(i, task) for i, task in enumerate(TASKS, 1)]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(TASKS)} problems to {path}")


if __name__ == "__main__":
    main()
