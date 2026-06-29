"""画像 API · Profiles API"""
from fastapi import APIRouter, Depends

from app.api.deps import get_gateway
from app.data_access import EngineDataGateway
from app.engines.profile import ProfileEngine

router = APIRouter(prefix="/api/profiles", tags=["Profiles"])


@router.get("/student/{student_no}")
async def get_profile(student_no: str, gateway: EngineDataGateway = Depends(get_gateway)):
    """学生三维画像（知识/行为/认知）+ 分层。"""
    return await ProfileEngine(gateway).build_profile(student_no)


@router.get("/")
async def all_profiles(gateway: EngineDataGateway = Depends(get_gateway)):
    """全班学生画像。"""
    return await ProfileEngine(gateway).build_all_profiles()
