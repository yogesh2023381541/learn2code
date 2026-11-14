import json
from pathlib import Path


TASKS = [
    ("Climb Steps", "climb-steps", "Easy", "Count ways to reach step n using jumps of one or two.", "5", "8", "1", "1"),
    ("Minimum Climb Cost", "minimum-climb-cost", "Easy", "Return the minimum cost to pass the top when each step has a landing cost.", "3 10 15 20", "15", "4 1 100 1 1", "2"),
    ("House Robber", "house-robber", "Medium", "Choose non-adjacent house values for the largest total.", "5 2 7 9 3 1", "11", "4 2 1 1 2", "4"),
    ("Circular House Robber", "circular-house-robber", "Medium", "Choose non-adjacent values on a circle for the largest total.", "4 2 3 2 5", "5", "3 1 2 3", "3"),
    ("Fibonacci Modulo", "fibonacci-modulo", "Easy", "Return the n-th Fibonacci number modulo m.", "10|1000", "55", "20|7", "5"),
    ("Tribonacci Steps", "tribonacci-steps", "Easy", "Return T(n), where T(0)=0, T(1)=1, T(2)=1, modulo m.", "5|1000", "7", "7|100", "44"),
    ("Decode Digit Text", "decode-digit-text", "Medium", "Count decodings of a digit string where 1-26 map to letters.", "226", "3", "06", "0"),
    ("Word Break Count", "word-break-count", "Medium", "Count ways to split a string into dictionary words.", "catsanddog|cat cats and sand dog", "2", "apple|app", "0"),
    ("Longest Increasing Subsequence", "longest-increasing-subsequence", "Medium", "Return the length of a longest strictly increasing subsequence.", "8 10 9 2 5 3 7 101 18", "4", "5 5 4 3 2 1", "1"),
    ("Number Of LIS", "number-of-lis", "Hard", "Count longest increasing subsequences.", "5 1 3 5 4 7", "2", "4 2 2 2 2", "4"),
    ("Longest Bitonic Subsequence", "longest-bitonic-subsequence", "Medium", "Return the longest subsequence that first rises then falls.", "8 1 4 2 3 5 2 1 0", "6", "5 1 2 3 4 5", "5"),
    ("Longest Common Subsequence", "longest-common-subsequence", "Medium", "Return the length of a longest subsequence shared by two strings.", "abcde|ace", "3", "abc|def", "0"),
    ("Longest Common Substring", "longest-common-substring", "Medium", "Return the length of the longest contiguous substring shared by two strings.", "ababc|babca", "4", "xyz|abc", "0"),
    ("Edit Distance", "edit-distance", "Medium", "Return minimum insertions, deletions, and replacements to transform one word into another.", "horse|ros", "3", "intention|execution", "5"),
    ("Delete For Equal", "delete-for-equal", "Medium", "Return minimum deletions from two strings to make them equal.", "sea|eat", "2", "abc|abc", "0"),
    ("Distinct Subsequences", "distinct-subsequences", "Hard", "Count subsequences of source equal to target.", "rabbbit|rabbit", "3", "babgbag|bag", "5"),
    ("Wildcard Pattern DP", "wildcard-pattern-dp", "Medium", "Match text against ? and * using dynamic programming.", "adceb|*a*b", "true", "cb|?a", "false"),
    ("Regex Dot Star", "regex-dot-star", "Hard", "Match text against a pattern where . is any character and * repeats the previous token.", "aab|c*a*b", "true", "mississippi|mis*is*p*.", "false"),
    ("Partition Equal Sum", "partition-equal-sum", "Medium", "Determine whether values can be split into two subsets with equal sum.", "4 1 5 11 5", "true", "4 1 2 3 5", "false"),
    ("Target Sum Signs", "target-sum-signs", "Medium", "Count plus/minus assignments reaching target.", "5 1 1 1 1 1|3", "5", "3 1 2 3|1", "2"),
    ("Subset Sum Decision", "subset-sum-decision", "Medium", "Determine whether some subset sums to target.", "4 3 34 4 12|9", "true", "3 2 4 6|5", "false"),
    ("Count Subset Sum", "count-subset-sum", "Medium", "Count subsets whose values sum to target.", "4 1 2 3 3|6", "3", "3 2 2 2|3", "0"),
    ("Zero One Knapsack", "zero-one-knapsack", "Medium", "Maximize value under a weight capacity, using each item at most once.", "3 2:3 3:4 4:5|5", "7", "2 4:10 5:11|3", "0"),
    ("Unbounded Knapsack", "unbounded-knapsack", "Medium", "Maximize value when each item may be selected repeatedly.", "2 2:3 3:4|7", "10", "1 5:8|4", "0"),
    ("Coin Change Minimum", "coin-change-minimum", "Medium", "Return the fewest coins needed to make amount, or -1.", "3 1 2 5|11", "3", "2 2 4|3", "-1"),
    ("Coin Change Ways", "coin-change-ways", "Medium", "Count combinations of unlimited coins that make amount.", "3 1 2 5|5", "4", "2 2 4|3", "0"),
    ("Rod Cutting", "rod-cutting", "Medium", "Maximize revenue by cutting a rod with prices for lengths 1 through n.", "4 2 5 7 8", "10", "3 1 5 8", "8"),
    ("Minimum Cost Tickets", "minimum-cost-tickets", "Medium", "Buy one, seven, or thirty-day passes for minimum travel cost.", "4 1 4 6 7|2 7 15", "11", "3 1 2 3|2 5 9", "6"),
    ("Grid Unique Paths", "grid-unique-paths", "Easy", "Count right/down paths through an empty m by n grid.", "3|7", "28", "1|5", "1"),
    ("Grid Obstacles Paths", "grid-obstacles-paths", "Medium", "Count right/down paths avoiding blocked cells.", "3 3 000 010 000", "2", "2 2 10 01", "0"),
    ("Grid Minimum Path", "grid-minimum-path", "Medium", "Return the minimum top-left to bottom-right path sum.", "3 3 1 3 1 1 5 1 4 2 1", "7", "2 2 1 2 3 4", "7"),
    ("Triangle Minimum Path", "triangle-minimum-path", "Medium", "Return the minimum sum from triangle top to bottom using adjacent children.", "4 2 3 4 6 5 7 4 1 8 3", "11", "2 1 2 3", "4"),
    ("Dungeon Health", "dungeon-health", "Hard", "Return minimum starting health needed to cross a grid while never reaching zero.", "3 3 -2 -3 3 -5 -10 1 10 30 -5", "7", "1 1 -5", "6"),
    ("Cherry Collection", "cherry-collection", "Hard", "Two synchronized travelers collect maximum values moving down or diagonally in a grid.", "3 3 3 1 1 2 5 1 5 5 5", "24", "2 2 1 1 1 1", "4"),
    ("Maximal Square", "maximal-square", "Medium", "Return the area of the largest all-one square in a binary grid.", "4 5 10100 10111 11111 10010", "4", "2 2 00 01", "1"),
    ("Largest One Rectangle", "largest-one-rectangle", "Hard", "Return the area of the largest all-one rectangle in a binary grid.", "2 5 10101 11111", "5", "1 4 1111", "4"),
    ("Stock One Trade", "stock-one-trade", "Easy", "Maximize profit from one buy followed by one sell.", "6 7 1 5 3 6 4", "5", "5 5 4 3 2 1", "0"),
    ("Stock Unlimited Trades", "stock-unlimited-trades", "Medium", "Maximize profit with unlimited non-overlapping buy/sell trades.", "6 7 1 5 3 6 4", "7", "5 5 4 3 2 1", "0"),
    ("Stock Cooldown", "stock-cooldown", "Medium", "Maximize trading profit when selling forces one cooldown day.", "5 1 2 3 0 2", "3", "3 2 1 0", "0"),
    ("Stock Transaction Fee", "stock-transaction-fee", "Medium", "Maximize unlimited trading profit with a fee per sale.", "6 1 3 2 8 4 9|2", "8", "4 1 3 7 5|3", "3"),
    ("Burst Balloons", "burst-balloons", "Hard", "Maximize coins from removing balloons in an optimal order.", "4 3 1 5 8", "167", "3 1 5 3", "35"),
    ("Matrix Chain Cost", "matrix-chain-cost", "Hard", "Return the minimum scalar multiplications needed to multiply a matrix chain.", "4 10 30 5 60", "4500", "3 10 20 30", "6000"),
    ("Boolean Parenthesization", "boolean-parenthesization", "Hard", "Count parenthesizations of T/F operands and &|^ operators that evaluate true.", "5 T|F&T^T|F", "5", "3 T^F|T", "2"),
    ("Palindrome Partition Cuts", "palindrome-partition-cuts", "Hard", "Return minimum cuts needed to partition a string into palindromes.", "aab", "1", "racecar", "0"),
    ("Word Wrap Cost", "word-wrap-cost", "Medium", "Place words within width and minimize squared unused spaces on non-final lines.", "4 3 2 2 5|6", "10", "3 2 2 2|4", "4"),
    ("Egg Drop Moves", "egg-drop-moves", "Hard", "Return minimum trials in the worst case to test floors with eggs.", "2|10", "4", "3|14", "4"),
    ("Burst Sequence Count", "burst-sequence-count", "Medium", "Count ways to parenthesize a sequence of n operations, modulo m.", "5|1000000007", "14", "4|1000", "5"),
    ("Minimum Palindrome Insertions", "minimum-palindrome-insertions", "Medium", "Return minimum insertions needed to make a string a palindrome.", "mbadm", "2", "race", "3"),
    ("Longest Palindromic Subsequence", "longest-palindromic-subsequence", "Medium", "Return the length of a longest palindromic subsequence.", "bbbab", "4", "cbbd", "2"),
    ("Interleaving Strings", "interleaving-strings", "Hard", "Determine whether a target is an order-preserving interleaving of two strings.", "aabcc|dbbca|aadbbcbcac", "true", "aabcc|dbbca|aadbbbaccc", "false"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # Parse the documented dynamic-programming input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/);\n// Parse the documented dynamic-programming input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        Scanner scanner = new Scanner(System.in);\n        // Parse the documented dynamic-programming input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented dynamic-programming input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    return {
        "title": title,
        "slug": f"dynamic-programming-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": "Dynamic Programming",
        "topic": "Dynamic Programming",
        "tags": ["dynamic-programming", slug.split("-")[0]],
        "description": (
            f"{operation} Inputs use the pipe-separated notation shown in examples for separate parameters. "
            "Return the exact count, cost, length, or boolean requested by the statement."
        ),
        "input_format": "The input is a whitespace- or pipe-separated record; the examples show the exact parameter order.",
        "output_format": "Print the requested integer, boolean, or sequence on one line.",
        "constraints": "1 <= n and string length <= 100000; values fit signed 32-bit integers; modulo is used where specified.",
        "examples": [{"input": public_input, "output": public_output}, {"input": hidden_input, "output": hidden_output}],
        "hints": [
            "Define the smallest subproblem and the information needed to extend it.",
            "Look for overlapping states and decide whether a rolling array can reduce memory.",
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
    path = Path(__file__).parents[1] / "datasets" / "dynamic_programming.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"problems": [make_problem(i, task) for i, task in enumerate(TASKS, 1)]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(TASKS)} problems to {path}")


if __name__ == "__main__":
    main()
