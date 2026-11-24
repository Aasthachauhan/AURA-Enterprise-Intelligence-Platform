"""Chat API router with standard and SSE streaming endpoints."""
import json
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.chat import (
    ConversationCreate, ConversationUpdate, ConversationOut,
    MessageCreate, MessageOut, MessageFeedback
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Conversational AI Workspace"])


@router.post("/conversations", response_model=ConversationOut)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Start a new conversation workspace."""
    conv = await ChatService.create_conversation(
        db=db,
        workspace_id=workspace.id,
        user_id=current_user.id,
        title=data.title
    )
    return ConversationOut.model_validate(conv)


@router.get("/conversations", response_model=List[ConversationOut])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List all conversations in workspace."""
    conversations = await ChatService.list_conversations(
        db=db,
        workspace_id=workspace.id,
        user_id=current_user.id
    )
    return [ConversationOut.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Get single conversation and its full message history."""
    conv = await ChatService.get_conversation(db=db, conversation_id=conversation_id, workspace_id=workspace.id)
    return {
        "id": conv.id,
        "workspace_id": conv.workspace_id,
        "title": conv.title,
        "is_pinned": conv.is_pinned,
        "created_at": conv.created_at,
        "updated_at": conv.updated_at,
        "messages": [MessageOut.model_validate(m) for m in conv.messages]
    }


@router.patch("/conversations/{conversation_id}", response_model=ConversationOut)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Rename or pin conversation."""
    conv = await ChatService.update_conversation(
        db=db,
        conversation_id=conversation_id,
        workspace_id=workspace.id,
        title=data.title,
        is_pinned=data.is_pinned
    )
    return ConversationOut.model_validate(conv)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Delete conversation."""
    await ChatService.delete_conversation(db=db, conversation_id=conversation_id, workspace_id=workspace.id)
    return {"message": "Conversation deleted successfully"}


@router.post("/conversations/{conversation_id}/messages", response_model=MessageOut)
async def post_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Post message and run agentic RAG reasoning."""
    msg = await ChatService.process_message(
        db=db,
        conversation_id=conversation_id,
        user_message_text=data.content,
        workspace_id=workspace.id,
        user_id=current_user.id,
        selected_document_ids=data.selected_document_ids,
        use_agents=data.use_agents
    )
    return MessageOut.model_validate(msg)


@router.post("/conversations/{conversation_id}/stream")
async def post_message_stream(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Post message with Server-Sent Events (SSE) streaming updates."""
    async def sse_event_generator():
        # Yield agent progress steps
        yield f"data: {json.dumps({'type': 'step', 'agent': 'supervisor', 'status': 'Planning task execution...'})}\n\n"
        await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'type': 'step', 'agent': 'research', 'status': 'Retrieving grounded evidence from documents...'})}\n\n"
        await asyncio.sleep(0.1)

        msg = await ChatService.process_message(
            db=db,
            conversation_id=conversation_id,
            user_message_text=data.content,
            workspace_id=workspace.id,
            user_id=current_user.id,
            selected_document_ids=data.selected_document_ids,
            use_agents=data.use_agents
        )

        out_dict = MessageOut.model_validate(msg).model_dump(mode="json")
        yield f"data: {json.dumps({'type': 'complete', 'message': out_dict})}\n\n"

    return StreamingResponse(sse_event_generator(), media_type="text/event-stream")


@router.post("/messages/{message_id}/feedback", response_model=MessageOut)
async def submit_message_feedback(
    message_id: str,
    data: MessageFeedback,
    db: AsyncSession = Depends(get_db)
):
    """Submit thumbs up / thumbs down feedback on assistant message."""
    msg = await ChatService.submit_feedback(
        db=db,
        message_id=message_id,
        rating=data.rating,
        notes=data.notes
    )
    return MessageOut.model_validate(msg)
