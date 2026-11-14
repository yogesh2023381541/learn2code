"""Persist user-level DSA problem progress.

Revision ID: 0009_problem_progress
Revises: 0008_problem_learning_content
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_problem_progress"
down_revision = "0008_problem_learning_content"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "practice_problem_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_id", sa.Integer(), sa.ForeignKey("practice_problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="not_started"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bookmarked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("next_revision_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "problem_id", name="uq_problem_progress_user_problem"),
    )
    op.create_index("ix_practice_problem_progress_user_id", "practice_problem_progress", ["user_id"])
    op.create_index("ix_practice_problem_progress_problem_id", "practice_problem_progress", ["problem_id"])


def downgrade() -> None:
    op.drop_index("ix_practice_problem_progress_problem_id", table_name="practice_problem_progress")
    op.drop_index("ix_practice_problem_progress_user_id", table_name="practice_problem_progress")
    op.drop_table("practice_problem_progress")
