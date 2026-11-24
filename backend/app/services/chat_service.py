"""Conversational AI workspace service with multi-agent orchestration and streaming support."""
import json
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.models.workspace import Workspace
from app.models.agent import AgentRun
from app.rag.engine import rag_engine
from app.agents.graph import aura_agent_app


class ChatService:
    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        workspace_id: str,
        user_id: str,
        title: Optional[str] = "New Conversation"
    ) -> Conversation:
        """Create new conversation."""
        conv = Conversation(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title or "New Conversation"
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    @staticmethod
    async def list_conversations(
        db: AsyncSession,
        workspace_id: str,
        user_id: str
    ) -> List[Conversation]:
        """List user conversations in workspace."""
        res = await db.execute(
            select(Conversation)
            .filter(Conversation.workspace_id == workspace_id)
            .order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc())
        )
        conversations = res.scalars().all()
        for c in conversations:
            cnt_res = await db.execute(select(func.count(Message.id)).filter(Message.conversation_id == c.id))
            c.message_count = cnt_res.scalar() or 0
        return list(conversations)

    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        conversation_id: str,
        workspace_id: str
    ) -> Conversation:
        """Fetch conversation with all messages."""
        res = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .filter(Conversation.id == conversation_id, Conversation.workspace_id == workspace_id)
        )
        conv = res.scalars().first()
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        return conv

    @staticmethod
    async def update_conversation(
        db: AsyncSession,
        conversation_id: str,
        workspace_id: str,
        title: Optional[str] = None,
        is_pinned: Optional[bool] = None
    ) -> Conversation:
        """Update conversation properties."""
        conv = await ChatService.get_conversation(db, conversation_id, workspace_id)
        if title is not None:
            conv.title = title
        if is_pinned is not None:
            conv.is_pinned = is_pinned
        await db.commit()
        return conv

    @staticmethod
    async def delete_conversation(
        db: AsyncSession,
        conversation_id: str,
        workspace_id: str
    ) -> bool:
        """Delete conversation and cascade delete its messages."""
        conv = await ChatService.get_conversation(db, conversation_id, workspace_id)
        await db.delete(conv)
        await db.commit()
        return True

    @staticmethod
    async def process_message(
        db: AsyncSession,
        conversation_id: str,
        user_message_text: str,
        workspace_id: str,
        user_id: str,
        selected_document_ids: Optional[List[str]] = None,
        use_agents: bool = True
    ) -> Message:
        """Execute user message turn and generate assistant response."""
        # 1. Store User Message
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message_text,
            tokens_prompt=len(user_message_text.split()),
            total_tokens=len(user_message_text.split())
        )
        db.add(user_msg)
        await db.flush()

        start_time = time.time()
        agent_steps = []
        citations = []
        tool_calls = []

        if use_agents:
            # 2. Multi-Agent Orchestration via LangGraph
            initial_state = {
                "task_id": f"msg-{int(time.time())}",
                "workspace_id": workspace_id,
                "user_id": user_id,
                "query": user_message_text,
                "selected_document_ids": selected_document_ids,
                "plan_steps": [],
                "research_findings": [],
                "retrieved_chunks": [],
                "extracted_entities": [],
                "analytical_insights": [],
                "tool_calls": [],
                "requires_approval": False,
                "approval_prompt": None,
                "is_approved": None,
                "verification_passed": True,
                "citations": [],
                "final_response": None,
                "retry_count": 0,
                "max_retries": 1,
                "duration_ms": 0,
                "status": "pending",
                "error": None
            }

            output_state = await aura_agent_app.ainvoke(initial_state)

            final_text = output_state.get("final_response") or "Analysis completed."
            citations = output_state.get("citations", [])
            agent_steps = output_state.get("plan_steps", [])
            tool_calls = output_state.get("tool_calls", [])

            # Persist AgentRun record
            agent_run = AgentRun(
                workspace_id=workspace_id,
                conversation_id=conversation_id,
                user_id=user_id,
                agent_type="supervisor",
                status="completed",
                input_payload={"query": user_message_text},
                output_payload={"response": final_text[:300]},
                plan_steps=agent_steps,
                duration_ms=int((time.time() - start_time) * 1000)
            )
            db.add(agent_run)

        else:
            # 3. Direct Grounded RAG Query
            rag_output = await rag_engine.answer_query(
                db=db,
                query=user_message_text,
                workspace_id=workspace_id,
                filter_document_ids=selected_document_ids,
                top_k=5
            )
            final_text = rag_output["answer"]
            citations = rag_output["citations"]

        latency_ms = int((time.time() - start_time) * 1000)
        prompt_tokens = len(user_message_text.split()) + 300
        comp_tokens = len(final_text.split())

        # 4. Store Assistant Message
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=final_text,
            citations_json=citations,
            agent_steps_json=agent_steps,
            tool_calls_json=tool_calls,
            tokens_prompt=prompt_tokens,
            tokens_completion=comp_tokens,
            total_tokens=prompt_tokens + comp_tokens,
            latency_ms=latency_ms
        )
        db.add(assistant_msg)

        # Update conversation timestamp & auto-title if first message
        conv = await db.get(Conversation, conversation_id)
        if conv and conv.title == "New Conversation":
            # Set title to first 5 words of query
            conv.title = " ".join(user_message_text.split()[:5])

        await db.commit()
        await db.refresh(assistant_msg)
        return assistant_msg

    @staticmethod
    async def submit_feedback(
        db: AsyncSession,
        message_id: str,
        rating: int,
        notes: Optional[str] = None
    ) -> Message:
        """Submit user feedback rating for assistant message."""
        msg = await db.get(Message, message_id)
        if not msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        msg.feedback_rating = rating
        msg.feedback_notes = notes
        await db.commit()
        await db.refresh(msg)
        return msg
