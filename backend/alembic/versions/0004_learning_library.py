"""Add lessons, practice, bookmarks, and history.

Revision ID: 0004_learning_library
Revises: 0003_user_activity
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_learning_library"
down_revision = "0003_user_activity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(180), nullable=False, unique=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("code_example", sa.Text()),
        sa.Column("video_url", sa.String(500)),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default="30"),
    )
    op.create_index("ix_lessons_subject_id", "lessons", ["subject_id"])
    op.create_index("ix_lessons_slug", "lessons", ["slug"], unique=True)

    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress_user_lesson"),
    )
    op.create_index("ix_lesson_progress_user_id", "lesson_progress", ["user_id"])
    op.create_index("ix_lesson_progress_lesson_id", "lesson_progress", ["lesson_id"])

    op.create_table(
        "practice_problems",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("acceptance_rate", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_practice_problems_slug", "practice_problems", ["slug"], unique=True)

    op.create_table(
        "practice_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_id", sa.Integer(), sa.ForeignKey("practice_problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("language", sa.String(40), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="submitted"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_practice_submissions_user_id", "practice_submissions", ["user_id"])
    op.create_index("ix_practice_submissions_problem_id", "practice_submissions", ["problem_id"])

    op.create_table(
        "user_bookmarks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_bookmark_target"),
    )
    op.create_index("ix_user_bookmarks_user_id", "user_bookmarks", ["user_id"])

    op.create_table(
        "user_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("viewed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_history_user_id", "user_history", ["user_id"])

    subjects = sa.table("subjects", sa.column("id", sa.Integer()), sa.column("name", sa.String()))
    lessons = sa.table(
        "lessons",
        sa.column("subject_id", sa.Integer()),
        sa.column("title", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("summary", sa.Text()),
        sa.column("content", sa.Text()),
        sa.column("code_example", sa.Text()),
        sa.column("order_index", sa.Integer()),
        sa.column("estimated_minutes", sa.Integer()),
    )
    subject_rows = {row.name: row.id for row in op.get_bind().execute(sa.select(subjects.c.id, subjects.c.name))}
    lesson_rows = []
    for subject_name, slug, title, summary, content, code in [
        ("Python", "python-foundations", "Python foundations", "Variables, values, and readable programs.", "Learn how values and names work together to build small, reliable programs.", "name = 'Learn2Code'\nprint(name)"),
        ("Python", "python-collections", "Working with collections", "Use lists and dictionaries to organize data.", "Collections let you group related values and choose the right structure for each problem.", "habits = {'coding': True}\nprint(habits['coding'])"),
        ("React", "react-components", "Components and props", "Build reusable interface components.", "Components keep UI behavior understandable and reusable as an application grows.", "function Greeting({name}) {\n  return <h1>Hello {name}</h1>\n}"),
        ("SQL & Databases", "sql-select", "Querying with SELECT", "Read data with clear SQL queries.", "SELECT queries let you retrieve exactly the records needed by an application.", "SELECT name FROM learners WHERE active = true;"),
    ]:
        if subject_name in subject_rows:
            lesson_rows.append({
                "subject_id": subject_rows[subject_name], "title": title, "slug": slug,
                "summary": summary, "content": content, "code_example": code,
                "order_index": len([row for row in lesson_rows if row["subject_id"] == subject_rows[subject_name]]) + 1,
                "estimated_minutes": 30,
            })
    op.bulk_insert(lessons, lesson_rows)

    problems = sa.table(
        "practice_problems", sa.column("title", sa.String()), sa.column("slug", sa.String()),
        sa.column("description", sa.Text()), sa.column("difficulty", sa.String()),
        sa.column("category", sa.String()), sa.column("acceptance_rate", sa.Float()),
    )
    op.bulk_insert(problems, [
        {"title": "Two Sum", "slug": "two-sum", "description": "Return indices of two values that add up to a target.", "difficulty": "Easy", "category": "Arrays", "acceptance_rate": 48.0},
        {"title": "Valid Parentheses", "slug": "valid-parentheses", "description": "Determine whether brackets are correctly balanced.", "difficulty": "Easy", "category": "Stack", "acceptance_rate": 54.0},
        {"title": "Merge Intervals", "slug": "merge-intervals", "description": "Merge overlapping intervals into a minimal list.", "difficulty": "Medium", "category": "Sorting", "acceptance_rate": 41.0},
        {"title": "Trapping Rain Water", "slug": "trapping-rain-water", "description": "Calculate how much water can be trapped between bars.", "difficulty": "Hard", "category": "Arrays", "acceptance_rate": 29.0},
    ])


def downgrade() -> None:
    op.drop_index("ix_user_history_user_id", table_name="user_history")
    op.drop_table("user_history")
    op.drop_index("ix_user_bookmarks_user_id", table_name="user_bookmarks")
    op.drop_table("user_bookmarks")
    op.drop_index("ix_practice_submissions_problem_id", table_name="practice_submissions")
    op.drop_index("ix_practice_submissions_user_id", table_name="practice_submissions")
    op.drop_table("practice_submissions")
    op.drop_index("ix_practice_problems_slug", table_name="practice_problems")
    op.drop_table("practice_problems")
    op.drop_index("ix_lesson_progress_lesson_id", table_name="lesson_progress")
    op.drop_index("ix_lesson_progress_user_id", table_name="lesson_progress")
    op.drop_table("lesson_progress")
    op.drop_index("ix_lessons_slug", table_name="lessons")
    op.drop_index("ix_lessons_subject_id", table_name="lessons")
    op.drop_table("lessons")
