"""FastAPI dependencies for authentication, authorization, and workspace access."""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate the currently authenticated user."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
        
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Validate that current user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required"
        )
    return current_user


async def get_current_workspace(
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-Id"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Workspace:
    """Validate and return the active workspace for the user, ensuring tenant isolation."""
    if x_workspace_id:
        # Check membership
        query = select(Workspace).join(WorkspaceMember).filter(
            Workspace.id == x_workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
        result = await db.execute(query)
        workspace = result.scalars().first()
        if workspace:
            return workspace
        
        # If user is admin, allow access to workspace
        if current_user.role == "admin":
            result = await db.execute(select(Workspace).filter(Workspace.id == x_workspace_id))
            admin_ws = result.scalars().first()
            if admin_ws:
                return admin_ws
                
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to specified workspace denied or workspace not found"
        )
    
    # Otherwise fallback to user's first available or default workspace
    query = select(Workspace).join(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id
    ).order_by(Workspace.is_default.desc())
    
    result = await db.execute(query)
    workspace = result.scalars().first()
    
    if not workspace:
        # Create a default workspace for user if none exists
        default_ws = Workspace(
            name=f"{current_user.full_name}'s Workspace",
            description="Default personal enterprise workspace",
            is_default=True
        )
        db.add(default_ws)
        await db.flush()
        
        member = WorkspaceMember(
            workspace_id=default_ws.id,
            user_id=current_user.id,
            role="admin"
        )
        db.add(member)
        await db.commit()
        await db.refresh(default_ws)
        return default_ws
        
    return workspace
