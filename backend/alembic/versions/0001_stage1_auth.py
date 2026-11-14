"""Create Stage 1 authentication and subject schema.

Revision ID: 0001_stage1_auth
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_stage1_auth"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="student"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("experience_level", sa.String(length=30)),
        sa.Column("learning_goal", sa.String(length=100)),
        sa.Column("preferred_language", sa.String(length=40)),
        sa.Column("daily_minutes", sa.Integer()),
        sa.Column("subjects", sa.Text()),
        sa.Column("learning_hours", sa.Float(), nullable=False, server_default="0"),
        sa.Column("topics_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("problems_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False, server_default="beginner"),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_subjects_slug", "subjects", ["slug"], unique=False)
    op.create_index("ix_subjects_category", "subjects", ["category"], unique=False)
    op.create_index("ix_subjects_is_published", "subjects", ["is_published"], unique=False)
    op.create_table(
        "refresh_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_id", sa.String(length=64), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("token_id"),
    )
    op.create_index("ix_refresh_sessions_user_id", "refresh_sessions", ["user_id"], unique=False)
    op.create_index("ix_refresh_sessions_token_id", "refresh_sessions", ["token_id"], unique=False)
    op.create_index("ix_refresh_sessions_expires_at", "refresh_sessions", ["expires_at"], unique=False)
    subjects = sa.table(
        "subjects",
        sa.column("name", sa.String),
        sa.column("slug", sa.String),
        sa.column("category", sa.String),
        sa.column("description", sa.Text),
        sa.column("difficulty", sa.String),
        sa.column("estimated_minutes", sa.Integer),
        sa.column("is_published", sa.Boolean),
    )
    op.bulk_insert(
        subjects,
        [
            {
                "name": "Python",
                "slug": "python",
                "category": "Programming",
                "description": "Build a strong foundation with Python fundamentals and real projects.",
                "difficulty": "intermediate",
                "estimated_minutes": 1080,
                "is_published": True,
            },
            {
                "name": "Data Structures & Algorithms",
                "slug": "data-structures-algorithms",
                "category": "Computer science",
                "description": "Master problem solving patterns that power great engineering interviews.",
                "difficulty": "intermediate",
                "estimated_minutes": 1920,
                "is_published": True,
            },
            {
                "name": "React",
                "slug": "react",
                "category": "Web development",
                "description": "Create fast, accessible interfaces with modern React and TypeScript.",
                "difficulty": "beginner",
                "estimated_minutes": 1260,
                "is_published": True,
            },
            {
                "name": "SQL & Databases",
                "slug": "sql-databases",
                "category": "Backend",
                "description": "Design reliable data models and write queries with confidence.",
                "difficulty": "beginner",
                "estimated_minutes": 840,
                "is_published": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("refresh_sessions")
    op.drop_index("ix_subjects_is_published", table_name="subjects")
    op.drop_index("ix_subjects_category", table_name="subjects")
    op.drop_index("ix_subjects_slug", table_name="subjects")
    op.drop_table("subjects")
    op.drop_table("user_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
