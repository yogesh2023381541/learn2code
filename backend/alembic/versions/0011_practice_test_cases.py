"""Add public and private practice test cases.

Revision ID: 0011_practice_test_cases
Revises: 0010_problem_statements
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_practice_test_cases"
down_revision = "0010_problem_statements"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "practice_test_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("problem_id", sa.Integer(), sa.ForeignKey("practice_problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stdin", sa.Text(), nullable=False, server_default=""),
        sa.Column("expected_stdout", sa.Text(), nullable=False),
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("time_limit_ms", sa.Integer(), nullable=False, server_default="3000"),
        sa.Column("memory_limit_mb", sa.Integer(), nullable=False, server_default="256"),
    )
    op.create_index("ix_practice_test_cases_problem_id", "practice_test_cases", ["problem_id"])

    bind = op.get_bind()
    problems = {
        row.slug: row.id
        for row in bind.execute(sa.text("SELECT id, slug FROM practice_problems"))
    }
    cases = {
        "two-sum": [
            ("2 7 11 15\n9\n", "[0, 1]\n", False),
            ("3 2 4\n6\n", "[1, 2]\n", True),
        ],
        "valid-parentheses": [
            ("()[]{}\n", "true\n", False),
            ("([)]\n", "false\n", True),
        ],
        "merge-intervals": [
            ("1 3\n2 6\n8 10\n", "[[1, 6], [8, 10]]\n", False),
        ],
        "trapping-rain-water": [
            ("0 1 0 2\n", "1\n", False),
        ],
    }
    table = sa.table(
        "practice_test_cases",
        sa.column("problem_id", sa.Integer()),
        sa.column("stdin", sa.Text()),
        sa.column("expected_stdout", sa.Text()),
        sa.column("is_hidden", sa.Boolean()),
        sa.column("order_index", sa.Integer()),
    )
    for slug, problem_cases in cases.items():
        problem_id = problems.get(slug)
        if problem_id is None:
            continue
        for order_index, (stdin, expected_stdout, is_hidden) in enumerate(problem_cases):
            bind.execute(sa.insert(table).values(
                problem_id=problem_id,
                stdin=stdin,
                expected_stdout=expected_stdout,
                is_hidden=is_hidden,
                order_index=order_index,
            ))


def downgrade() -> None:
    op.drop_index("ix_practice_test_cases_problem_id", table_name="practice_test_cases")
    op.drop_table("practice_test_cases")
