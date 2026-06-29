"""诊断 API · Diagnosis API（新数据层：EngineDataGateway）"""
from fastapi import APIRouter, Depends

from app.api.deps import get_gateway
from app.data_access import EngineDataGateway
from app.engines.diagnosis import DiagnosisEngine
from app.schemas import FullDiagnosisSchema

router = APIRouter(prefix="/api/diagnosis", tags=["Diagnosis"])


@router.get("/student/{student_no}", response_model=FullDiagnosisSchema)
async def diagnose_student(
    student_no: str,
    max_diagnoses: int = 100,
    gateway: EngineDataGateway = Depends(get_gateway),
):
    """诊断学生的所有错误（前置回溯 + BKT + 错因）。"""
    engine = DiagnosisEngine(gateway)
    return await engine.diagnose_student(student_no, max_diagnoses=max_diagnoses)


@router.get("/student/{student_no}/mastery")
async def get_mastery(
    student_no: str,
    gateway: EngineDataGateway = Depends(get_gateway),
):
    """按知识点的掌握度（BKT）。"""
    engine = DiagnosisEngine(gateway)
    return await engine.compute_mastery(student_no)
