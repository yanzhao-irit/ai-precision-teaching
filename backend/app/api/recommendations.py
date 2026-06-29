"""推荐 API · Recommendation API"""
from typing import Optional

from fastapi import APIRouter, Depends

from app.api.deps import get_gateway
from app.data_access import EngineDataGateway
from app.engines.recommendation import RecommendationEngine

router = APIRouter(prefix="/api/recommendations", tags=["Recommendation"])


@router.get("/student/{student_no}")
async def recommend_for_student(
    student_no: str,
    max_items: int = 15,
    learning_style: Optional[str] = None,
    gateway: EngineDataGateway = Depends(get_gateway),
):
    """三路径推荐（补救/巩固/拓展）。资源需按知识点打标签后才有内容。"""
    return await RecommendationEngine(gateway).recommend_for_student(
        student_no, max_items=max_items, learning_style=learning_style
    )
