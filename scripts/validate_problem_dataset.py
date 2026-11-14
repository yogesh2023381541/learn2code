import ast
import json
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "title",
    "slug",
    "difficulty",
    "category",
    "description",
    "input_format",
    "output_format",
    "constraints",
    "examples",
    "test_cases",
    "starter_code",
    "time_limit_ms",
    "memory_limit_mb",
}
LANGUAGES = {"python", "java", "cpp", "javascript"}


def validate(path: Path, expected_count: int) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    problems = data.get("problems")
    assert isinstance(problems, list), "top-level problems must be a list"
    assert len(problems) == expected_count, f"expected {expected_count} problems, got {len(problems)}"
    slugs = [problem["slug"] for problem in problems]
    titles = [problem["title"] for problem in problems]
    assert len(set(slugs)) == len(slugs), "duplicate slug"
    assert len(set(titles)) == len(titles), "duplicate title"

    for number, problem in enumerate(problems, 1):
        missing = REQUIRED_FIELDS - problem.keys()
        assert not missing, f"problem {number} missing {sorted(missing)}"
        assert problem["difficulty"] in {"Easy", "Medium", "Hard"}
        assert len(problem["examples"]) >= 2, f"problem {number} needs two examples"
        cases = problem["test_cases"]
        assert any(not case["is_hidden"] for case in cases), f"problem {number} has no public case"
        assert any(case["is_hidden"] for case in cases), f"problem {number} has no hidden case"
        assert set(problem["starter_code"]) == LANGUAGES, f"problem {number} starter languages mismatch"
        ast.parse(problem["starter_code"]["python"])

    print(f"validated {len(problems)} problems in {path}")
    print("validated: JSON, required fields, unique titles/slugs, examples, public/hidden tests, starter keys, Python syntax")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_problem_dataset.py DATASET EXPECTED_COUNT")
    validate(Path(sys.argv[1]), int(sys.argv[2]))
