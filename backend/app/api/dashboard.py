"""
教师端看板 API · Teacher dashboard API
======================================
课程总览 / 班级筛选 / 薄弱知识点 / 高错题 / 干扰项分析 / 知识点详情。
所有接口按 ?course_code= 取课程，?class_name= 可选按班级筛选（缺省=全部班级）。
掌握度沿用诊断引擎 BKT，详见 app/services/dashboard.py。
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_sql
from app.data_access import SqlRepository
from app.services import CourseAnalytics

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def _cc(course_code: str = Query(..., description="课程码，如 AI-BASE-2025")) -> str:
    return course_code


def _class(class_name: str | None = Query(None, description="班级名，缺省=全部班级")):
    return class_name


# ---------- 课程列表（带统计）----------
@router.get("/courses")
async def courses_with_stats(sql: SqlRepository = Depends(get_sql)):
    """① 课程列表：每门课的班级数/学生数/已测章节/整体正确率。"""
    return await sql.course_summaries()


# ---------- 某课程的班级 ----------
@router.get("/classes")
async def classes(course_code: str = Depends(_cc), sql: SqlRepository = Depends(get_sql)):
    """课程下的班级列表（用于看板筛选器）。"""
    return await sql.classes_of_course(course_code)


# ---------- 课程看板总览 ----------
@router.get("/course")
async def course_dashboard(
    course_code: str = Depends(_cc),
    class_name: str | None = Depends(_class),
    sql: SqlRepository = Depends(get_sql),
):
    """② 课程看板：概况统计 + 学生分层分布 + 参与/成绩。"""
    stats = await sql.dashboard_stats(course_code, class_name)
    rows = await sql.kp_responses(course_code, class_name)
    mastery = CourseAnalytics(rows).tier_distribution()
    return {
        "course_code": course_code,
        "class_name": class_name,
        "stats": stats,
        "mastery": mastery,
    }


# ---------- 需关注学生（学业 / 态度 / 未测）----------
ACADEMIC_MASTERY_MAX = 0.5   # 掌握度低于此 → 学业预警
ATTITUDE_HW_MAX = 60         # 作业成绩低于此 → 学习态度预警（总不交/敷衍作业）


@router.get("/attention")
async def students_to_watch(
    course_code: str = Depends(_cc),
    class_name: str | None = Depends(_class),
    sql: SqlRepository = Depends(get_sql),
):
    """需关注学生，分三类：
    - academic 学业预警：有测验数据但平均掌握度低
    - attitude 学习态度：任务/作业完成率低（总不交）
    - untested 未测：没有逐题测验数据（不计入学业预警）
    """
    eng = await sql.student_engagement(course_code, class_name)
    rows = await sql.kp_responses(course_code, class_name)
    mastery = CourseAnalytics(rows).student_avg  # student_no -> 平均掌握度

    academic, attitude, untested = [], [], []
    for s in eng:
        if not s["tested"]:
            untested.append({
                "student_no": s["student_no"], "name": s["name"],
                "task_ratio": s["task_ratio"], "homework_score": s["homework_score"],
            })
        else:
            avg = mastery.get(s["student_no"])
            if avg is not None and avg < ACADEMIC_MASTERY_MAX:
                academic.append({
                    "student_no": s["student_no"], "name": s["name"],
                    "avg_mastery": round(avg, 3), "accuracy": s["accuracy"],
                })
        # 态度预警与是否测验无关：作业成绩过低 → 总不交/敷衍作业
        hw = s["homework_score"]
        if hw is not None and hw < ATTITUDE_HW_MAX:
            attitude.append({
                "student_no": s["student_no"], "name": s["name"],
                "homework_score": hw, "final_score": s["final_score"],
                "task_completed": s["task_completed"], "task_total": s["task_total"],
            })

    academic.sort(key=lambda x: x["avg_mastery"])
    attitude.sort(key=lambda x: x["homework_score"])
    return {
        "academic": academic,
        "attitude": attitude,
        "untested": untested,
        "counts": {
            "academic": len(academic),
            "attitude": len(attitude),
            "untested": len(untested),
            "total_enrolled": len(eng),
        },
    }


# ---------- 学生花名册（分层）----------
@router.get("/students")
async def student_roster(
    course_code: str = Depends(_cc),
    class_name: str | None = Depends(_class),
    sql: SqlRepository = Depends(get_sql),
):
    """全班花名册，每生带分层(优秀/达标/薄弱/未测)与学习态度标记。"""
    eng = await sql.student_engagement(course_code, class_name)
    rows = await sql.kp_responses(course_code, class_name)
    mastery = CourseAnalytics(rows).student_avg

    counts = {"excellent": 0, "on_track": 0, "weak": 0, "untested": 0, "attitude": 0}
    out = []
    for s in eng:
        avg = mastery.get(s["student_no"])
        if not s["tested"] or avg is None:
            tier = "untested"
        elif avg >= 0.7:
            tier = "excellent"
        elif avg >= 0.4:
            tier = "on_track"
        else:
            tier = "weak"
        hw = s["homework_score"]
        attitude = hw is not None and hw < ATTITUDE_HW_MAX
        counts[tier] += 1
        if attitude:
            counts["attitude"] += 1
        out.append({
            "student_no": s["student_no"],
            "name": s["name"],
            "class_name": s["class_name"],
            "tier": tier,
            "avg_mastery": round(avg, 3) if avg is not None else None,
            "accuracy": s["accuracy"],
            "homework_score": hw,
            "attitude": attitude,
        })

    order = {"weak": 0, "untested": 1, "on_track": 2, "excellent": 3}
    out.sort(key=lambda x: (order.get(x["tier"], 9), -(x["avg_mastery"] or 0)))
    return {"students": out, "counts": counts}


# ---------- 薄弱知识点排行 ----------
@router.get("/weak-knowledge-points")
async def weak_knowledge_points(
    course_code: str = Depends(_cc),
    class_name: str | None = Depends(_class),
    limit: int = 10,
    sql: SqlRepository = Depends(get_sql),
):
    """薄弱知识点 Top N（按全班平均掌握度升序）。"""
    rows = await sql.kp_responses(course_code, class_name)
    return CourseAnalytics(rows).weak_knowledge_points(limit)


# ---------- 高错题排行 ----------
@router.get("/high-error-questions")
async def high_error_questions(
    course_code: str = Depends(_cc),
    class_name: str | None = Depends(_class),
    limit: int = 10,
    sql: SqlRepository = Depends(get_sql),
):
    """高错题 Top N（按正确率升序）。"""
    stats = await sql.question_stats(course_code, class_name)
    q2kp = await sql.question_kp_map(course_code)
    labels = await sql.kp_labels(course_code)
    out = []
    for q in stats:
        total, correct = q["total"], q["correct"]
        kp_code = q2kp.get(q["question_id"])
        out.append({
            "question_id": q["question_id"],
            "seq_no": q["seq_no"],
            "stem": q["stem"],
            "type": q["type"],
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total, 3) if total else None,
            "error_rate": round(1 - correct / total, 3) if total else None,
            "kp_code": kp_code,
            "kp_label": labels.get(kp_code, {}).get("label") if kp_code else None,
        })
    out.sort(key=lambda x: (x["accuracy"] if x["accuracy"] is not None else 1.0))
    return out[:limit]


# ---------- 单题下钻（含干扰项分析）----------
@router.get("/question/{question_id}")
async def question_drilldown(
    question_id: str,
    course_code: str = Depends(_cc),
    class_name: str | None = Depends(_class),
    sql: SqlRepository = Depends(get_sql),
):
    """③ 题目下钻：题干/选项/正确答案 + 干扰项分布 + 答错学生。"""
    detail = await sql.question_detail(question_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="question not found")
    distribution = await sql.option_distribution(question_id, class_name)
    missed = await sql.students_missed_question(question_id, class_name)
    q2kp = await sql.question_kp_map(course_code)
    labels = await sql.kp_labels(course_code)
    kp_code = q2kp.get(question_id)
    total = sum(d["count"] for d in distribution)
    correct = sum(d["count"] for d in distribution if d["is_correct"])
    return {
        "detail": detail,
        "kp_code": kp_code,
        "kp_label": labels.get(kp_code, {}).get("label") if kp_code else None,
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 3) if total else None,
        "distribution": distribution,
        "missed_students": missed,
    }


# ---------- 知识点下钻 ----------
@router.get("/knowledge-point/{kp_code}")
async def knowledge_point_drilldown(
    kp_code: str,
    course_code: str = Depends(_cc),
    class_name: str | None = Depends(_class),
    sql: SqlRepository = Depends(get_sql),
):
    """④ 知识点下钻：平均掌握度/正确率 + 薄弱学生名单。"""
    label = await sql.kp_label(course_code, kp_code)
    if label is None:
        raise HTTPException(status_code=404, detail="knowledge point not found")
    rows = await sql.kp_responses(course_code, class_name)
    kp_entry = next(
        (k for k in CourseAnalytics(rows).knowledge_points() if k["kp_code"] == kp_code),
        None,
    )
    students = await sql.kp_student_accuracy(course_code, kp_code, class_name)
    out = []
    for s in students:
        total, correct = s["total"], s["correct"]
        out.append({
            "student_no": s["student_no"],
            "name": s["name"],
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total, 3) if total else None,
        })
    out.sort(key=lambda x: (x["accuracy"] if x["accuracy"] is not None else 1.0))
    return {
        "kp_code": kp_code,
        "label": label,
        "avg_mastery": kp_entry["avg_mastery"] if kp_entry else None,
        "tier": kp_entry["tier"] if kp_entry else None,
        "accuracy": kp_entry["accuracy"] if kp_entry else None,
        "students": out,
    }
