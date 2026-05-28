from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from ..config import get_settings
from .models import metadata, get_metadata

settings = get_settings()

# Primary application engine (read‑only role appuser will use this URL)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    echo=False,
    future=True,
)

# Audit engine (audituser role)
audit_engine = create_async_engine(
    settings.AUDIT_DATABASE_URL,
    pool_size=2,
    max_overflow=5,
    echo=False,
    future=True,
)

# Session makers
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
AuditAsyncSessionLocal = async_sessionmaker(bind=audit_engine, class_=AsyncSession, expire_on_commit=False)

# Helper to run DDL and role creation
async def init_db():
    """Create tables and required PostgreSQL roles/grants.
    This function is idempotent – it will not fail if tables or roles already exist.
    """
    # Create tables in the primary DB (metadata includes all tables)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
        # ---- Role creation (appuser) ----
        await conn.execute(
            text(
                f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{settings.POSTGRES_USER}') THEN "
                f"CREATE ROLE {settings.POSTGRES_USER} WITH LOGIN PASSWORD '{settings.POSTGRES_PASSWORD}'; "
                f"END IF; END $$;"
            )
        )
        # Grant SELECT on all tables to appuser
        await conn.execute(
            text(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {settings.POSTGRES_USER};")
        )
        # ---- Role creation (audituser) ----
        await conn.execute(
            text(
                f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{settings.AUDIT_USER}') THEN "
                f"CREATE ROLE {settings.AUDIT_USER} WITH LOGIN PASSWORD '{settings.AUDIT_PASSWORD}'; "
                f"END IF; END $$;"
            )
        )
        # Grant INSERT on audit_log only to audituser
        await conn.execute(
            text(f"GRANT INSERT ON audit_log TO {settings.AUDIT_USER};")
        )

async def close_db():
    """Dispose both async engines."""
    await engine.dispose()
    await audit_engine.dispose()

async def check_db_connection() -> bool:
    """Return True if a simple SELECT 1 succeeds, else False."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            _ = result.scalar_one()
        return True
    except Exception:
        return False
