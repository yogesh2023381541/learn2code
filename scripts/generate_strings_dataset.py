import json
from pathlib import Path


TASKS = [
    ("Vowel Census", "vowel-census", "Easy", "Count English vowels in a string, ignoring letter case.", "Education", "5", "rhythm", "0"),
    ("Reverse Word Order", "reverse-word-order", "Easy", "Print the words in reverse order while preserving each word's spelling.", "learn code daily", "daily code learn", "one two three", "three two one"),
    ("Run-Length Encoding", "run-length-encoding", "Easy", "Compress each consecutive run as its character followed by its count.", "aaabbc", "a3b2c1", "xyzzzz", "x1y1z4"),
    ("Run-Length Expansion", "run-length-expansion", "Easy", "Expand a string made of letter-count pairs into its original repeated form.", "a3b2c1", "aaabbc", "x1y1z4", "xyzzzz"),
    ("First Unique Character", "first-unique-character", "Easy", "Return the zero-based index of the first character occurring once, or -1.", "swiss", "1", "aabbcc", "-1"),
    ("Anagram Signature", "anagram-signature", "Easy", "Print the lowercase letters sorted alphabetically to form a comparison signature.", "Listen", "eilnst", "binary", "abinry"),
    ("Anagram Decision", "anagram-decision", "Easy", "Determine whether two strings contain the same characters with the same frequencies.", "secure rescue", "true", "stone notes", "false"),
    ("Palindrome Sentence", "palindrome-sentence", "Easy", "Check whether letters and digits read the same in both directions, ignoring case and punctuation.", "A man, a plan", "false", "Never odd or even", "true"),
    ("Longest Token", "longest-token", "Easy", "Print the longest whitespace-separated token; choose the earliest on ties.", "write clean code", "write", "red blue green", "green"),
    ("Word Frequency", "word-frequency", "Easy", "Count case-insensitive occurrences of a target word in a sentence.", "Code code makes progress|code", "2", "A tiny test|large", "0"),
    ("Remove Adjacent Pairs", "remove-adjacent-pairs", "Medium", "Repeatedly delete equal adjacent character pairs until no such pair remains.", "abbaca", "ca", "azxxzy", "ay"),
    ("Balanced Bracket Text", "balanced-bracket-text", "Easy", "Check whether (), [], and {} are correctly nested while ignoring other characters.", "a[(b)]", "true", "([)]", "false"),
    ("Common Prefix", "common-prefix", "Easy", "Return the longest prefix shared by every pipe-separated word.", "flower|flow|flight", "fl", "dog|racecar|car", ""),
    ("Common Suffix", "common-suffix", "Easy", "Return the longest suffix shared by every pipe-separated word.", "running|jogging|walking", "ing", "cat|bat|car", ""),
    ("Character Class Count", "character-class-count", "Easy", "Print counts of lowercase letters, uppercase letters, digits, and other characters.", "Ab3!", "1 1 1 1", "Hello 42", "4 0 2 1"),
    ("Lexicographic Rotation", "lexicographic-rotation", "Medium", "Print the lexicographically smallest circular rotation of a string.", "baca", "abac", "aaaa", "aaaa"),
    ("Reverse Vowels", "reverse-vowels", "Easy", "Reverse only vowels while leaving every consonant and position otherwise unchanged.", "education", "oducatein", "hello", "holle"),
    ("Isomorphic Words", "isomorphic-words", "Medium", "Check whether a one-to-one character mapping transforms the first word into the second.", "egg add", "true", "foo bar", "false"),
    ("Edit Distance One", "edit-distance-one", "Medium", "Determine whether two strings differ by at most one insertion, deletion, or replacement.", "pale ple", "true", "abc axcde", "false"),
    ("Smallest Cover Window", "smallest-cover-window", "Hard", "Find the shortest substring containing every character of a target with required multiplicity.", "ADOBECODEBANC|ABC", "BANC", "a|aa", ""),
    ("Subsequence Decision", "subsequence-decision", "Easy", "Check whether the first string appears as a subsequence of the second.", "ace|abcde", "true", "aec|abcde", "false"),
    ("Interleaving Decision", "interleaving-decision", "Medium", "Check whether a third string preserves the internal order of two source strings while interleaving them.", "ab|cd|acbd", "true", "ab|cd|adbc", "false"),
    ("Longest Palindromic Slice", "longest-palindromic-slice", "Medium", "Return the longest palindromic substring; choose the earliest one on equal lengths.", "babad", "bab", "cbbd", "bb"),
    ("Count Palindromic Slices", "count-palindromic-slices", "Medium", "Count all non-empty substrings that are palindromes.", "aaa", "6", "abc", "3"),
    ("Distinct Substring Count", "distinct-substring-count", "Medium", "Count distinct non-empty substrings of a string.", "ababa", "9", "aaaa", "4"),
    ("Longest Repeated-Free Slice", "longest-repeated-free-slice", "Medium", "Return the length of the longest substring with no repeated character.", "abcabcbb", "3", "bbbbb", "1"),
    ("At-Most-K Distinct Slice", "at-most-k-distinct-slice", "Medium", "Return the longest substring containing at most k distinct characters.", "eceba|2", "3", "aa|1", "2"),
    ("Letter Inventory Difference", "letter-inventory-difference", "Easy", "Print characters whose count is larger in the first string than the second, alphabetically with counts.", "banana|band", "a1", "abc|xyz", "abc1"),
    ("Pattern Word Match", "pattern-word-match", "Medium", "Check whether a pattern's symbols map one-to-one to the words in a sentence.", "abba|dog cat cat dog", "true", "abba|dog cat cat fish", "false"),
    ("URL-safe Normalizer", "url-safe-normalizer", "Easy", "Lowercase text, replace every run of non-letters or digits with one hyphen, and trim hyphens.", "Hello, New World!", "hello-new-world", "  C++ / Java  ", "c-java"),
    ("Reverse Each Token", "reverse-each-token", "Easy", "Reverse characters inside each whitespace-separated token without changing token order.", "learn fast now", "nrael tsaf won", "one", "eno"),
    ("Minimal Delete Palindrome", "minimal-delete-palindrome", "Medium", "Return the minimum number of character deletions needed to make a string a palindrome.", "aebcbda", "2", "racecar", "0"),
    ("Longest Balanced Binary Text", "longest-balanced-binary-text", "Medium", "Return the longest substring containing equal numbers of 0 and 1.", "00110", "4", "1111", "0"),
    ("Binary Text Addition", "binary-text-addition", "Easy", "Add two non-negative binary strings and print the binary result without leading zeroes.", "1011|110", "10001", "0|0", "0"),
    ("Base-36 Digit Sum", "base-36-digit-sum", "Easy", "Sum the values of lowercase base-36 digits, where a-z represent 10-35.", "az09", "70", "hello", "62"),
    ("Roman Token Value", "roman-token-value", "Easy", "Convert a valid Roman numeral token using subtractive notation into its integer value.", "MCM", "1900", "XLII", "42"),
    ("Zigzag Text Rows", "zigzag-text-rows", "Medium", "Write characters across the requested zigzag row count and read rows from top to bottom.", "PAYPALISHIRING|3", "PAHNAPLSIIGYIR", "HELLO|4", "HOELL"),
    ("String Rotation Offset", "string-rotation-offset", "Easy", "Return the left rotation offset that changes the first string into the second, or -1.", "waterbottle|erbottlewat", "3", "abc|acb", "-1"),
    ("Longest Common Subsequence Length", "longest-common-subsequence-length", "Medium", "Return the length of a longest subsequence shared by two strings.", "abcde|ace", "3", "abc|def", "0"),
    ("Shortest Common Supersequence Length", "shortest-common-supersequence-length", "Hard", "Return the shortest length of a string containing both inputs as subsequences.", "abac|cab", "5", "geek|eke", "5"),
    ("Wildcard Text Match", "wildcard-text-match", "Medium", "Match text against a pattern where ? matches one character and * matches any sequence.", "adceb|*a*b", "true", "cb|?a", "false"),
    ("Prefix Function Border", "prefix-function-border", "Medium", "Return the length of the longest proper prefix that is also a suffix.", "ababa", "3", "abcd", "0"),
    ("Repeated Pattern Root", "repeated-pattern-root", "Easy", "Check whether a string can be built by repeating one shorter non-empty pattern.", "abab", "true", "aba", "false"),
    ("Text Justification Width", "text-justification-width", "Medium", "Pack pipe-separated words into lines of exactly width characters, left-aligning the final line.", "This|is|a|test|10", "This  is a|test      ", "A|short|line|8", "A short|line    "),
    ("Minimum Parenthesis Insertions", "minimum-parenthesis-insertions", "Medium", "Return insertions needed to balance a string containing only opening and closing parentheses.", "()))", "1", "(((", "3"),
    ("Remove Duplicate Letters", "remove-duplicate-letters", "Hard", "Keep one copy of each letter and produce the lexicographically smallest possible result.", "cbacdcbc", "acdb", "bcabc", "abc"),
    ("Count Digit Substrings", "count-digit-substrings", "Easy", "Count contiguous substrings consisting only of digits.", "a12bc345", "5", "abc", "0"),
    ("Reverse Words In Place", "reverse-words-in-place", "Medium", "Reverse the order of words and collapse repeated whitespace to single spaces.", "  hello   world  ", "world hello", "learn code", "code learn"),
    ("Character Shift Cipher", "character-shift-cipher", "Easy", "Shift each English letter forward by k cyclically while preserving case and other characters.", "Abc-z|2", "Cde-b", "Zoo!|1", "App!"),
    ("Longest Common Prefix After Removal", "longest-common-prefix-after-removal", "Hard", "For each word, print the common-prefix length of all remaining pipe-separated words.", "flower|flow|flight", "4 2 2", "aa|ab|ac", "1 1 1"),
]


