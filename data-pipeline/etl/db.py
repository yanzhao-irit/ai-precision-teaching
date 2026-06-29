"""
ETL 数据库层 · DB helpers (psycopg 3, 同步)
连接信息从环境变量取，默认与 docker-compose / app config 一致。
"""
from __future__ import annotations

import os
import hashlib
from contextlib import contextmanager

import psycopg


def dsn() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'ai_precision_teaching')} "
        f"user={os.getenv('POSTGRES_USER', 'postgres')} "
        f"password={os.getenv('POSTGRES_PASSWORD', 'password')}"
    )


@contextmanager
def connect():
    conn = psycopg.connect(dsn())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def kp_code_for(course_code: str, label: str) -> str:
    """由课程 + 知识点名生成稳定的跨库码（与 Neo4j KnowledgePoint.kp_code 对齐）。"""
    h = hashlib.md5(label.encode("utf-8")).hexdigest()[:10]
    return f"{course_code}:{h}"


# ---------- get-or-create / upsert ----------
def upsert_course(cur, course_code: str, course_name: str | None) -> int:
    # 新建时无名则用 code 兜底；已存在时只有传了新名才更新，否则保留原名
    cur.execute(
        """INSERT INTO course (course_code, course_name)
           VALUES (%s, COALESCE(%s, %s))
           ON CONFLICT (course_code)
           DO UPDATE SET course_name = COALESCE(%s, course.course_name)
           RETURNING course_id""",
        (course_code, course_name, course_code, course_name),
    )
    return cur.fetchone()[0]


def upsert_chapter(cur, course_id: int, chapter_no: int | None, title: str | None) -> int | None:
    if chapter_no is None:
        return None
    cur.execute(
        """INSERT INTO chapter (course_id, chapter_no, title)
           VALUES (%s, %s, %s)
           ON CONFLICT (course_id, chapter_no)
           DO UPDATE SET title = COALESCE(EXCLUDED.title, chapter.title)
           RETURNING chapter_id""",
        (course_id, chapter_no, title or f"第{chapter_no}章"),
    )
    return cur.fetchone()[0]


def get_or_create_assessment(cur, course_id, chapter_id, atype, title, source_file) -> int:
    cur.execute(
        "SELECT assessment_id FROM assessment WHERE course_id=%s AND type=%s AND title=%s",
        (course_id, atype, title),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """INSERT INTO assessment (course_id, chapter_id, type, title, source_file)
           VALUES (%s, %s, %s, %s, %s) RETURNING assessment_id""",
        (course_id, chapter_id, atype, title, source_file),
    )
    return cur.fetchone()[0]


def find_assessment(cur, course_id, chapter_no, atype) -> int | None:
    cur.execute(
        """SELECT a.assessment_id FROM assessment a
           LEFT JOIN chapter c ON c.chapter_id=a.chapter_id
           WHERE a.course_id=%s AND a.type=%s AND COALESCE(c.chapter_no,-1)=%s""",
        (course_id, atype, chapter_no if chapter_no is not None else -1),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_or_create_question(cur, assessment_id, q) -> int:
    cur.execute(
        "SELECT question_id FROM question WHERE assessment_id=%s AND seq_no=%s",
        (assessment_id, q.seq_no),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """INSERT INTO question
             (assessment_id, seq_no, type, stem, correct_answer, explanation,
              difficulty, suggested_score, kp_status)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING question_id""",
        (assessment_id, q.seq_no, q.type, q.stem, q.correct_answer, q.explanation,
         q.difficulty, q.suggested_score,
         "approved" if q.knowledge_point else "pending"),
    )
    return cur.fetchone()[0]


def upsert_option(cur, question_id, opt):
    cur.execute(
        """INSERT INTO question_option (question_id, option_label, option_text, is_correct)
           VALUES (%s,%s,%s,%s)
           ON CONFLICT (question_id, option_label)
           DO UPDATE SET option_text=EXCLUDED.option_text, is_correct=EXCLUDED.is_correct""",
        (question_id, opt.label, opt.text, opt.is_correct),
    )


def upsert_knowledge_point(cur, course_id, course_code, label) -> int:
    code = kp_code_for(course_code, label)
    cur.execute(
        """INSERT INTO knowledge_point (course_id, kp_code, label, source, review_status)
           VALUES (%s,%s,%s,'imported','approved')
           ON CONFLICT (course_id, kp_code)
           DO UPDATE SET label=EXCLUDED.label
           RETURNING kp_id""",
        (course_id, code, label),
    )
    return cur.fetchone()[0]


def link_question_kp(cur, question_id, kp_id):
    cur.execute(
        """INSERT INTO question_knowledge_point
             (question_id, kp_id, source, review_status)
           VALUES (%s,%s,'imported','approved')
           ON CONFLICT (question_id, kp_id) DO NOTHING""",
        (question_id, kp_id),
    )


def upsert_student(cur, student_no, full_name) -> int:
    cur.execute(
        """INSERT INTO student (student_no, full_name)
           VALUES (%s,%s)
           ON CONFLICT (student_no)
           DO UPDATE SET full_name=COALESCE(EXCLUDED.full_name, student.full_name)
           RETURNING student_id""",
        (student_no, full_name),
    )
    return cur.fetchone()[0]


def upsert_enrollment(cur, student_id, course_id, **org) -> int:
    cur.execute(
        """INSERT INTO enrollment
             (student_id, course_id, school_name, department_name, major_name,
              class_name, admission_year)
           VALUES (%s,%s,%s,%s,%s,%s,%s)
           ON CONFLICT (student_id, course_id)
           DO UPDATE SET class_name=COALESCE(EXCLUDED.class_name, enrollment.class_name)
           RETURNING enrollment_id""",
        (student_id, course_id, org.get("school"), org.get("department"),
         org.get("major"), org.get("class_name"), org.get("admission_year")),
    )
    return cur.fetchone()[0]


def upsert_submission(cur, enrollment_id, assessment_id, total, status, submitted_at, src) -> int:
    cur.execute(
        """INSERT INTO submission
             (enrollment_id, assessment_id, total_score, status, submitted_at, source_file)
           VALUES (%s,%s,%s,%s,%s,%s)
           ON CONFLICT (enrollment_id, assessment_id)
           DO UPDATE SET total_score=EXCLUDED.total_score, status=EXCLUDED.status,
                         submitted_at=EXCLUDED.submitted_at
           RETURNING submission_id""",
        (enrollment_id, assessment_id, total, status, submitted_at, src),
    )
    return cur.fetchone()[0]


def upsert_response(cur, submission_id, question_id, r):
    cur.execute(
        """INSERT INTO question_response
             (submission_id, question_id, student_answer, answer_snapshot, is_correct, score)
           VALUES (%s,%s,%s,%s,%s,%s)
           ON CONFLICT (submission_id, question_id)
           DO UPDATE SET student_answer=EXCLUDED.student_answer,
                         answer_snapshot=EXCLUDED.answer_snapshot,
                         is_correct=EXCLUDED.is_correct, score=EXCLUDED.score""",
        (submission_id, question_id, r.student_answer, r.correct_answer, r.is_correct, r.score),
    )
