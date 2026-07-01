"""FastAPI shared dependencies."""
from fastapi import Cookie, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.postgres_client import get_pg_session
from app.data_access import SqlRepository, GraphRepository, EngineDataGateway


async def _optional_driver():
    try:
        from app.core.neo4j_client import get_neo4j_driver
        return await get_neo4j_driver()
    except Exception:
        return None


async def get_sql(session: AsyncSession = Depends(get_pg_session)) -> SqlRepository:
    return SqlRepository(session)


async def get_gateway(
    course_code: str = Query(...),
    session: AsyncSession = Depends(get_pg_session),
) -> EngineDataGateway:
    driver = await _optional_driver()
    return EngineDataGateway(SqlRepository(session), GraphRepository(driver), course_code)


# ── Auth dependencies ────────────────────────────────────────────────────────

def _decode(token: str | None) -> dict:
    from jose import JWTError
    from app.core.auth import decode_token
    if not token:
        raise HTTPException(401, "Non authentifié")
    try:
        return decode_token(token)
    except JWTError:
        raise HTTPException(401, "Token invalide ou expiré")


async def get_current_user(apt_token: str | None = Cookie(default=None)) -> dict:
    return _decode(apt_token)


async def teacher_required(apt_token: str | None = Cookie(default=None)) -> dict:
    payload = _decode(apt_token)
    if payload.get("role") != "teacher":
        raise HTTPException(403, "Accès réservé aux enseignants")
    return payload


async def student_required(apt_token: str | None = Cookie(default=None)) -> dict:
    payload = _decode(apt_token)
    if payload.get("role") != "student":
        raise HTTPException(403, "Accès réservé aux étudiants")
    return payload
