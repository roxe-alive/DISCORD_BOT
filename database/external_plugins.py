import asyncpg
import os
from config import Config



pool = None

_DDL_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS external_plugins (
    plugin_name TEXT PRIMARY KEY,
    file_name   TEXT NOT NULL,
    gist_url    TEXT NOT NULL,
    installed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

async def _ensure_schema(conn: asyncpg.Connection) -> None:
    """Create required tables if they do not exist."""
    await conn.execute(_DDL_CREATE_TABLE)


async def init_db():
    """Initialize a global connection pool and ensure schema exists."""
    global pool
    if pool is None:
        if not Config.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not configured in environment/config.env")
        pool = await asyncpg.create_pool(Config.DATABASE_URL)
        # Ensure schema once when pool is first created
        async with pool.acquire() as conn:
            await _ensure_schema(conn)
    return pool


async def add(plugin_name: str, file_name: str, gist_url: str):
    """Add plugin metadata to PostgreSQL."""
    await init_db()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO external_plugins (plugin_name, file_name, gist_url)
            VALUES ($1, $2, $3)
            ON CONFLICT (plugin_name) DO NOTHING;
        """, plugin_name, file_name, gist_url)


async def remove(plugin_name: str):
    """Remove a plugin by name."""
    await init_db()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM external_plugins WHERE plugin_name = $1;",
            plugin_name
        )


async def get_all():
    """Get all saved plugins."""
    await init_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM external_plugins;")
    return rows
