"""initial schema — precision teaching v1 (two-DB redesign)

Fresh baseline for the redesigned relational schema (see backend/db/schema.sql
and docs/data-schema.md). This is a NEW history root (down_revision = None).

NOTE: the older revisions (baseline_existing_schema / *_sync) belong to the
discarded design. Before running this on a fresh DB, remove those obsolete
files from alembic/versions/ so there is a single head, or stamp a clean DB:
    alembic stamp base && alembic upgrade head

Revision ID: 0001_init
Revises:
"""
from pathlib import Path

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

# backend/db/schema.sql  (this file is at backend/alembic/versions/)
_SCHEMA_SQL = Path(__file__).resolve().parents[2] / "db" / "schema.sql"

# reverse-dependency drop order for downgrade
_TABLES = [
    "composite_grade", "student_progress", "chapter_visit_daily",
    "attendance_record", "attendance_session", "discussion_participation",
    "media_view", "task_completion", "learning_resource",
    "question_response", "submission", "kp_generation_log",
    "question_knowledge_point", "question_option", "question", "assessment",
    "knowledge_point", "concept", "enrollment", "student", "chapter",
    "course", "teacher",
]
_TYPES = [
    "review_status", "content_source", "attendance_status", "task_status",
    "submission_status", "question_type", "assessment_type",
]


def _statements(sql: str):
    """Split DDL into individual statements (asyncpg rejects multi-statement
    execute). Strips line comments; this schema has no dollar-quoted blocks."""
    stripped = "\n".join(line.split("--", 1)[0] for line in sql.splitlines())
    return [s.strip() for s in stripped.split(";") if s.strip()]


def upgrade() -> None:
    sql = _SCHEMA_SQL.read_text(encoding="utf-8")
    for stmt in _statements(sql):
        op.execute(sa.text(stmt))


def downgrade() -> None:
    for table in _TABLES:
        op.execute(sa.text(f"DROP TABLE IF EXISTS {table} CASCADE"))
    for enum in _TYPES:
        op.execute(sa.text(f"DROP TYPE IF EXISTS {enum}"))
