"""Add submission metrics and admin import jobs.

Revision ID: 0012_admin_import_analytics
Revises: 0011_practice_test_cases
"""
from alembic import op
import sqlalchemy as sa

revision = "0012_admin_import_analytics"
down_revision = "0011_practice_test_cases"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("practice_problems", sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()))
    for name, column in [
        ("stdout", sa.Text()),
        ("stderr", sa.Text()),
        ("duration_ms", sa.Integer(),),
        ("memory_kb", sa.Integer()),
        ("passed_tests", sa.Integer()),
        ("total_tests", sa.Integer()),
    ]:
        op.add_column("practice_submissions", sa.Column(name, column, nullable=True))
    op.create_table(
        "problem_import_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_format", sa.String(10), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False, server_default="skip"),
        sa.Column("status", sa.String(20), nullable=False, server_default="completed"),
        sa.Column("imported_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors_json", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_problem_import_jobs_admin_id", "problem_import_jobs", ["admin_id"])


def downgrade() -> None:
    op.drop_index("ix_problem_import_jobs_admin_id", table_name="problem_import_jobs")
    op.drop_table("problem_import_jobs")
    for name in ["total_tests", "passed_tests", "memory_kb", "duration_ms", "stderr", "stdout"]:
        op.drop_column("practice_submissions", name)
    op.drop_column("practice_problems", "is_published")
