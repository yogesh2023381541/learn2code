"""Add recommendations, roadmaps, quizzes, revision, and admin drafts.

Revision ID: 0006_intelligence_features
Revises: 0005_ai_assistant
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_intelligence_features"
down_revision = "0005_ai_assistant"
branch_labels = None
depends_on = None


def _table(name, columns):
    op.create_table(name, *columns)


def upgrade() -> None:
    fk_user = lambda: sa.ForeignKey("users.id", ondelete="CASCADE")
    _table("ai_recommendations", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), fk_user(), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("reason", sa.Text(), nullable=False), sa.Column("target_type", sa.String(30), nullable=False), sa.Column("target_id", sa.Integer(), nullable=False), sa.Column("evidence_json", sa.Text(), nullable=False), sa.Column("dismissed", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)])
    op.create_index("ix_ai_recommendations_user_id", "ai_recommendations", ["user_id"])
    _table("personalized_roadmaps", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), fk_user(), nullable=False), sa.Column("goal", sa.String(180), nullable=False), sa.Column("experience_level", sa.String(30), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)])
    op.create_index("ix_personalized_roadmaps_user_id", "personalized_roadmaps", ["user_id"])
    _table("personalized_roadmap_nodes", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("roadmap_id", sa.Integer(), sa.ForeignKey("personalized_roadmaps.id", ondelete="CASCADE"), nullable=False), sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False), sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id", ondelete="SET NULL")), sa.Column("title", sa.String(180), nullable=False), sa.Column("node_type", sa.String(30), nullable=False, server_default="lesson"), sa.Column("order_index", sa.Integer(), nullable=False), sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default="30"), sa.Column("prerequisite_ids", sa.Text(), nullable=False, server_default="[]")])
    op.create_index("ix_personalized_roadmap_nodes_roadmap_id", "personalized_roadmap_nodes", ["roadmap_id"])
    op.create_index("ix_personalized_roadmap_nodes_subject_id", "personalized_roadmap_nodes", ["subject_id"])
    _table("quizzes", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), fk_user(), nullable=False), sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="SET NULL")), sa.Column("title", sa.String(180), nullable=False), sa.Column("difficulty", sa.String(20), nullable=False), sa.Column("question_count", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)])
    op.create_index("ix_quizzes_user_id", "quizzes", ["user_id"])
    _table("quiz_questions", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("quiz_id", sa.Integer(), sa.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False), sa.Column("prompt", sa.Text(), nullable=False), sa.Column("options_json", sa.Text(), nullable=False), sa.Column("correct_answer", sa.String(200), nullable=False), sa.Column("explanation", sa.Text(), nullable=False)])
    op.create_index("ix_quiz_questions_quiz_id", "quiz_questions", ["quiz_id"])
    _table("quiz_attempts", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), fk_user(), nullable=False), sa.Column("quiz_id", sa.Integer(), sa.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False), sa.Column("score", sa.Integer(), nullable=False), sa.Column("answers_json", sa.Text(), nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)])
    op.create_index("ix_quiz_attempts_user_id", "quiz_attempts", ["user_id"])
    _table("revision_sessions", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), fk_user(), nullable=False), sa.Column("topic", sa.String(180), nullable=False), sa.Column("due_at", sa.DateTime(timezone=True), nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True)), sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1")])
    op.create_index("ix_revision_sessions_user_id", "revision_sessions", ["user_id"])
    op.create_index("ix_revision_sessions_due_at", "revision_sessions", ["due_at"])
    _table("flashcards", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), fk_user(), nullable=False), sa.Column("topic", sa.String(180), nullable=False), sa.Column("front", sa.Text(), nullable=False), sa.Column("back", sa.Text(), nullable=False)])
    op.create_index("ix_flashcards_user_id", "flashcards", ["user_id"])
    _table("flashcard_reviews", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), fk_user(), nullable=False), sa.Column("flashcard_id", sa.Integer(), sa.ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False), sa.Column("quality", sa.Integer(), nullable=False), sa.Column("reviewed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)])
    op.create_index("ix_flashcard_reviews_user_id", "flashcard_reviews", ["user_id"])
    op.create_index("ix_flashcard_reviews_flashcard_id", "flashcard_reviews", ["flashcard_id"])
    _table("admin_content_drafts", [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("author_id", sa.Integer(), fk_user(), nullable=False), sa.Column("content_type", sa.String(40), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("body_json", sa.Text(), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="pending"), sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)])
    op.create_index("ix_admin_content_drafts_author_id", "admin_content_drafts", ["author_id"])


def downgrade() -> None:
    for index, table in [
        ("ix_admin_content_drafts_author_id", "admin_content_drafts"),
        ("ix_flashcard_reviews_flashcard_id", "flashcard_reviews"), ("ix_flashcard_reviews_user_id", "flashcard_reviews"),
        ("ix_flashcards_user_id", "flashcards"), ("ix_revision_sessions_due_at", "revision_sessions"), ("ix_revision_sessions_user_id", "revision_sessions"),
        ("ix_quiz_attempts_user_id", "quiz_attempts"), ("ix_quiz_questions_quiz_id", "quiz_questions"), ("ix_quizzes_user_id", "quizzes"),
        ("ix_personalized_roadmap_nodes_subject_id", "personalized_roadmap_nodes"), ("ix_personalized_roadmap_nodes_roadmap_id", "personalized_roadmap_nodes"),
        ("ix_personalized_roadmaps_user_id", "personalized_roadmaps"), ("ix_ai_recommendations_user_id", "ai_recommendations"),
    ]:
        op.drop_index(index, table_name=table)
    for table in ["admin_content_drafts", "flashcard_reviews", "flashcards", "revision_sessions", "quiz_attempts", "quiz_questions", "quizzes", "personalized_roadmap_nodes", "personalized_roadmaps", "ai_recommendations"]:
        op.drop_table(table)
