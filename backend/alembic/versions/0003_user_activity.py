"""Persist dashboard learning activity.

Revision ID: 0003_user_activity
Revises: 0002_subject_enrollments
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_user_activity"
down_revision = "0002_subject_enrollments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_activity",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activity_date", sa.Date(), nullable=False),
        sa.Column("minutes", sa.Integer(), nullable=False),
        sa.Column("activity_type", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_activity_user_id", "user_activity", ["user_id"], unique=False)
    op.create_index("ix_user_activity_activity_date", "user_activity", ["activity_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_activity_activity_date", table_name="user_activity")
    op.drop_index("ix_user_activity_user_id", table_name="user_activity")
    op.drop_table("user_activity")
