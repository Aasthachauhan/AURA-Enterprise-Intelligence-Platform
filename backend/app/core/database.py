"""Database connection and session management."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables and seed default admin account."""
    import app.models  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Auto-seed default enterprise admin user and workspace if missing
    from app.core.security import hash_password
    from app.models.user import User
    from app.models.workspace import Organization, Workspace, WorkspaceMember
    from sqlalchemy.future import select

    async with AsyncSessionLocal() as session:
        admin_user = (await session.execute(select(User).filter(User.email == "admin@aura.enterprise"))).scalars().first()
        if not admin_user:
            admin_user = User(
                email="admin@aura.enterprise",
                full_name="AURA Enterprise Admin",
                hashed_password=hash_password("admin123"),
                role="admin",
                is_active=True
            )
            session.add(admin_user)
            await session.flush()
            
            org = Organization(name="AURA Enterprise", slug="aura-enterprise")
            session.add(org)
            await session.flush()
            
            ws = Workspace(
                organization_id=org.id,
                name="Primary Enterprise Workspace",
                description="Default intelligence workspace",
                is_default=True
            )
            session.add(ws)
            await session.flush()
            
            member = WorkspaceMember(workspace_id=ws.id, user_id=admin_user.id, role="admin")
            session.add(member)
            await session.commit()
