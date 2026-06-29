"""
ETL 解析器 · Parsers (纯函数，不依赖数据库)
================================================
把三类导出文件解析成结构化 dataclass，便于脱库单测。
入库逻辑见 load.py。

- parse_question_bank: 题库 .xls          -> ParsedAssessment(题目+选项+知识点)
- parse_student_doc:   学生答题 .doc       -> ParsedSubmission(逐题作答)
- parse_class_export:  班级一键导出 .xlsx  -> ParsedClassExport(学生/选课/成绩/行为)
"""
from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")

# ---------- 映射表 · Mappings ----------
QUESTION_TYPE = {
    "单选题": "single_choice",
    "多选题": "multiple_choice",
    "判断题": "true_false",
    "填空题": "fill_blank",
}
DIFFICULTY = {"易": 1, "中": 3, "难": 5}
TASK_STATUS = {"已完成": "completed", "未完成": "not_completed", "进行中": "in_progress"}
SUBMISSION_STATUS = {"已完成": "completed", "待批阅": "pending_review",
                     "未完成": "not_submitted", "未提交": "not_submitted", "迟交": "late"}
ATTENDANCE = {"已签": "present", "缺勤": "absent", "请假": "leave",
              "教师代签": "teacher_signed", "未参与": "not_participated"}


# ============================================================
# 数据结构 · Dataclasses
# ============================================================
@dataclass
class ParsedOption:
    label: str
    text: str
    is_correct: bool


@dataclass
class ParsedQuestion:
    seq_no: int
    type: str
    stem: str
    correct_answer: Optional[str]
    explanation: Optional[str]
    difficulty: Optional[int]
    suggested_score: Optional[float]
    knowledge_point: Optional[str]       # 题库“知识点”列；缺失→None→交 LLM
    options: list[ParsedOption] = field(default_factory=list)


@dataclass
class ParsedAssessment:
    course_code: str
    course_name: Optional[str]
    chapter_no: Optional[int]
    assessment_type: str
    title: str
    source_file: str
    questions: list[ParsedQuestion] = field(default_factory=list)


@dataclass
class ParsedResponse:
    seq_no: int
    student_answer: Optional[str]
    correct_answer: Optional[str]
    is_correct: Optional[bool]
    score: Optional[float]


@dataclass
class ParsedSubmission:
    student_no: Optional[str]
    student_name: Optional[str]
    class_name: Optional[str]
    title: str                # 测评标题（用于匹配 assessment）
    chapter_no: Optional[int]
    total_score: Optional[float]
    submitted_at: Optional[str]
    source_file: str
    responses: list[ParsedResponse] = field(default_factory=list)


# ============================================================
# 工具 · Helpers
# ============================================================
def _clean(v) -> Optional[str]:
    if v is None:
        return None
    s = str(v).replace("&nbsp;", " ").strip()
    if s.lower() in ("nan", "none", "nat"):   # pandas 空值被 str() 成 "nan"
        return None
    return s or None


def _chapter_no_from(name: str) -> Optional[int]:
    m = re.search(r"第\s*(\d+)\s*章", name) or re.search(r"章节\s*(\d+)", name)
    return int(m.group(1)) if m else None


def _assessment_type_from(name: str) -> str:
    if "单元测试" in name or "测验" in name:
        return "unit_test"
    if "作业" in name:
        return "homework"
    if "考试" in name:
        return "exam"
    return "unit_test"


def _norm_answer(ans: Optional[str], qtype: str) -> Optional[str]:
    """归一化用于对错判定：选择题排序去空格大写；判断题 √/正确→T，×/错误→F。"""
    if not ans:
        return None
    a = ans.strip()
    if qtype == "true_false" or a in ("√", "×", "对", "错", "正确", "错误"):
        if a in ("√", "对", "正确", "A", "T", "true", "True"):
            return "T"
        if a in ("×", "错", "错误", "B", "F", "false", "False"):
            return "F"
    return "".join(sorted(a.upper().replace(" ", "")))


