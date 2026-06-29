"""
Neo4j 客户端单例 · Neo4j Client Singleton
=========================================
封装连接池管理，应用启动时初始化，关闭时释放。
Wraps connection pool management — initialise on startup, release on shutdown.

用法 · Usage:
    from app.core.neo4j_client import get_neo4j_driver
    async with get_neo4j_driver() as session:
        result = await session.run("MATCH (n) RETURN n")
"""

from neo4j import AsyncGraphDatabase, Driver
from app.core.config import settings

_driver: Driver | None = None


async def get_neo4j_driver() -> Driver:
    """
    获取 Neo4j 异步驱动（单例）。
    Get the Neo4j async driver (singleton).
    """
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        # 验证连接 · Verify connection
        await _driver.verify_connectivity()
    return _driver


async def close_neo4j_driver() -> None:
    """应用关闭时释放连接池 · Release connection pool on app shutdown."""
    global _driver
    if _driver:
        await _driver.close()
        _driver = None