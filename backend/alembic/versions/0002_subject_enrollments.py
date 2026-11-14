"""Persist user subject enrollments and progress.

Revision ID: 0002_subject_enrollments
Revises: 0001_stage1_auth
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_subject_enrollments"
down_revision = "0001_stage1_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subject_enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_topic", sa.String(length=160)),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "subject_id", name="uq_subject_enrollments_user_subject"),
    )
    op.create_index("ix_subject_enrollments_user_id", "subject_enrollments", ["user_id"], unique=False)
    op.create_index("ix_subject_enrollments_subject_id", "subject_enrollments", ["subject_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_subject_enrollments_subject_id", table_name="subject_enrollments")
    op.drop_index("ix_subject_enrollments_user_id", table_name="subject_enrollments")
    op.drop_table("subject_enrollments")
