"""Add structured problem learning content.

Revision ID: 0008_problem_learning_content
Revises: 0007_subject_catalog
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_problem_learning_content"
down_revision = "0007_subject_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("practice_problems", sa.Column("topic", sa.String(100)))
    op.add_column("practice_problems", sa.Column("pattern", sa.String(100)))
    op.add_column("practice_problems", sa.Column("constraints", sa.Text()))
    op.add_column("practice_problems", sa.Column("examples_json", sa.Text()))
    op.add_column("practice_problems", sa.Column("hints_json", sa.Text()))
    op.add_column("practice_problems", sa.Column("editorial", sa.Text()))
    op.add_column("practice_problems", sa.Column("reference_url", sa.String(500)))
    bind = op.get_bind()
    content = {
        "two-sum": ("Arrays", "Hash Map", "Use each value at most once.", '[{"input":"[2,7,11,15], target=9","output":"[0,1]"}]', '["Can you store values you have already seen?","What complement is needed for the current value?"]', "Scan once while storing value-to-index pairs. For each value, check whether its complement was seen before; this gives linear time and additional linear space.", "https://leetcode.com/problems/two-sum/"),
        "valid-parentheses": ("Stacks", "Matching Stack", "Input contains only bracket characters.", '[{"input":"()[]{}","output":"true"}]', '["What should happen when you see an opening bracket?","Which closing bracket matches the stack top?"]', "Push opening brackets and require every closing bracket to match the latest opening bracket. The stack must be empty at the end.", "https://leetcode.com/problems/valid-parentheses/"),
        "merge-intervals": ("Intervals", "Sort and Merge", "Intervals may be unsorted.", '[{"input":"[[1,3],[2,6]]","output":"[[1,6]]"}]', '["What order makes overlap checks local?","When can the current interval be extended?"]', "Sort by start time, then merge into the last output interval whenever the next start is within the current end.", "https://leetcode.com/problems/merge-intervals/"),
        "trapping-rain-water": ("Arrays", "Two Pointers", "Heights are non-negative.", '[{"input":"[0,1,0,2]","output":"1"}]', '["What limits water at the shorter side?","Can left and right maxima be maintained incrementally?"]', "Maintain left and right maxima and move the pointer with the smaller boundary. That side cannot gain a better boundary by waiting.", "https://leetcode.com/problems/trapping-rain-water/"),
    }
    for slug, values in content.items():
        bind.execute(sa.text(
            "UPDATE practice_problems SET topic=:topic, pattern=:pattern, constraints=:constraints, "
            "examples_json=:examples, hints_json=:hints, editorial=:editorial, reference_url=:reference "
            "WHERE slug=:slug"
        ), {
            "slug": slug, "topic": values[0], "pattern": values[1], "constraints": values[2],
            "examples": values[3], "hints": values[4], "editorial": values[5], "reference": values[6],
        })


def downgrade() -> None:
    for column in ["reference_url", "editorial", "hints_json", "examples_json", "constraints", "pattern", "topic"]:
        op.drop_column("practice_problems", column)