# ============================================================
# 1) 题库 .xls
# ============================================================
def parse_question_bank(
    path: str | Path,
    course_code: str,
    course_name: Optional[str] = None,
    chapter_no: Optional[int] = None,
    assessment_type: Optional[str] = None,
    title: Optional[str] = None,
) -> ParsedAssessment:
    import pandas as pd

    path = Path(path)
    name = path.stem
    df = pd.read_excel(path, header=None)          # xlrd 处理 .xls
    header = [(_clean(x) or "") for x in df.iloc[0].tolist()]
    # 列定位（容错：按表头名找；找不到回退到默认列序）
    def col(label, default):
        for i, h in enumerate(header):
            if h == label:
                return i
        return default

    c_type, c_stem, c_ans = col("题目类型", 1), col("大题题干", 3), col("正确答案", 6)
    c_expl, c_diff, c_kp = col("答案解析", 7), col("难易度", 8), col("知识点", 9)
    c_score, c_optn, c_opt0 = col("建议分数", 10), col("选项数", 11), col("选项A", 12)

    assessment = ParsedAssessment(
        course_code=course_code,
        course_name=course_name,
        chapter_no=chapter_no if chapter_no is not None else _chapter_no_from(name),
        assessment_type=assessment_type or _assessment_type_from(name),
        title=title or name,
        source_file=path.name,
    )

    seq = 0
    for idx in range(1, df.shape[0]):
        row = df.iloc[idx]
        qtype_cn = _clean(row[c_type])
        stem = _clean(row[c_stem])
        if not qtype_cn or not stem:
            continue
        seq += 1
        qtype = QUESTION_TYPE.get(qtype_cn, "subjective")
        opt_count = int(row[c_optn]) if str(row[c_optn]).strip().isdigit() else 0
        options = []
        for i in range(opt_count):
            txt = _clean(row[c_opt0 + i]) if (c_opt0 + i) < df.shape[1] else None
            if txt is None:
                continue
            label = chr(ord("A") + i)
            options.append(ParsedOption(label=label, text=txt, is_correct=False))
        correct = _clean(row[c_ans])
        # 标记正确选项
        if correct:
            correct_letters = set(re.findall(r"[A-Z]", correct.upper()))
            for o in options:
                o.is_correct = o.label in correct_letters
        diff = DIFFICULTY.get(_clean(row[c_diff]) or "", None)
        score = None
        try:
            score = float(row[c_score])
        except (TypeError, ValueError):
            pass
        assessment.questions.append(ParsedQuestion(
            seq_no=seq, type=qtype, stem=stem, correct_answer=correct,
            explanation=_clean(row[c_expl]), difficulty=diff,
            suggested_score=score, knowledge_point=_clean(row[c_kp]), options=options,
        ))
    return assessment


# ============================================================
# 2) 学生答题 .doc  (Word 2003 XML, UTF-8)
# ============================================================
def parse_student_doc(path: str | Path) -> ParsedSubmission:
    path = Path(path)
    raw = path.read_text(encoding="utf-8", errors="replace")
    # 题目靠 <w:p> 段落分隔：每段提取其 <w:t> 文本拼成一行
    lines = []
    for para in re.split(r"<w:p[ >]", raw):
        texts = re.findall(r"<w:t[^>]*>(.*?)</w:t>", para, re.S)
        if not texts:
            continue
        line = "".join(texts)
        for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&nbsp;", " ")):
            line = line.replace(a, b)
        line = line.strip()
        if line:
            lines.append(line)

    # 文件名：学院-专业-班级-学号-姓名.doc
    parts = path.stem.split("-")
    student_no = parts[-2].strip() if len(parts) >= 2 else None
    student_name = parts[-1].strip() if len(parts) >= 1 else None
    class_name = parts[2].strip() if len(parts) >= 3 else None

    full = "\n".join(lines)
    total = re.search(r"作业得分[:：]\s*([\d.]+)", full)
    submitted = re.search(r"提交时间[:：]\s*([\d\-]+\s+[\d:]+)", full)
    name_in_doc = re.search(r"答题人[:：]\s*([^\s]+)", full)
    if name_in_doc:
        student_name = name_in_doc.group(1)

    sub = ParsedSubmission(
        student_no=student_no, student_name=student_name, class_name=class_name,
        # 章节号优先从正文标题（含“第N章…【单元测试】”）取，文件名兜底
        title=path.stem, chapter_no=_chapter_no_from(full) or _chapter_no_from(path.stem),
        total_score=float(total.group(1)) if total else None,
        submitted_at=submitted.group(1) if submitted else None,
        source_file=path.name,
    )

    # 按题切块
    q_re = re.compile(r"^(\d+)\.")
    cur = None
    cur_type = "single_choice"
    for ln in lines:
        m = q_re.match(ln)
        if m:
            if cur is not None:
                sub.responses.append(cur)
            cur = ParsedResponse(seq_no=int(m.group(1)), student_answer=None,
                                 correct_answer=None, is_correct=None, score=None)
            cur_type = "single_choice"
            continue
        if cur is None:
            continue
        if re.match(r"^[A-Z]、", ln):
            cur_type = "single_choice"  # 有字母选项→选择题
        sa = re.search(r"学生答案[:：]\s*([^\s正]+)", ln)
        ca = re.search(r"正确答案[:：]\s*(\S+)", ln)
        sc = re.search(r"题目得分[:：]\s*([\d.]+)", ln)
        if "√" in ln or "×" in ln:
            cur_type = "true_false"
            pair = re.findall(r"[√×]", ln)
            if len(pair) >= 2:
                cur.student_answer, cur.correct_answer = pair[0], pair[1]
        if sa:
            cur.student_answer = sa.group(1)
        if ca:
            cur.correct_answer = ca.group(1)
        if sc:
            cur.score = float(sc.group(1))
        if cur.student_answer and cur.correct_answer:
            cur.is_correct = (_norm_answer(cur.student_answer, cur_type)
                              == _norm_answer(cur.correct_answer, cur_type))
    if cur is not None:
        sub.responses.append(cur)
    return sub


