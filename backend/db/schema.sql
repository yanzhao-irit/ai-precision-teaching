-- =====================================================================
-- AI 精准教学系统 · 关系库建表脚本 (PostgreSQL)
-- Canonical DDL — 与 docs/data-schema.md 对应；docker-compose 首次启动自动加载。
-- All attribute names in English. 中英文说明见 docs/data-schema.md 数据字典。
-- =====================================================================

-- ---------- 枚举 · Enums ----------
CREATE TYPE assessment_type   AS ENUM ('homework','unit_test','exam','offline','major_project','chapter_task');
CREATE TYPE question_type     AS ENUM ('single_choice','multiple_choice','true_false','fill_blank','subjective');
CREATE TYPE submission_status AS ENUM ('completed','pending_review','not_submitted','late');
CREATE TYPE task_status       AS ENUM ('completed','not_completed','in_progress');
CREATE TYPE attendance_status AS ENUM ('present','absent','leave','teacher_signed','not_participated');
CREATE TYPE content_source    AS ENUM ('imported','ai_generated','manual');
CREATE TYPE review_status      AS ENUM ('approved','pending','rejected');

-- ---------- 身份与结构 · Identity & Structure ----------
CREATE TABLE teacher (
    teacher_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name    TEXT NOT NULL,
    email        TEXT UNIQUE
);

