"""预警 API · Early-Warning API"""
from fastapi import APIRouter, Depends

from app.api.deps import get_gateway
from app.data_access import EngineDataGateway
from app.engines.warning import WarningEngine

router = APIRouter(prefix="/api/warnings", tags=["Early Warning"])


@router.get("/watch-list")
async def watch_list(gateway: EngineDataGateway = Depends(get_gateway)):
    """需关注学生的风险名单（多信号）。"""
    return await WarningEngine(gateway).get_watch_list()
