# 目标数据库 Schema 设计 · Target Database Schema

> 配套架构图见对话。原则：所有属性名用英文；本文末尾附中英文数据字典。
> 关系库 = PostgreSQL（教学业务 + 题目 + 逐题作答 + 知识点登记表）；图库 = Neo4j（仅知识图谱）。
> 跨库桥 = 共享的 `kp_code`（知识点稳定 ID）。学生只存关系库。

约定 · Conventions
- 代理主键 `*_id` 用 `BIGINT GENERATED ALWAYS AS IDENTITY`。
- 自然键（如 `student_no` 学号、`kp_code` 知识点码、`concept_code` 概念码）单独建唯一索引，作为跨库/跨源对齐键。
- 时间统一 `TIMESTAMPTZ`；金额/分数 `NUMERIC`。
- 多课程隔离：所有内容/图谱表都带 `course_id`。
- 知识点缺失时由 LLM 生成 → `source='ai_generated'` + `review_status='pending'`，人工校对后转 `approved`（详见第二步落地方案）。

---

## 1. 关系库 PostgreSQL — DDL

```sql
-- ============ 枚举 · Enums ============
CREATE TYPE assessment_type   AS ENUM ('homework','unit_test','exam','offline','major_project','chapter_task');
CREATE TYPE question_type     AS ENUM ('single_choice','multiple_choice','true_false','fill_blank','subjective');
CREATE TYPE submission_status AS ENUM ('completed','pending_review','not_submitted','late');
CREATE TYPE task_status       AS ENUM ('completed','not_completed','in_progress');
CREATE TYPE attendance_status AS ENUM ('present','absent','leave','teacher_signed','not_participated');
CREATE TYPE content_source    AS ENUM ('imported','ai_generated','manual');
CREATE TYPE review_status      AS ENUM ('approved','pending','rejected');

-- ============ 身份与结构 · Identity & Structure ============
CREATE TABLE teacher (
    teacher_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name    TEXT NOT NULL,
    email        TEXT UNIQUE
);

CREATE TABLE course (
    course_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_code      TEXT UNIQUE,                 -- 跨课程隔离键 / 与图库 Course.course_code 对齐
    course_name      TEXT NOT NULL,
    term_code        TEXT,                         -- e.g. 2025-2026-1
    teacher_id       BIGINT REFERENCES teacher(teacher_id),
    source_platform  TEXT,                         -- 学习通 / 超星 等
    created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chapter (
    chapter_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id     BIGINT NOT NULL REFERENCES course(course_id),
    chapter_no    INT,                              -- 章序号
    title         TEXT NOT NULL,
    UNIQUE (course_id, chapter_no)
);

CREATE TABLE student (
    student_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_no    TEXT NOT NULL UNIQUE,             -- 学号：全系统唯一连接键
    external_uid  TEXT,                             -- 平台 UID（xlsx 里的 UID）
    full_name     TEXT,
    anonymous_code TEXT UNIQUE
);

CREATE TABLE enrollment (
    enrollment_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id      BIGINT NOT NULL REFERENCES student(student_id),
    course_id       BIGINT NOT NULL REFERENCES course(course_id),
    school_name     TEXT,
    department_name TEXT,
    major_name      TEXT,
    class_name      TEXT,
    admission_year  INT,
    UNIQUE (student_id, course_id)
);

-- ============ 知识点登记表（桥）· Knowledge Point Registry (Bridge) ============
-- 关系库的知识点主表；图库按 kp_code/concept_code 同步同一份 ID。
CREATE TABLE concept (
    concept_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id     BIGINT NOT NULL REFERENCES course(course_id),
    concept_code  TEXT NOT NULL,                    -- 与图库 Concept.concept_code 对齐
    label         TEXT NOT NULL,
    label_en      TEXT,
    chapter_id    BIGINT REFERENCES chapter(chapter_id),
    source        content_source NOT NULL DEFAULT 'manual',
    review_status review_status  NOT NULL DEFAULT 'approved',
    UNIQUE (course_id, concept_code)
);

CREATE TABLE knowledge_point (
    kp_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id       BIGINT NOT NULL REFERENCES course(course_id),
    kp_code         TEXT NOT NULL,                  -- 与图库 KnowledgePoint.kp_code 对齐（跨库桥）
    label           TEXT NOT NULL,                  -- 如“图灵测试的提出者”
    concept_id      BIGINT REFERENCES concept(concept_id),  -- 归属的粗概念
    difficulty      SMALLINT,                       -- 1..5
    source          content_source NOT NULL DEFAULT 'imported',
    review_status   review_status  NOT NULL DEFAULT 'approved',
    generated_model TEXT,                           -- 若 AI 生成，记录模型
    confidence      NUMERIC(4,3),                   -- AI 生成/映射置信度 0..1
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE (course_id, kp_code)
);

-- ============ 题目 · Questions ============
CREATE TABLE assessment (
    assessment_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id       BIGINT NOT NULL REFERENCES course(course_id),
    chapter_id      BIGINT REFERENCES chapter(chapter_id),
    type            assessment_type NOT NULL,
    title           TEXT NOT NULL,                  -- 如“第1章 单元测试”
    max_score       NUMERIC(6,2),
    source_file     TEXT
);

CREATE TABLE question (
    question_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    assessment_id   BIGINT NOT NULL REFERENCES assessment(assessment_id),
    seq_no          INT,                            -- 题号
    type            question_type NOT NULL,
    stem            TEXT NOT NULL,                  -- 题干
    correct_answer  TEXT,                           -- 正确答案，如 B / ABCD / √
    explanation     TEXT,                           -- 答案解析
    difficulty      SMALLINT,                       -- 1..5（易=1…难=5）
    suggested_score NUMERIC(6,2),                   -- 建议分数
    kp_status       review_status NOT NULL DEFAULT 'approved'  -- 题目知识点整体标注状态
);

CREATE TABLE question_option (
    option_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question_id  BIGINT NOT NULL REFERENCES question(question_id),
    option_label CHAR(1) NOT NULL,                  -- A/B/C/...
    option_text  TEXT NOT NULL,
    is_correct   BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (question_id, option_label)
);

-- 题目 ↔ 知识点（M:N）。映射本身也可能由 LLM 推断 → 带 source/confidence/review_status
CREATE TABLE question_knowledge_point (
    question_id   BIGINT NOT NULL REFERENCES question(question_id),
    kp_id         BIGINT NOT NULL REFERENCES knowledge_point(kp_id),
    weight        NUMERIC(4,3) DEFAULT 1.0,         -- 一题多知识点时的权重
    source        content_source NOT NULL DEFAULT 'imported',
    confidence    NUMERIC(4,3),
    review_status review_status  NOT NULL DEFAULT 'approved',
    PRIMARY KEY (question_id, kp_id)
);

-- LLM 生成知识点/映射的审计日志（支撑第二步）
CREATE TABLE kp_generation_log (
    log_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question_id   BIGINT REFERENCES question(question_id),
    model         TEXT,
    prompt        TEXT,
    raw_response  TEXT,
    produced_kp   TEXT,                             -- 模型产出的知识点标签
    confidence    NUMERIC(4,3),
    created_at    TIMESTAMPTZ DEFAULT now(),
    reviewed_by   BIGINT REFERENCES teacher(teacher_id),
    review_result review_status DEFAULT 'pending'
);

-- ============ 作答（逐题 + 整份）· Responses ============
CREATE TABLE submission (
    submission_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id  BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    assessment_id  BIGINT NOT NULL REFERENCES assessment(assessment_id),
    total_score    NUMERIC(6,2),
    status         submission_status NOT NULL DEFAULT 'completed',
    submitted_at   TIMESTAMPTZ,
    source_file    TEXT,                            -- 来源 doc 文件
    UNIQUE (enrollment_id, assessment_id)
);

CREATE TABLE question_response (
    response_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    submission_id  BIGINT NOT NULL REFERENCES submission(submission_id),
    question_id    BIGINT NOT NULL REFERENCES question(question_id),
    student_answer TEXT,                            -- 学生答案
    answer_snapshot TEXT,                           -- 正确答案快照（防题库变动）
    is_correct     BOOLEAN,                         -- 学生答案==正确答案
    score          NUMERIC(6,2),                    -- 题目得分
    answered_at    TIMESTAMPTZ,
    UNIQUE (submission_id, question_id)
);

-- ============ 学习行为（聚合信号）· Engagement (aggregate signals) ============
CREATE TABLE learning_resource (
    resource_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id       BIGINT NOT NULL REFERENCES course(course_id),
    chapter_id      BIGINT REFERENCES chapter(chapter_id),
    title           TEXT NOT NULL,
    resource_kind   TEXT,                            -- video / doc / task_point
    nominal_minutes NUMERIC(8,2)
);

CREATE TABLE task_completion (
    task_completion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id      BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    resource_id        BIGINT NOT NULL REFERENCES learning_resource(resource_id),
    status             task_status NOT NULL DEFAULT 'not_completed',
    completed_at       TIMESTAMPTZ
);

CREATE TABLE media_view (
    media_view_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id  BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    resource_id    BIGINT NOT NULL REFERENCES learning_resource(resource_id),
    watch_start_at TIMESTAMPTZ,
    watch_end_at   TIMESTAMPTZ,
    replay_ratio   NUMERIC(8,4),                     -- 反刍比
    watch_minutes  NUMERIC(10,4)
);

CREATE TABLE discussion_participation (
    discussion_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id      BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    observed_at        TIMESTAMPTZ,
    total_discussions  INT,
    posted_discussions INT,
    replies            INT,
    replied_topics     INT,
    likes_received     INT
);

CREATE TABLE attendance_session (
    session_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id     BIGINT NOT NULL REFERENCES course(course_id),
    session_label TEXT,
    session_date  DATE
);

CREATE TABLE attendance_record (
    attendance_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id    BIGINT NOT NULL REFERENCES attendance_session(session_id),
    enrollment_id BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    status        attendance_status,
    UNIQUE (session_id, enrollment_id)
);

CREATE TABLE chapter_visit_daily (
    visit_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id    BIGINT NOT NULL REFERENCES course(course_id),
    activity_date DATE,
    total_views  INT,
    views_00_04  INT, views_04_08 INT, views_08_12 INT,
    views_12_16  INT, views_16_20 INT, views_20_24 INT
);

CREATE TABLE student_progress (
    progress_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id        BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    observed_at          TIMESTAMPTZ,
    task_completed_count INT,
    task_total_count     INT,
    task_completion_ratio NUMERIC(6,4),
    video_watch_minutes  NUMERIC(10,4),
    discussion_count     INT,
    chapter_visit_count  INT,
    learning_status      TEXT
);

CREATE TABLE composite_grade (
    composite_grade_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id      BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    homework_score     NUMERIC(6,2),
    final_score        NUMERIC(6,2),
    computed_at        TIMESTAMPTZ DEFAULT now(),
    UNIQUE (enrollment_id)
);

-- ============ 关键索引 · Indexes ============
CREATE INDEX idx_qr_question         ON question_response(question_id);
CREATE INDEX idx_qr_correct          ON question_response(is_correct);
CREATE INDEX idx_qkp_kp              ON question_knowledge_point(kp_id);
CREATE INDEX idx_kp_concept          ON knowledge_point(concept_id);
CREATE INDEX idx_submission_assess   ON submission(assessment_id);
CREATE INDEX idx_kp_review           ON knowledge_point(review_status);
```