CREATE TABLE course (
    course_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_code      TEXT UNIQUE,
    course_name      TEXT NOT NULL,
    term_code        TEXT,
    teacher_id       BIGINT REFERENCES teacher(teacher_id),
    source_platform  TEXT,
    created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chapter (
    chapter_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id     BIGINT NOT NULL REFERENCES course(course_id),
    chapter_no    INT,
    title         TEXT NOT NULL,
    UNIQUE (course_id, chapter_no)
);

CREATE TABLE student (
    student_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_no     TEXT NOT NULL UNIQUE,
    external_uid   TEXT,
    full_name      TEXT,
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

-- ---------- 知识点登记表（桥）· Knowledge Point Registry (Bridge) ----------
CREATE TABLE concept (
    concept_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id     BIGINT NOT NULL REFERENCES course(course_id),
    concept_code  TEXT NOT NULL,
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
    kp_code         TEXT NOT NULL,
    label           TEXT NOT NULL,
    concept_id      BIGINT REFERENCES concept(concept_id),
    difficulty      SMALLINT,
    source          content_source NOT NULL DEFAULT 'imported',
    review_status   review_status  NOT NULL DEFAULT 'approved',
    generated_model TEXT,
    confidence      NUMERIC(4,3),
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE (course_id, kp_code)
);

-- ---------- 题目 · Questions ----------
CREATE TABLE assessment (
    assessment_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id       BIGINT NOT NULL REFERENCES course(course_id),
    chapter_id      BIGINT REFERENCES chapter(chapter_id),
    type            assessment_type NOT NULL,
    title           TEXT NOT NULL,
    max_score       NUMERIC(6,2),
    source_file     TEXT
);

CREATE TABLE question (
    question_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    assessment_id   BIGINT NOT NULL REFERENCES assessment(assessment_id),
    seq_no          INT,
    type            question_type NOT NULL,
    stem            TEXT NOT NULL,
    correct_answer  TEXT,
    explanation     TEXT,
    difficulty      SMALLINT,
    suggested_score NUMERIC(6,2),
    kp_status       review_status NOT NULL DEFAULT 'approved'
);

CREATE TABLE question_option (
    option_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question_id  BIGINT NOT NULL REFERENCES question(question_id),
    option_label CHAR(1) NOT NULL,
    option_text  TEXT NOT NULL,
    is_correct   BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (question_id, option_label)
);

CREATE TABLE question_knowledge_point (
    question_id   BIGINT NOT NULL REFERENCES question(question_id),
    kp_id         BIGINT NOT NULL REFERENCES knowledge_point(kp_id),
    weight        NUMERIC(4,3) DEFAULT 1.0,
    source        content_source NOT NULL DEFAULT 'imported',
    confidence    NUMERIC(4,3),
    review_status review_status  NOT NULL DEFAULT 'approved',
    PRIMARY KEY (question_id, kp_id)
);

CREATE TABLE kp_generation_log (
    log_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question_id   BIGINT REFERENCES question(question_id),
    model         TEXT,
    prompt        TEXT,
    raw_response  TEXT,
    produced_kp   TEXT,
    confidence    NUMERIC(4,3),
    created_at    TIMESTAMPTZ DEFAULT now(),
    reviewed_by   BIGINT REFERENCES teacher(teacher_id),
    review_result review_status DEFAULT 'pending'
);

-- ---------- 作答 · Responses ----------
CREATE TABLE submission (
    submission_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id  BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    assessment_id  BIGINT NOT NULL REFERENCES assessment(assessment_id),
    total_score    NUMERIC(6,2),
    status         submission_status NOT NULL DEFAULT 'completed',
    submitted_at   TIMESTAMPTZ,
    source_file    TEXT,
    UNIQUE (enrollment_id, assessment_id)
);

CREATE TABLE question_response (
    response_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    submission_id   BIGINT NOT NULL REFERENCES submission(submission_id),
    question_id     BIGINT NOT NULL REFERENCES question(question_id),
    student_answer  TEXT,
    answer_snapshot TEXT,
    is_correct      BOOLEAN,
    score           NUMERIC(6,2),
    answered_at     TIMESTAMPTZ,
    UNIQUE (submission_id, question_id)
);

-- ---------- 学习行为（聚合信号）· Engagement ----------
CREATE TABLE learning_resource (
    resource_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id       BIGINT NOT NULL REFERENCES course(course_id),
    chapter_id      BIGINT REFERENCES chapter(chapter_id),
    title           TEXT NOT NULL,
    resource_kind   TEXT,
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
    replay_ratio   NUMERIC(8,4),
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
    visit_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id     BIGINT NOT NULL REFERENCES course(course_id),
    activity_date DATE,
    total_views   INT,
    views_00_04   INT, views_04_08 INT, views_08_12 INT,
    views_12_16   INT, views_16_20 INT, views_20_24 INT
);

CREATE TABLE student_progress (
    progress_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id         BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    observed_at           TIMESTAMPTZ,
    task_completed_count  INT,
    task_total_count      INT,
    task_completion_ratio NUMERIC(6,4),
    video_watch_minutes   NUMERIC(10,4),
    discussion_count      INT,
    chapter_visit_count   INT,
    learning_status       TEXT
);

CREATE TABLE composite_grade (
    composite_grade_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id      BIGINT NOT NULL REFERENCES enrollment(enrollment_id),
    homework_score     NUMERIC(6,2),
    final_score        NUMERIC(6,2),
    computed_at        TIMESTAMPTZ DEFAULT now(),
    UNIQUE (enrollment_id)
);

-- ---------- Authentification · App Users ----------
CREATE TYPE user_role AS ENUM ('teacher', 'student');

CREATE TABLE app_user (
    user_id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    login                TEXT NOT NULL UNIQUE,
    password_hash        TEXT NOT NULL,
    role                 user_role NOT NULL DEFAULT 'student',
    student_id           BIGINT REFERENCES student(student_id),
    must_change_password BOOLEAN NOT NULL DEFAULT false,
    is_active            BOOLEAN NOT NULL DEFAULT true,
    created_at           TIMESTAMPTZ DEFAULT now(),
    last_login_at        TIMESTAMPTZ
);

CREATE INDEX idx_app_user_login    ON app_user(login);
CREATE INDEX idx_app_user_student  ON app_user(student_id);

-- ---------- 索引 · Indexes ----------
CREATE INDEX idx_qr_question       ON question_response(question_id);
CREATE INDEX idx_qr_correct        ON question_response(is_correct);
CREATE INDEX idx_qkp_kp            ON question_knowledge_point(kp_id);
CREATE INDEX idx_kp_concept        ON knowledge_point(concept_id);
CREATE INDEX idx_submission_assess ON submission(assessment_id);
CREATE INDEX idx_kp_review         ON knowledge_point(review_status);
CREATE INDEX idx_qkp_review        ON question_knowledge_point(review_status);
CREATE INDEX idx_question_assess   ON question(assessment_id);
CREATE INDEX idx_enrollment_course ON enrollment(course_id);