def starter(language: str) -> str:
    if language == "python":
        return "import sys\n\ndef solve():\n    data = sys.stdin.read().splitlines()\n    # Parse the documented input and print the required result.\n\nif __name__ == '__main__':\n    solve()\n"
    if language == "javascript":
        return "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\r?\\n/);\n// Parse the documented input and print the required result.\n"
    if language == "java":
        return "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));\n        // Parse the documented input and print the required result.\n    }\n}\n"
    return "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Parse the documented input and print the required result.\n    return 0;\n}\n"


def make_problem(index: int, task: tuple[str, ...]) -> dict:
    title, slug, difficulty, operation, public_input, public_output, hidden_input, hidden_output = task
    return {
        "title": title,
        "slug": f"strings-{index:02d}-{slug}",
        "difficulty": difficulty,
        "category": "Strings",
        "topic": "Strings",
        "tags": ["strings", slug.split("-")[0]],
        "description": (
            f"{operation} Inputs use the pipe-separated notation shown in the examples when more than one "
            "logical value is supplied. Treat characters exactly as stated, and print only the requested result."
        ),
        "input_format": "The input is a whitespace- or pipe-separated record; the examples show the exact token order for the operation.",
        "output_format": "Print the requested string, integer, boolean, or sequence on one line.",
        "constraints": "1 <= length of each string <= 100000; input uses printable ASCII characters unless the operation says otherwise.",
        "examples": [
            {"input": public_input, "output": public_output},
            {"input": hidden_input, "output": hidden_output},
        ],
        "hints": [
            "Track frequencies or a left and right boundary instead of repeatedly rebuilding substrings.",
            "Preserve the distinction between character order and character frequency.",
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
    path = Path(__file__).parents[1] / "datasets" / "strings.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"problems": [make_problem(i, task) for i, task in enumerate(TASKS, 1)]}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(TASKS)} problems to {path}")


if __name__ == "__main__":
    main()