---

## 2. 图库 Neo4j — Schema

```cypher
// 约束（唯一键，按课程隔离用 course_code 属性区分）
CREATE CONSTRAINT course_code  IF NOT EXISTS FOR (c:Course)         REQUIRE c.course_code  IS UNIQUE;
CREATE CONSTRAINT concept_code IF NOT EXISTS FOR (c:Concept)        REQUIRE c.concept_code IS UNIQUE;
CREATE CONSTRAINT kp_code      IF NOT EXISTS FOR (k:KnowledgePoint) REQUIRE k.kp_code      IS UNIQUE;

// 节点 · Nodes
(:Course         {course_code, course_name, term_code})
(:Concept        {concept_code, course_code, label, label_en, chapter_no, difficulty})
(:KnowledgePoint {kp_code,      course_code, label, difficulty, source, review_status})
(:Misconception  {mc_code,      kp_code,     description})   // 可选：源自答案解析

// 关系 · Relationships
(:Course)-[:HAS_CONCEPT]->(:Concept)
(:Concept)-[:HAS_KNOWLEDGE_POINT]->(:KnowledgePoint)
(:Concept)-[:REQUIRES {source, confidence, review_status, explanation}]->(:Concept)  // 前置关系：LLM生成+人工校对
(:KnowledgePoint)-[:HAS_MISCONCEPTION]->(:Misconception)  // 可选
```

