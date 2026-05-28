from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from .config import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a read‑only DB session for normal operations."""
    async with AsyncSessionLocal() as session:
        yield session

# Audit DB (separate credentials)
engine_audit = create_async_engine(settings.AUDIT_DATABASE_URL, echo=False, future=True)
AsyncAuditSessionLocal = async_sessionmaker(bind=engine_audit, class_=AsyncSession, expire_on_commit=False)

async def get_audit_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a read‑only session for audit logging purposes."""
    async with AsyncAuditSessionLocal() as session:
        yield session
