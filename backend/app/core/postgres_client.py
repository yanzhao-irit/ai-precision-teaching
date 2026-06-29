"""
PostgreSQL Client
=================
Gestion de la connexion PostgreSQL via SQLAlchemy async.

Usage:
    from app.core.postgres_client import get_pg_session, Base
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# ── Moteur ────────────────────────────────────────────
engine = create_async_engine(
    settings.POSTGRES_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ── Session Factory ───────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ── Base Modèles ──────────────────────────────────────
class Base(DeclarativeBase):
    pass

# ── Helpers ───────────────────────────────────────────
async def init_postgres():
    """连接性检查。表由 schema.sql / Alembic 迁移管理，不在此 create_all。"""
    from sqlalchemy import text
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("✅ PostgreSQL connected")

async def close_postgres():
    """Ferme le pool de connexions."""
    await engine.dispose()
    logger.info("🔌 PostgreSQL déconnecté")

async def get_pg_session() -> AsyncSession:
    """Dependency FastAPI pour obtenir une session PostgreSQL."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