说明 · Notes
- 图库**不存学生、不存作答**。节点的 `kp_code` / `concept_code` 与关系库同名字段一一对齐，是唯一的跨库连接方式。
- `:REQUIRES` 边的 `source` 区分 `imported / ai_generated / manual`，`review_status` 标注是否已人工校对。
- `course_code` 作为属性挂在每个节点上，查询时 `WHERE n.course_code = $code` 即实现多课程隔离。

---

## 3. 数据字典（中英文）· Data Dictionary

### 关系库表 · Relational tables

| 表 Table | 中文 | English |
|---|---|---|
| teacher | 教师 | Teachers |
| course | 课程 | Courses |
| chapter | 章节 | Course chapters |
| student | 学生（全局唯一，以学号连接） | Students (global, keyed by student_no) |
| enrollment | 选课（学生×课程，含院系专业班级） | Enrollment (student×course, org info) |
| concept | 粗概念（图谱第一层，桥） | Coarse concepts (graph layer 1, bridge) |
| knowledge_point | 细知识点登记表（图谱第二层，桥） | Knowledge-point registry (graph layer 2, bridge) |
| assessment | 测评项（作业/测验/考试等） | Gradable assessments |
| question | 题目 | Questions |
| question_option | 选项 | Answer options |
| question_knowledge_point | 题目↔知识点映射（M:N） | Question–KP mapping |
| kp_generation_log | LLM 知识点生成审计日志 | LLM KP-generation audit log |
| submission | 整份提交（学生×测评） | Assessment submissions |
| question_response | 逐题作答（核心诊断数据） | Per-question responses (core) |
| learning_resource | 学习资源（视频/文档/任务点） | Learning resources |
| task_completion | 任务点完成 | Task-point completion |
| media_view | 音视频观看 | Audio/video views |
| discussion_participation | 讨论参与 | Discussion participation |
| attendance_session | 签到场次 | Attendance sessions |
| attendance_record | 签到记录 | Attendance records |
| chapter_visit_daily | 章节访问（按日/时段） | Daily chapter visits by time slot |
| student_progress | 学习进度快照 | Student progress snapshots |
| composite_grade | 综合成绩 | Composite grades |