# ============================================================
# 3) 班级一键导出 .xlsx  (13 sheet)
# ============================================================
@dataclass
class ParsedStudent:
    student_no: str
    external_uid: Optional[str]
    full_name: Optional[str]
    school: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    class_name: Optional[str] = None
    admission_year: Optional[int] = None


@dataclass
class ParsedClassExport:
    course_code: str
    course_name: Optional[str]
    students: list[ParsedStudent] = field(default_factory=list)
    progress: list[dict] = field(default_factory=list)        # student_no -> 指标
    homework: list[dict] = field(default_factory=list)        # 每生每章作业成绩
    unit_tests: list[dict] = field(default_factory=list)      # 每生每章测验成绩
    composite: list[dict] = field(default_factory=list)       # 综合成绩


def parse_class_export(path: str | Path, course_code: str) -> ParsedClassExport:
    import pandas as pd

    path = Path(path)
    xls = pd.ExcelFile(path)
    out = ParsedClassExport(course_code=course_code, course_name="人工智能基础")

    def sheet(name):
        return pd.read_excel(xls, name, header=None) if name in xls.sheet_names else None

    # --- 学生学习进度详情：UID/学号/姓名/院系专业班级 + 进度指标（表头在第3行=idx2）---
    sp = sheet("学生学习进度详情")
    if sp is not None:
        for i in range(3, sp.shape[0]):
            r = sp.iloc[i]
            sno = _clean(r[2])
            if not sno:
                continue
            out.students.append(ParsedStudent(
                student_no=sno, external_uid=_clean(r[0]), full_name=_clean(r[1]),
                school=_clean(r[3]), department=_clean(r[4]), major=_clean(r[5]),
                class_name=_clean(r[6]),
                admission_year=int(r[7]) if str(r[7]).strip().isdigit() else None,
            ))
            done, total = (str(r[8]).split("/") + ["", ""])[:2]
            out.progress.append({
                "student_no": sno,
                "task_completed_count": int(done) if done.strip().isdigit() else None,
                "task_total_count": int(total) if total.strip().isdigit() else None,
                "discussion_count": int(r[11]) if str(r[11]).strip().isdigit() else None,
                "chapter_visit_count": int(r[12]) if str(r[12]).strip().isdigit() else None,
                "learning_status": _clean(r[13]),
            })

    # --- 综合成绩：序号/姓名/学号/.../作业(100%)/综合成绩 ---
    cg = sheet("综合成绩")
    if cg is not None:
        for i in range(3, cg.shape[0]):
            r = cg.iloc[i]
            sno = _clean(r[2])
            if not sno:
                continue
            def num(x):
                try:
                    return float(x)
                except (TypeError, ValueError):
                    return None
            out.composite.append({"student_no": sno,
                                  "homework_score": num(r[7]), "final_score": num(r[8])})
    return out
