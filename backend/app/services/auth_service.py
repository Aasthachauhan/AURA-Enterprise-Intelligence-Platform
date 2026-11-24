"""Authentication service implementing business logic for user management and tokens."""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.models.workspace import Organization, Workspace, WorkspaceMember
from app.models.audit import AuditLog
from app.schemas.auth import UserRegister, UserLogin, TokenResponse


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, data: UserRegister, ip_address: Optional[str] = None) -> TokenResponse:
        """Register a new user, create an organization and a default workspace."""
        # Check existing user
        result = await db.execute(select(User).filter(User.email == data.email.lower()))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists"
            )
        
        # First registered user is automatically admin
        user_count_res = await db.execute(select(User))
        is_first_user = len(user_count_res.scalars().all()) == 0
        assigned_role = "admin" if is_first_user else "member"
        
        # Create User
        new_user = User(
            email=data.email.lower(),
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=assigned_role,
            is_active=True,
            is_verified=True
        )
        db.add(new_user)
        await db.flush()
        
        # Create Organization
        org_name = data.organization_name or f"{data.full_name}'s Organization"
        org_slug = org_name.lower().replace(" ", "-") + f"-{new_user.id[:6]}"
        org = Organization(name=org_name, slug=org_slug)
        db.add(org)
        await db.flush()
        
        # Create Default Workspace
        workspace = Workspace(
            organization_id=org.id,
            name=f"{data.full_name}'s Workspace",
            description="Primary intelligence workspace",
            is_default=True
        )
        db.add(workspace)
        await db.flush()
        
        # Add Membership
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=new_user.id,
            role="admin"
        )
        db.add(member)
        
        # Audit Log
        audit = AuditLog(
            user_id=new_user.id,
            workspace_id=workspace.id,
            action="USER_REGISTER",
            resource_type="USER",
            resource_id=new_user.id,
            ip_address=ip_address,
            status="SUCCESS",
            details_json={"email": new_user.email, "role": assigned_role}
        )
        db.add(audit)
        
        await db.commit()
        await db.refresh(new_user)
        
        # Generate tokens
        token_payload = {"sub": new_user.id, "email": new_user.email, "role": new_user.role}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role,
                "active_workspace_id": workspace.id
            }
        )

    @staticmethod
    async def login(db: AsyncSession, data: UserLogin, ip_address: Optional[str] = None) -> TokenResponse:
        """Authenticate user and issue JWT credentials."""
        result = await db.execute(select(User).filter(User.email == data.email.lower()))
        user = result.scalars().first()
        
        if not user or not verify_password(data.password, user.hashed_password):
            audit = AuditLog(
                action="USER_LOGIN",
                resource_type="USER",
                ip_address=ip_address,
                status="FAILURE",
                details_json={"email": data.email, "reason": "Invalid credentials"}
            )
            db.add(audit)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Get active workspace
        ws_res = await db.execute(
            select(Workspace).join(WorkspaceMember).filter(WorkspaceMember.user_id == user.id).order_by(Workspace.is_default.desc())
        )
        workspace = ws_res.scalars().first()
        workspace_id = workspace.id if workspace else None
        
        # Audit Log
        audit = AuditLog(
            user_id=user.id,
            workspace_id=workspace_id,
            action="USER_LOGIN",
            resource_type="USER",
            resource_id=user.id,
            ip_address=ip_address,
            status="SUCCESS",
            details_json={"email": user.email}
        )
        db.add(audit)
        await db.commit()
        
        token_payload = {"sub": user.id, "email": user.email, "role": user.role}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "active_workspace_id": workspace_id
            }
        )

    @staticmethod
    async def refresh(db: AsyncSession, refresh_token: str) -> Dict[str, Any]:
        """Validate refresh token and issue new access token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        user_id = payload.get("sub")
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer active or valid"
            )
        
        token_payload = {"sub": user.id, "email": user.email, "role": user.role}
        new_access_token = create_access_token(token_payload)
        new_refresh_token = create_refresh_token(token_payload)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