### 关键字段 · Key columns

| 字段 Column | 所属表 | 中文 | English |
|---|---|---|---|
| student_no | student | 学号，全系统唯一连接键 | Student number; global join key |
| external_uid | student | 平台 UID（xlsx 中的 UID） | LMS platform UID |
| course_code | course | 课程隔离键，与图库对齐 | Course isolation key, aligns with graph |
| kp_code | knowledge_point | 知识点稳定码，**跨库桥** | Stable KP code, **cross-DB bridge** |
| concept_code | concept | 概念稳定码，与图库对齐 | Stable concept code, aligns with graph |
| source | concept / knowledge_point / question_knowledge_point | 来源：导入/AI生成/人工 | Origin: imported/ai_generated/manual |
| review_status | 同上 | 审核：通过/待审/驳回 | Review: approved/pending/rejected |
| generated_model | knowledge_point | AI 生成时所用模型 | Model used when AI-generated |
| confidence | knowledge_point / question_knowledge_point | 生成/映射置信度 0..1 | Generation/mapping confidence 0..1 |
| stem | question | 题干 | Question stem |
| correct_answer | question | 正确答案（B/ABCD/√） | Correct answer |
| explanation | question | 答案解析 | Answer explanation |
| difficulty | question / knowledge_point | 难度 1..5 | Difficulty 1..5 |
| student_answer | question_response | 学生答案 | Student's answer |
| answer_snapshot | question_response | 正确答案快照 | Snapshot of correct answer |
| is_correct | question_response | 是否答对 | Whether correct |
| score | question_response | 题目得分 | Score on this question |
| total_score | submission | 整份得分 | Total submission score |
| status | submission | 已完成/待批阅/未交/迟交 | completed/pending_review/not_submitted/late |
| replay_ratio | media_view | 反刍比（重复观看程度） | Replay ratio |
| watch_minutes | media_view | 观看分钟数 | Watched minutes |
| task_completion_ratio | student_progress | 任务点完成百分比 | Task completion ratio |
| learning_status | student_progress | 学习情况文本 | Learning status text |

### 枚举值 · Enums

| 枚举 Enum | 取值 Values | 含义 Meaning |
|---|---|---|
| assessment_type | homework / unit_test / exam / offline / major_project / chapter_task | 作业/单元测试/考试/线下/大作业/章节任务 |
| question_type | single_choice / multiple_choice / true_false / fill_blank / subjective | 单选/多选/判断/填空/主观 |
| submission_status | completed / pending_review / not_submitted / late | 已完成/待批阅/未提交/迟交 |
| task_status | completed / not_completed / in_progress | 已完成/未完成/进行中 |
| attendance_status | present / absent / leave / teacher_signed / not_participated | 已签/缺勤/请假/教师代签/未参与 |
| content_source | imported / ai_generated / manual | 导入/AI生成/人工 |
| review_status | approved / pending / rejected | 通过/待审/驳回 |

---

## 4. 设计要点回顾 · Design Highlights

1. **学生只在关系库**（`student`），图库无学生节点；学号 `student_no` 是全系统连接键。
2. **跨库桥 = `kp_code` / `concept_code`**：关系库 `knowledge_point` / `concept` 是主登记表，图库节点用同名码同步，靠共享码匹配，不做物理外键。
3. **逐题诊断数据**落在 `question_response`（来自 doc）；`submission` 存整份分数（doc 头 / xlsx）。
4. **知识点缺失可由 LLM 补全**：`knowledge_point.source='ai_generated'` + `review_status='pending'` + `generated_model` + `confidence`，并用 `kp_generation_log` 留痕，人工校对后转 `approved`。题目↔知识点映射同样支持 AI 推断与审核。
5. **行为/参与度**（视频/任务/讨论/签到/进度）只作聚合信号，喂画像与预警，不参与逐题错因诊断。
6. **多课程**：所有内容表与图谱节点带 `course_id` / `course_code`，天然隔离。
```
