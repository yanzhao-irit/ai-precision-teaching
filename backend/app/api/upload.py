"""
数据上传 API · Data upload
==========================
教师在首页上传三类原始文件，后端落盘后调用既有 ETL（data-pipeline/run_etl.py）入库：
  - question-bank   作业题库 .xls/.xlsx   -> run_etl questions
  - class-export    班级一键导出 .xlsx    -> run_etl class-export
  - student-answers 学生作业 zip(含 .doc) -> 解压 -> run_etl answers <dir>

复用子进程跑 ETL（与命令行同一套逻辑），cwd 设为 data-pipeline 以便 `import etl`。
"""
import asyncio
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router = APIRouter(prefix="/api/upload", tags=["Upload"])

# backend/app/api/upload.py -> 仓库根
REPO_ROOT = Path(__file__).resolve().parents[3]
PIPELINE_DIR = REPO_ROOT / "data-pipeline"
RUN_ETL = PIPELINE_DIR / "run_etl.py"


async def _run_etl(args: list[str]) -> str:
    if not RUN_ETL.exists():
        raise HTTPException(500, detail=f"run_etl.py 未找到：{RUN_ETL}")

    def _call():
        return subprocess.run(
            [sys.executable, str(RUN_ETL), *args],
            cwd=str(PIPELINE_DIR), capture_output=True, text=True,
        )

    proc = await asyncio.to_thread(_call)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "ETL 执行失败").strip()
        raise HTTPException(500, detail=detail[-2000:])
    return (proc.stdout or "").strip()


async def _save_temp(file: UploadFile, default_name: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="apt_upload_"))
    dest = tmp / (file.filename or default_name)
    dest.write_bytes(await file.read())
    return dest


@router.post("/question-bank")
async def upload_question_bank(
    course_code: str = Form(...),
    course_name: str | None = Form(None),
    file: UploadFile = File(...),
):
    """作业题库 .xls/.xlsx。"""
    path = await _save_temp(file, "qbank.xls")
    args = ["questions", str(path), "--course-code", course_code]
    if course_name:
        args += ["--course-name", course_name]
    return {"message": await _run_etl(args)}


@router.post("/class-export")
async def upload_class_export(
    course_code: str = Form(...),
    course_name: str | None = Form(None),
    file: UploadFile = File(...),
):
    """班级一键导出 .xlsx。"""
    path = await _save_temp(file, "class_export.xlsx")
    args = ["class-export", str(path), "--course-code", course_code]
    if course_name:
        args += ["--course-name", course_name]
    return {"message": await _run_etl(args)}


@router.post("/student-answers")
async def upload_student_answers(
    course_code: str = Form(...),
    file: UploadFile = File(...),
):
    """学生作业 zip（内含若干 .doc）。"""
    path = await _save_temp(file, "answers.zip")
    extract_dir = path.parent / "docs"
    extract_dir.mkdir(exist_ok=True)
    try:
        with zipfile.ZipFile(path) as z:
            z.extractall(extract_dir)
    except zipfile.BadZipFile:
        raise HTTPException(400, detail="不是有效的 zip 压缩包")
    docs = list(extract_dir.rglob("*.doc"))
    if not docs:
        raise HTTPException(400, detail="压缩包内未找到 .doc 文件")
    # run_etl answers 支持传目录；用解压根目录（递归交给 _iter 的目录遍历无效，故传含 .doc 的目录）
    target = docs[0].parent if len({d.parent for d in docs}) == 1 else extract_dir
    return {"message": await _run_etl(["answers", str(target), "--course-code", course_code])}
