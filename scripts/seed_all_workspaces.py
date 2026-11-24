"""Seed all available sample documents from datasets/ into all admin workspaces."""
import asyncio
import os
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.document import Document
from app.services.document_service import DocumentService
from fastapi import UploadFile

DATASET_FILES = [
    ("sample_enterprise_agreement.pdf", "datasets/sample_enterprise_agreement.pdf", "Legal"),
    ("sample_prd.docx", "datasets/sample_prd.docx", "Product"),
    ("sample_financials.xlsx", "datasets/sample_financials.xlsx", "Finance"),
    ("sample_test_coverage.csv", "datasets/sample_test_coverage.csv", "Engineering"),
    ("sample_contract.txt", "datasets/sample_contract.txt", "Legal"),
    ("sample_architecture.html", "datasets/sample_architecture.html", "Architecture"),
    ("sample_prd.md", "datasets/sample_prd.md", "Product"),
    ("sample_financials.csv", "datasets/sample_financials.csv", "Finance"),
]

class MockUploadFile:
    def __init__(self, filename: str, path: str):
        self.filename = filename
        self._path = path
    
    async def read(self) -> bytes:
        with open(self._path, "rb") as f:
            return f.read()

async def seed_all():
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).filter(User.email == "admin@aura.enterprise"))).scalars().first()
        if not user:
            print("Admin user not found!")
            return
        
        # Get all workspaces for admin
        memberships = (await db.execute(select(WorkspaceMember).filter(WorkspaceMember.user_id == user.id))).scalars().all()
        ws_ids = [m.workspace_id for m in memberships]
        workspaces = (await db.execute(select(Workspace).filter(Workspace.id.in_(ws_ids)))).scalars().all()
        
        print(f"Seeding documents for {len(workspaces)} workspaces of {user.email}:")
        for ws in workspaces:
            print(f"\n--- Workspace: {ws.name} ({ws.id}) ---")
            for filename, path, category in DATASET_FILES:
                if not os.path.exists(path):
                    print(f"Skipping {path} (not found)")
                    continue
                
                # Check if already in workspace
                existing = (await db.execute(select(Document).filter(
                    Document.workspace_id == ws.id,
                    Document.filename == filename
                ))).scalars().first()
                
                if existing and existing.status == "completed":
                    print(f"  [ALREADY INDEXED] {filename} (Chunks: {existing.chunk_count})")
                    continue
                
                mock_file = MockUploadFile(filename, path)
                try:
                    doc = await DocumentService.upload_document(
                        db=db,
                        file=mock_file,
                        workspace=ws,
                        user=user,
                        category=category
                    )
                    print(f"  [INDEXED OK] {filename} -> Doc ID: {doc.id}, Status: {doc.status}, Chunks: {doc.chunk_count}")
                except Exception as e:
                    print(f"  [ERROR] {filename}: {e}")

if __name__ == "__main__":
    asyncio.run(seed_all())
