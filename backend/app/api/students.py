"""学生与课程 API · Students & Courses API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_sql, get_gateway
from app.data_access import SqlRepository, EngineDataGateway

router = APIRouter(tags=["Students & Courses"])


class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    term_code: str | None = None


@router.get("/api/courses")
async def list_courses(sql: SqlRepository = Depends(get_sql)):
    """全部课程。"""
    return await sql.list_courses()


@router.post("/api/courses")
async def create_course(payload: CourseCreate, sql: SqlRepository = Depends(get_sql)):
    """新建（或按 code 更新名称）一门课程。"""
    return await sql.create_course(payload.course_code, payload.course_name, payload.term_code)


@router.get("/api/students")
async def list_students(gateway: EngineDataGateway = Depends(get_gateway)):
    """某课程下的学生（需 course_code）。"""
    return await gateway.get_students()
