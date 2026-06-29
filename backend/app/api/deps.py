"""FastAPI 共享依赖 · shared dependencies（新数据层）。"""
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.postgres_client import get_pg_session
from app.data_access import SqlRepository, GraphRepository, EngineDataGateway


async def _optional_driver():
    """图库不可用时返回 None，引擎降级为无前置回溯。"""
    try:
        from app.core.neo4j_client import get_neo4j_driver
        return await get_neo4j_driver()
    except Exception:
        return None


async def get_sql(session: AsyncSession = Depends(get_pg_session)) -> SqlRepository:
    return SqlRepository(session)


async def get_gateway(
    course_code: str = Query(..., description="课程码，如 AI-BASE-2025"),
    session: AsyncSession = Depends(get_pg_session),
) -> EngineDataGateway:
    driver = await _optional_driver()
    return EngineDataGateway(SqlRepository(session), GraphRepository(driver), course_code)
