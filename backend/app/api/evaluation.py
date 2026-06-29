"""评估与班级分析 API · Evaluation & Class Analytics API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_gateway
from app.data_access import EngineDataGateway
from app.engines.evaluation import EvaluationEngine

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation & Analytics"])


@router.get("/overview")
async def overview(gateway: EngineDataGateway = Depends(get_gateway)):
    return await EvaluationEngine(gateway).class_overview()


@router.get("/heatmap")
async def heatmap(gateway: EngineDataGateway = Depends(get_gateway)):
    return await EvaluationEngine(gateway).class_mastery_heatmap()


@router.get("/tier-distribution")
async def tier_distribution(gateway: EngineDataGateway = Depends(get_gateway)):
    return await EvaluationEngine(gateway).tier_distribution()


@router.get("/top-root-causes")
async def top_root_causes(limit: int = 5, gateway: EngineDataGateway = Depends(get_gateway)):
    return await EvaluationEngine(gateway).top_root_causes(limit)


@router.get("/top-error-concepts")
async def top_error_concepts(limit: int = 5, gateway: EngineDataGateway = Depends(get_gateway)):
    return await EvaluationEngine(gateway).top_error_concepts(limit)


class PrePostInput(BaseModel):
    pre_scores: list[float]
    post_scores: list[float]


@router.post("/pre-post")
def pre_post(data: PrePostInput, gateway: EngineDataGateway = Depends(get_gateway)):
    """前后测配对 t 检验 + 效应量（需 scipy）。"""
    return EvaluationEngine(gateway).pre_post_comparison(data.pre_scores, data.post_scores)
