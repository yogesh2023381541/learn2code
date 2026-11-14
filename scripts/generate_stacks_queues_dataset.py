import json
from pathlib import Path


TASKS = [
    ("Bracket Validator", "bracket-validator", "Easy", "Check whether brackets are properly nested.", "([]{})", "true", "([)]", "false"),
    ("Stack Minimum", "stack-minimum", "Easy", "Return the smallest value in a stack after all listed pushes.", "5 4 2 9 -1 6", "-1", "3 7 8 9", "7"),
    ("Stack Maximum", "stack-maximum", "Easy", "Return the largest value in a stack.", "4 -3 8 1 5", "8", "2 -9 -4", "-4"),
    ("Queue Front", "queue-front", "Easy", "Return the front value after enqueueing the listed values.", "4 8 1 6 3", "8", "1 42", "42"),
    ("Queue Reversal", "queue-reversal", "Easy", "Reverse the order of every value in a queue.", "5 1 2 3 4 5", "5 4 3 2 1", "3 9 0 -2", "-2 0 9"),
    ("Evaluate Postfix", "evaluate-postfix", "Medium", "Evaluate a space-separated postfix expression using integer arithmetic.", "5 2 3 + 4 *", "20", "7 2 / 3 +", "6"),
    ("Infix To Postfix", "infix-to-postfix", "Medium", "Convert an expression with +, -, *, /, and parentheses to postfix tokens.", "a+b*c", "a b c * +", "(a+b)*c", "a b + c *"),
    ("Next Greater Stream", "next-greater-stream", "Medium", "For each value, print the first greater value to its right, or -1.", "5 2 1 4 3 5", "4 4 5 5 -1", "4 9 8 7 6", "-1 -1 -1 -1"),
    ("Stock Span", "stock-span", "Medium", "For each price, return the number of consecutive earlier prices no greater than it, including today.", "7 100 80 60 70 60 75 85", "1 1 1 2 1 4 6", "4 10 20 30 40", "1 2 3 4"),
    ("Largest Histogram Rectangle", "largest-histogram-rectangle", "Hard", "Return the largest rectangle area under a histogram.", "6 2 1 5 6 2 3", "10", "4 2 4 2 4", "8"),
    ("Sliding Window Maximum", "sliding-window-maximum", "Hard", "Print the maximum of every contiguous window of width k.", "8 3 1 3 -1 -3 5 3 6 7|3", "3 3 5 5 6 7", "4 2 4 1 0|2", "4 4 1"),
    ("Sliding Window Minimum", "sliding-window-minimum", "Hard", "Print the minimum of every contiguous window of width k.", "6 2 1 5 3 4 0|3", "1 1 3 0", "4 8 7 9 6|2", "7 7 6"),
    ("Queue Using Two Stacks", "queue-using-two-stacks", "Easy", "Process enqueue and dequeue commands and print each dequeued value.", "5 E1 E2 D E3 D", "1 2", "4 E9 D D D", "9 -1 -1"),
    ("Stack Using Two Queues", "stack-using-two-queues", "Easy", "Process push and pop commands and print each popped value.", "5 P1 P2 O P3 O", "2 3", "3 O P7 O", "-1 7"),
    ("Min-Stack Operations", "min-stack-operations", "Medium", "Process push, pop, and minimum commands; print each requested minimum.", "6 P5 P2 M O M P1 M", "2 5 1", "4 P9 O M O", "-1"),
    ("Circular Queue Simulation", "circular-queue-simulation", "Medium", "Simulate a fixed-capacity circular queue and print dequeue results.", "3 E1 E2 D E3 E4 D D", "1 2 3", "2 E7 E8 E9 D D", "7 8"),
    ("Recent Request Counter", "recent-request-counter", "Easy", "For each timestamp, count timestamps in the last window inclusive.", "5 1 2 3 10 11|3", "1 2 3 1 2", "4 100 101 105 106|5", "1 2 2 2"),
    ("Asteroid Collision", "asteroid-collision", "Medium", "Positive values move right and negative values move left; resolve collisions and print survivors.", "3 5 10 -5", "5 10", "4 8 -8 2 -3", "-3"),
    ("Remove Adjacent Digits", "remove-adjacent-digits", "Medium", "Remove adjacent equal digits repeatedly and print the remaining digit text.", "abbaca", "ca", "azxxzy", "ay"),
    ("Decode Repetition", "decode-repetition", "Medium", "Decode nested k[segment] notation where k is a positive integer.", "3[a2[c]]", "accaccacc", "2[ab3[c]]", "abcccabccc"),
    ("Train Platform Order", "train-platform-order", "Medium", "Check whether a target departure order can be produced using one stack siding.", "1 2 3 4 5|5 4 3 2 1", "true", "1 2 3 4|2 1 4 3", "true"),
    ("Daily Temperature Wait", "daily-temperature-wait", "Medium", "For each temperature, report days until a warmer temperature, or 0.", "8 73 74 75 71 69 72 76 73", "1 1 4 2 1 1 0 0", "4 30 20 10 5", "0 0 0 0"),
    ("Expression Parenthesis Score", "expression-parenthesis-score", "Medium", "Score balanced parentheses: () is 1, concatenation adds, and nesting doubles.", "()(()())", "5", "((()))", "4"),
    ("Queue Interleave Halves", "queue-interleave-halves", "Easy", "Interleave the first and second halves of an even-sized queue.", "6 1 2 3 4 5 6", "1 4 2 5 3 6", "4 8 7 6 5", "8 6 7 5"),
    ("First Nonrepeating Stream", "first-nonrepeating-stream", "Medium", "After each arriving lowercase character, print the first character seen once, or #.", "a a b c", "a # b b", "a b a c", "a a b b"),
    ("Undo Redo History", "undo-redo-history", "Medium", "Process edit, undo, and redo commands and print the final text.", "E:a E:b U R E:c", "abc", "E:x E:y U U R", "x"),
    ("K-th Queue Person", "k-th-queue-person", "Easy", "Return the value at one-based queue position k without changing the queue.", "5 4 8 1 9 2|3", "1", "2 7 6|1", "7"),
    ("Task Round Robin", "task-round-robin", "Medium", "Process positive task durations with one unit per turn and print completion order.", "3 2 1 3", "2 1 3", "2 4 2", "1 2"),
    ("Multi-Level Queue Merge", "multi-level-queue-merge", "Hard", "Merge queues by taking one item from each non-empty queue in repeated rounds.", "2 1 2 3|3 4 5 6", "1 4 2 5 3 6", "3 a b c|1 x", "a x b c"),
    ("Queue Median Snapshot", "queue-median-snapshot", "Hard", "After each enqueue, print the lower median of all values currently in the queue.", "5 5 1 9 2 7", "5 1 5 2 5", "3 4 6 8", "4 4 6"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # Parse the documented stack/queue input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/);\n// Parse the documented stack/queue input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        Scanner scanner = new Scanner(System.in);\n        // Parse the documented stack/queue input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented stack/queue input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    return {
        "title": title,
        "slug": f"stacks-queues-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": "Stacks and Queues",
        "topic": "Stacks and Queues",
        "tags": ["stack" if "stack" in slug or "bracket" in slug else "queue", slug.split("-")[0]],
        "description": (
            f"{operation} Commands and multiple logical values use the notation shown in the examples. "
            "Preserve the order required by the data structure and print only requested results."
        ),
        "input_format": "The input is a whitespace-separated record; the examples show command, parameter, and value boundaries.",
        "output_format": "Print the requested value or sequence on one line, using single spaces between sequence items.",
        "constraints": "1 <= number of operations or values <= 100000; integer values fit in signed 32-bit range.",
        "examples": [{"input": public_input, "output": public_output}, {"input": hidden_input, "output": hidden_output}],
        "hints": [
            "A monotonic stack can answer nearest-greater or nearest-smaller questions in one pass.",
            "For a queue, separate the arrival order from the order in which removals are observed.",
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
    path = Path(__file__).parents[1] / "datasets" / "stacks_queues.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"problems": [make_problem(i, task) for i, task in enumerate(TASKS, 1)]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(TASKS)} problems to {path}")


if __name__ == "__main__":
    main()
