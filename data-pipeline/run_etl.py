#!/usr/bin/env python
"""
ETL 命令行入口 · CLI
====================
前提：docker compose up -d 已起好 PostgreSQL（表由 schema.sql 建好）。

用法 · Usage:
  # 1) 题库（先做）—— 单文件或目录(*.xls)
  python run_etl.py questions "<file_or_dir>" --course-code AI-BASE-2025 --course-name 人工智能基础

  # 2) 学生答题（后做）—— 单文件或目录(*.doc)
  python run_etl.py answers "<file_or_dir>" --course-code AI-BASE-2025

  # 3) 班级一键导出
  python run_etl.py class-export "<xlsx>" --course-code AI-BASE-2025

连接信息从环境变量取（POSTGRES_HOST/PORT/DB/USER/PASSWORD），默认对齐 docker-compose。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from etl import db, load
from etl.parsers import parse_question_bank, parse_student_doc, parse_class_export


def _iter(path: str, suffixes: tuple[str, ...]) -> list[Path]:
    p = Path(path)
    if p.is_dir():
        return sorted(f for f in p.iterdir() if f.suffix.lower() in suffixes)
    return [p]


def cmd_questions(args):
    files = _iter(args.path, (".xls", ".xlsx"))
    with db.connect() as conn:
        cur = conn.cursor()
        for f in files:
            a = parse_question_bank(f, course_code=args.course_code,
                                    course_name=args.course_name,
                                    chapter_no=args.chapter, assessment_type=args.type)
            res = load.load_question_bank(cur, a)
            print(f"[题库] {f.name} -> {res}")


def cmd_answers(args):
    files = _iter(args.path, (".doc",))
    with db.connect() as conn:
        cur = conn.cursor()
        ok = skip = 0
        for f in files:
            s = parse_student_doc(f)
            res = load.load_student_submission(cur, s, course_code=args.course_code,
                                               course_name=args.course_name)
            if "skipped" in res:
                skip += 1
                print(f"[跳过] {f.name} -> {res['skipped']}")
            else:
                ok += 1
                print(f"[答题] {res['student_no']} ch{s.chapter_no} 逐题{res['responses']}"
                      f" 缺题{res['missing_questions']}")
        print(f"--- 完成：入库 {ok}，跳过 {skip} ---")


def cmd_class_export(args):
    with db.connect() as conn:
        cur = conn.cursor()
        c = parse_class_export(args.path, course_code=args.course_code)
        if args.course_name:
            c.course_name = args.course_name
        res = load.load_class_export(cur, c)
        print(f"[班级导出] {Path(args.path).name} -> {res}")


def main():
    ap = argparse.ArgumentParser(description="AI 精准教学 ETL")
    sub = ap.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("questions", help="题库 .xls 入库")
    q.add_argument("path"); q.add_argument("--course-code", required=True)
    q.add_argument("--course-name"); q.add_argument("--chapter", type=int)
    q.add_argument("--type", choices=["unit_test", "homework", "exam"])
    q.set_defaults(func=cmd_questions)

    a = sub.add_parser("answers", help="学生答题 .doc 入库")
    a.add_argument("path"); a.add_argument("--course-code", required=True)
    a.add_argument("--course-name")
    a.set_defaults(func=cmd_answers)

    c = sub.add_parser("class-export", help="班级一键导出 .xlsx 入库")
    c.add_argument("path"); c.add_argument("--course-code", required=True)
    c.add_argument("--course-name")
    c.set_defaults(func=cmd_class_export)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
