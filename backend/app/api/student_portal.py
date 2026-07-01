"""
Espace étudiant — portail personnel
GET /api/student/me/courses      → cours de l'étudiant
GET /api/student/me/dashboard    → tableau de bord personnel
GET /api/student/me/mastery      → maîtrise par KP
GET /api/student/me/history      → historique des soumissions
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import student_required
from app.core.postgres_client import get_pg_session

router = APIRouter(prefix="/api/student", tags=["Student Portal"])


async def _rows(session: AsyncSession, sql: str, **params) -> list[dict]:
    res = await session.execute(text(sql), params)
    return [dict(r) for r in res.mappings().all()]


async def _get_student_id(session: AsyncSession, user_sub: str) -> int:
    """Resolve user_id → student_id."""
    res = await session.execute(
        text("SELECT student_id FROM app_user WHERE user_id = :uid"),
        {"uid": int(user_sub)},
    )
    row = res.mappings().first()
    if not row or not row["student_id"]:
        raise HTTPException(404, "Profil étudiant introuvable")
    return int(row["student_id"])


@router.get("/me/courses")
async def my_courses(
    session: AsyncSession = Depends(get_pg_session),
    user: dict = Depends(student_required),
):
    student_id = await _get_student_id(session, user["sub"])
    rows = await _rows(
        session,
        """
        SELECT c.course_code, c.course_name, c.term_code, e.class_name
        FROM enrollment e
        JOIN course c ON c.course_id = e.course_id
        WHERE e.student_id = :sid
        ORDER BY c.course_code
        """,
        sid=student_id,
    )
    return rows


@router.get("/me/dashboard")
async def my_dashboard(
    course_code: str,
    session: AsyncSession = Depends(get_pg_session),
    user: dict = Depends(student_required),
):
    student_id = await _get_student_id(session, user["sub"])

    # Stats personnelles
    personal = await _rows(
        session,
        """
        SELECT
            COUNT(qr.response_id)                                          AS total_responses,
            SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END)               AS correct,
            AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END)           AS accuracy,
            cg.homework_score,
            cg.final_score,
            sp.task_completed_count,
            sp.task_total_count,
            sp.discussion_count,
            sp.chapter_visit_count
        FROM enrollment e
        JOIN course c ON c.course_id = e.course_id AND c.course_code = :cc
        LEFT JOIN submission s ON s.enrollment_id = e.enrollment_id
        LEFT JOIN question_response qr ON qr.submission_id = s.submission_id
        LEFT JOIN composite_grade cg ON cg.enrollment_id = e.enrollment_id
        LEFT JOIN student_progress sp ON sp.enrollment_id = e.enrollment_id
        WHERE e.student_id = :sid
        GROUP BY cg.homework_score, cg.final_score,
                 sp.task_completed_count, sp.task_total_count,
                 sp.discussion_count, sp.chapter_visit_count
        """,
        sid=student_id, cc=course_code,
    )

    # Moyenne de la classe (pour comparaison anonyme)
    class_avg = await _rows(
        session,
        """
        SELECT
            AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) AS class_accuracy,
            AVG(cg.homework_score)                               AS class_homework,
            AVG(cg.final_score)                                  AS class_final
        FROM enrollment e
        JOIN course c ON c.course_id = e.course_id AND c.course_code = :cc
        LEFT JOIN submission s ON s.enrollment_id = e.enrollment_id
        LEFT JOIN question_response qr ON qr.submission_id = s.submission_id
        LEFT JOIN composite_grade cg ON cg.enrollment_id = e.enrollment_id
        """,
        cc=course_code,
    )

    # KP faibles personnels (accuracy < 0.6)
    weak_kps = await _rows(
        session,
        """
        SELECT kp.label, kp.kp_code,
               COUNT(qr.response_id)                              AS total,
               SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END)   AS correct,
               AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) AS accuracy
        FROM enrollment e
        JOIN course c ON c.course_id = e.course_id AND c.course_code = :cc
        JOIN submission s ON s.enrollment_id = e.enrollment_id
        JOIN question_response qr ON qr.submission_id = s.submission_id
        JOIN question_knowledge_point qkp ON qkp.question_id = qr.question_id
             AND qkp.review_status = 'approved'
        JOIN knowledge_point kp ON kp.kp_id = qkp.kp_id
        WHERE e.student_id = :sid
        GROUP BY kp.label, kp.kp_code
        HAVING AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) < 0.6
        ORDER BY accuracy ASC
        LIMIT 5
        """,
        sid=student_id, cc=course_code,
    )

    p = personal[0] if personal else {}
    ca = class_avg[0] if class_avg else {}

    def fnum(v):
        return round(float(v), 3) if v is not None else None

    total = int(p.get("total_responses") or 0)
    correct = int(p.get("correct") or 0)

    return {
        "personal": {
            "total_responses": total,
            "correct": correct,
            "accuracy": fnum(p.get("accuracy")),
            "homework_score": fnum(p.get("homework_score")),
            "final_score": fnum(p.get("final_score")),
            "task_completed": p.get("task_completed_count"),
            "task_total": p.get("task_total_count"),
            "discussion_count": p.get("discussion_count"),
            "chapter_visit_count": p.get("chapter_visit_count"),
        },
        "class_avg": {
            "accuracy": fnum(ca.get("class_accuracy")),
            "homework_score": fnum(ca.get("class_homework")),
            "final_score": fnum(ca.get("class_final")),
        },
        "weak_kps": [
            {
                "kp_code": r["kp_code"],
                "label": r["label"],
                "total": int(r["total"]),
                "correct": int(r["correct"]),
                "accuracy": fnum(r["accuracy"]),
            }
            for r in weak_kps
        ],
    }


@router.get("/me/mastery")
async def my_mastery(
    course_code: str,
    session: AsyncSession = Depends(get_pg_session),
    user: dict = Depends(student_required),
):
    student_id = await _get_student_id(session, user["sub"])
    rows = await _rows(
        session,
        """
        SELECT kp.kp_code, kp.label,
               COUNT(qr.response_id)                              AS total,
               SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END)   AS correct,
               AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) AS accuracy
        FROM enrollment e
        JOIN course c ON c.course_id = e.course_id AND c.course_code = :cc
        JOIN submission s ON s.enrollment_id = e.enrollment_id
        JOIN question_response qr ON qr.submission_id = s.submission_id
        JOIN question_knowledge_point qkp ON qkp.question_id = qr.question_id
             AND qkp.review_status = 'approved'
        JOIN knowledge_point kp ON kp.kp_id = qkp.kp_id
        WHERE e.student_id = :sid
        GROUP BY kp.kp_code, kp.label
        ORDER BY accuracy ASC
        """,
        sid=student_id, cc=course_code,
    )

    def tier(acc):
        if acc is None: return "no_data"
        if acc >= 0.7:  return "mastered"
        if acc >= 0.4:  return "partial"
        return "unlearned"

    return [
        {
            "kp_code": r["kp_code"],
            "label": r["label"],
            "total": int(r["total"]),
            "correct": int(r["correct"]),
            "accuracy": round(float(r["accuracy"]), 3) if r["accuracy"] is not None else None,
            "tier": tier(float(r["accuracy"]) if r["accuracy"] is not None else None),
        }
        for r in rows
    ]


@router.get("/me/history")
async def my_history(
    course_code: str,
    session: AsyncSession = Depends(get_pg_session),
    user: dict = Depends(student_required),
):
    student_id = await _get_student_id(session, user["sub"])
    rows = await _rows(
        session,
        """
        SELECT a.title, a.type::text AS type, s.total_score, s.status::text AS status,
               s.submitted_at,
               COUNT(qr.response_id)                              AS total,
               SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END)   AS correct
        FROM enrollment e
        JOIN course c ON c.course_id = e.course_id AND c.course_code = :cc
        JOIN submission s ON s.enrollment_id = e.enrollment_id
        JOIN assessment a ON a.assessment_id = s.assessment_id
        LEFT JOIN question_response qr ON qr.submission_id = s.submission_id
        WHERE e.student_id = :sid
        GROUP BY a.title, a.type, s.total_score, s.status, s.submitted_at
        ORDER BY s.submitted_at DESC NULLS LAST
        """,
        sid=student_id, cc=course_code,
    )
    return [
        {
            "title": r["title"],
            "type": r["type"],
            "total_score": float(r["total_score"]) if r["total_score"] is not None else None,
            "status": r["status"],
            "submitted_at": str(r["submitted_at"]) if r["submitted_at"] else None,
            "total_questions": int(r["total"]),
            "correct": int(r["correct"]),
            "accuracy": round(int(r["correct"]) / int(r["total"]), 3) if int(r["total"]) > 0 else None,
        }
        for r in rows
    ]
