import json
from pathlib import Path


TASKS = [
    ("Factorial Value", "factorial-value", "Easy", "Return n factorial.", "5", "120", "0", "1"),
    ("Recursive Digit Sum", "recursive-digit-sum", "Easy", "Repeatedly sum decimal digits until one digit remains.", "9875", "2", "0", "0"),
    ("Power Fast", "power-fast", "Easy", "Return x raised to non-negative exponent n using recursive exponentiation.", "2|10", "1024", "5|0", "1"),
    ("Fibonacci Recursion Count", "fibonacci-recursion-count", "Easy", "Return the n-th Fibonacci value.", "8", "21", "1", "1"),
    ("Tower Of Hanoi Moves", "tower-of-hanoi-moves", "Easy", "Return the number of moves needed to transfer n disks.", "4", "15", "1", "1"),
    ("Generate Binary Strings", "generate-binary-strings", "Easy", "Print all binary strings of length n in lexicographic order.", "3", "000 001 010 011 100 101 110 111", "2", "00 01 10 11"),
    ("Generate Parentheses", "generate-parentheses", "Medium", "Print all valid parenthesis strings containing n pairs.", "3", "((())) (()()) (())() ()(()) ()()()", "1", "()"),
    ("Permutations Distinct", "permutations-distinct", "Medium", "Print all permutations of distinct values in lexicographic order.", "3 1 2 3", "1 2 3|1 3 2|2 1 3|2 3 1|3 1 2|3 2 1", "2 4 5", "4 5|5 4"),
    ("Permutations With Duplicates", "permutations-with-duplicates", "Medium", "Print unique permutations of values in lexicographic order.", "3 1 1 2", "1 1 2|1 2 1|2 1 1", "3 2 2 2", "2 2 2"),
    ("Combinations K", "combinations-k", "Medium", "Print all k-element combinations from 1 through n.", "4|2", "1 2|1 3|1 4|2 3|2 4|3 4", "3|1", "1|2|3"),
    ("Subsets Distinct", "subsets-distinct", "Medium", "Print every subset of distinct values in increasing size then lexicographic order.", "3 1 2 3", "[]|1|2|3|1 2|1 3|2 3|1 2 3", "2 4 5", "[]|4|5|4 5"),
    ("Subsets With Duplicates", "subsets-with-duplicates", "Medium", "Print unique subsets when input values may repeat.", "3 1 2 2", "[]|1|2|1 2|2 2|1 2 2", "2 3 3", "[]|3|3 3"),
    ("Combination Target Sum", "combination-target-sum", "Medium", "Print combinations of reusable candidate values that sum to target.", "3 2 3 6|7", "2 2 3", "2 2 5|4", "2 2"),
    ("Combination Unique Target", "combination-unique-target", "Medium", "Print unique combinations using each candidate at most once to reach target.", "4 10 1 2 7 6|8", "1 7|2 6", "5 2 5 2 1 2|5", "1 2 2|5"),
    ("Palindrome Partitions", "palindrome-partitions", "Medium", "Print every partition whose pieces are palindromes.", "aab", "a|a|b|aa|b", "efe", "e|f|e|efe"),
    ("Restore IP Addresses", "restore-ip-addresses", "Medium", "Insert three dots to form valid IPv4 addresses.", "25525511135", "255.255.11.135|255.255.111.35", "0000", "0.0.0.0"),
    ("Letter Phone Combinations", "letter-phone-combinations", "Medium", "Print keypad letter combinations for a digit string.", "23", "ad ae af bd be bf cd ce cf", "2", "a b c"),
    ("Word Search Grid", "word-search-grid", "Medium", "Determine whether a word can be traced through adjacent unused grid cells.", "3 4 ABCE SFCS ADEE|ABCCED", "true", "2 2 AB BA|ABA", "false"),
    ("Rat Maze Paths", "rat-maze-paths", "Medium", "Print all paths from top-left to bottom-right through one-cells, using D and R moves.", "3 3 111 110 111", "DDRDR DRDD", "2 2 10 01", ""),
    ("N Queens Count", "n-queens-count", "Hard", "Count ways to place n queens so no pair attacks.", "4", "2", "1", "1"),
    ("N Queens Boards", "n-queens-boards", "Hard", "Print all valid n-queen boards using Q and . rows.", "4", ".Q.. ...Q Q... ..Q.", "1", "Q"),
    ("Sudoku Valid Fill", "sudoku-valid-fill", "Hard", "Determine whether a partially filled 9x9 Sudoku has at least one valid completion.", "9 53..7.... 6..195... .98....6. 8...6...3 4..8.3..1 7...2...6 .6....28. ...419..5 ....8..79", "true", "9 11....... ......... ......... ......... ......... ......... ......... ......... .........", "false"),
    ("Word Break Sentences", "word-break-sentences", "Hard", "Print every dictionary-word sentence that reconstructs a string.", "catsanddog|cat cats and sand dog", "cat sand dog|cats and dog", "pineapple|pine apple", "pine apple"),
    ("Expression Operators", "expression-operators", "Hard", "Insert +, -, or * between digits to reach target and print expressions.", "123|6", "1*2*3|1+2+3", "105|5", "10-5"),
    ("Binary Watch Times", "binary-watch-times", "Medium", "Print times whose binary watch has exactly turned-on count LEDs.", "1", "0:01 0:02 0:04 0:08 0:16 0:32 1:00 2:00 4:00 8:00", "0", "0:00"),
    ("Gray Code Sequence", "gray-code-sequence", "Medium", "Generate a cyclic n-bit Gray code sequence.", "2", "0 1 3 2", "1", "0 1"),
    ("Kth Permutation", "kth-permutation", "Medium", "Return the k-th lexicographic permutation of values 1 through n.", "3|4", "231", "4|1", "1234"),
    ("Unique Paths With Blocks", "unique-paths-with-blocks", "Medium", "Count paths through a blocked grid using recursive memoization.", "3 3 000 010 000", "2", "2 2 00 01", "0"),
    ("Partition Into K Equal Groups", "partition-into-k-equal-groups", "Hard", "Determine whether values can be partitioned into k groups with equal sums.", "5 4 3 2 3 5|4", "true", "4 1 2 3 4|3", "false"),
    ("Crossword Placement", "crossword-placement", "Hard", "Determine whether every supplied word can be placed in open horizontal or vertical slots.", "3 3 ... .#. ...|cat dog", "true", "2 2 ## ##|a", "false"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # Parse the documented recursion/backtracking input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/);\n// Parse the documented recursion/backtracking input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        Scanner scanner = new Scanner(System.in);\n        // Parse the documented recursion/backtracking input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented recursion/backtracking input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    return {
        "title": title,
        "slug": f"recursion-backtracking-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": "Recursion and Backtracking",
        "topic": "Recursion and Backtracking",
        "tags": ["recursion", "backtracking" if "count" not in slug and "value" not in slug else "recursion"],
        "description": (
            f"{operation} Inputs use the pipe-separated notation shown in examples for separate parameters. "
            "When multiple answers exist, print them in the stated deterministic order."
        ),
        "input_format": "The input is a whitespace- or pipe-separated record; the examples show the exact parameter order.",
        "output_format": "Print the requested value or each generated answer using the stated separators.",
        "constraints": "1 <= n and input length <= 15 for exhaustive generation; grid dimensions are at most 12 by 12.",
        "examples": [{"input": public_input, "output": public_output}, {"input": hidden_input, "output": hidden_output}],
        "hints": [
            "Choose a base case that represents one complete answer and undo each choice before returning.",
            "Prune a branch as soon as its partial state cannot satisfy the remaining constraints.",
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
    path = Path(__file__).parents[1] / "datasets" / "recursion_backtracking.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"problems": [make_problem(i, task) for i, task in enumerate(TASKS, 1)]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(TASKS)} problems to {path}")


if __name__ == "__main__":
    main()
