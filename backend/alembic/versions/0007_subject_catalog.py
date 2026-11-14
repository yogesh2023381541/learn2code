"""Expand the subject catalog and add an original DSA starter set.

Revision ID: 0007_subject_catalog
Revises: 0006_intelligence_features
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_subject_catalog"
down_revision = "0006_intelligence_features"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    subjects = sa.table(
        "subjects",
        sa.column("name", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("category", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("difficulty", sa.String()),
        sa.column("estimated_minutes", sa.Integer()),
        sa.column("is_published", sa.Boolean()),
    )
    existing = {row.slug for row in bind.execute(sa.select(subjects.c.slug))}
    catalog = [
        ("Full-Stack Development", "full-stack-development", "Web development", "Build complete web applications from UI to production APIs.", "intermediate", 2400),
        ("Machine Learning", "machine-learning", "Data and AI", "Learn practical machine learning foundations, evaluation, and projects.", "intermediate", 2100),
        ("DBMS", "dbms", "Computer science", "Understand data models, transactions, indexing, and database internals.", "intermediate", 1200),
        ("Computer Networks", "computer-networks", "Computer science", "Learn how modern networks move data reliably and securely.", "intermediate", 1200),
        ("System Design", "system-design", "Engineering", "Practice scalable architecture, trade-offs, and design communication.", "advanced", 1800),
        ("Aptitude", "aptitude", "Interview preparation", "Build quantitative, logical, and verbal reasoning speed.", "beginner", 900),
    ]
    for name, slug, category, description, difficulty, minutes in catalog:
        if slug not in existing:
            bind.execute(sa.insert(subjects).values(
                name=name, slug=slug, category=category, description=description,
                difficulty=difficulty, estimated_minutes=minutes, is_published=True,
            ))

    subject_ids = {row.slug: row.id for row in bind.execute(
        sa.text("SELECT id, slug FROM subjects WHERE is_published = true")
    )}
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
    lesson_templates = {
        "full-stack-development": ["Web foundations", "Backend APIs", "Authentication", "Deployment"],
        "machine-learning": ["Data preparation", "Regression and classification", "Model evaluation", "ML project workflow"],
        "dbms": ["Relational modeling", "Transactions", "Indexes", "Query planning"],
        "computer-networks": ["Networking fundamentals", "HTTP and HTTPS", "TCP and UDP", "Network security"],
        "system-design": ["Requirements and constraints", "Data and APIs", "Scaling strategies", "Reliability and observability"],
        "aptitude": ["Percentages and ratios", "Time and work", "Logical reasoning", "Verbal reasoning"],
        "data-structures-algorithms": ["Arrays and hashing", "Two pointers and sliding window", "Stacks and queues", "Trees and graphs", "Dynamic programming"],
    }
    existing_lessons = {row.slug for row in bind.execute(sa.text("SELECT slug FROM lessons"))}
    for subject_slug, titles in lesson_templates.items():
        subject_id = subject_ids.get(subject_slug)
        if subject_id is None:
            continue
        for order, title in enumerate(titles, 1):
            lesson_slug = f"{subject_slug}-{order}"
            if lesson_slug in existing_lessons:
                continue
            bind.execute(sa.insert(lessons).values(
                subject_id=subject_id, title=title, slug=lesson_slug,
                summary=f"Build a practical understanding of {title.lower()}.",
                content=f"This lesson introduces {title.lower()} with guided notes, examples, and exercises. Video placeholder: add your link later.",
                code_example=None, order_index=order, estimated_minutes=35,
            ))

    problems = sa.table(
        "practice_problems", sa.column("title", sa.String()), sa.column("slug", sa.String()),
        sa.column("description", sa.Text()), sa.column("difficulty", sa.String()),
        sa.column("category", sa.String()), sa.column("acceptance_rate", sa.Float()),
    )
    existing_problems = {row.slug for row in bind.execute(sa.text("SELECT slug FROM practice_problems"))}
    original_problems = [
        ("Longest Unique Window", "longest-unique-window", "Find the longest contiguous window with no repeated value.", "Medium", "Sliding Window"),
        ("Rotated Search", "rotated-search", "Find a target in a sorted array rotated at an unknown pivot.", "Medium", "Binary Search"),
        ("Daily Temperatures", "daily-temperatures", "For each day, find how many days until a warmer temperature.", "Medium", "Monotonic Stack"),
        ("Level Order Values", "level-order-values", "Return binary-tree values grouped by their depth.", "Medium", "Trees"),
        ("Course Prerequisites", "course-prerequisites", "Determine whether course prerequisites contain a cycle.", "Medium", "Graphs"),
        ("Minimum Coins", "minimum-coins", "Find the minimum number of coins needed for a target amount.", "Medium", "Dynamic Programming"),
    ]
    for title, slug, description, difficulty, category in original_problems:
        if slug not in existing_problems:
            bind.execute(sa.insert(problems).values(
                title=title, slug=slug, description=description,
                difficulty=difficulty, category=category, acceptance_rate=0,
            ))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text(
        "DELETE FROM practice_problems WHERE slug IN "
        "('longest-unique-window', 'rotated-search', 'daily-temperatures', "
        "'level-order-values', 'course-prerequisites', 'minimum-coins')"
    ))
    bind.execute(sa.text(
        "DELETE FROM lessons WHERE slug LIKE 'full-stack-development-%' "
        "OR slug LIKE 'machine-learning-%' OR slug LIKE 'dbms-%' "
        "OR slug LIKE 'computer-networks-%' OR slug LIKE 'system-design-%' "
        "OR slug LIKE 'aptitude-%' OR slug LIKE 'data-structures-algorithms-%'"
    ))
    bind.execute(sa.text(
        "DELETE FROM subjects WHERE slug IN ('full-stack-development', 'machine-learning', "
        "'dbms', 'computer-networks', 'system-design', 'aptitude')"
    ))
