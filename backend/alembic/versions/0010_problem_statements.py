"""Add starter code and complete original problem statements.

Revision ID: 0010_problem_statements
Revises: 0009_problem_progress
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_problem_statements"
down_revision = "0009_problem_progress"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("practice_problems", sa.Column("starter_code", sa.Text()))
    bind = op.get_bind()
    statements = {
        "two-sum": (
            "Given an integer array values and an integer target, return the indices of the two distinct values whose sum equals target. "
            "You may assume exactly one valid pair exists. Return the pair in any order.",
            "values = [2, 7, 11, 15]\ntarget = 9\n# Return the indices of the matching pair\n",
        ),
        "valid-parentheses": (
            "Given a string containing only the characters (, ), {, }, [ and ], determine whether the bracket sequence is balanced. "
            "Every closing bracket must match the most recent unmatched opening bracket.",
            'text = "()[]{}"\n# Return True when the sequence is balanced\n',
        ),
        "merge-intervals": (
            "Given a list of closed intervals, merge every pair that overlaps and return the resulting non-overlapping intervals sorted by start time. "
            "Intervals that only touch at an endpoint are considered overlapping.",
            "intervals = [[1, 3], [2, 6], [8, 10], [9, 12]]\n# Return the merged intervals\n",
        ),
        "trapping-rain-water": (
            "Given an array of non-negative bar heights where each bar has width one, return the total volume of water trapped after rainfall. "
            "Water cannot flow outside the array.",
            "heights = [0, 1, 0, 2, 1, 0, 1, 3]\n# Return the trapped water volume\n",
        ),
    }
    for slug, (description, starter_code) in statements.items():
        bind.execute(sa.text(
            "UPDATE practice_problems SET description=:description, starter_code=:starter_code WHERE slug=:slug"
        ), {"slug": slug, "description": description, "starter_code": starter_code})


def downgrade() -> None:
    op.drop_column("practice_problems", "starter_code")
