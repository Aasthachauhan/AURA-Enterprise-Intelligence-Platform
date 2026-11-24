# AURA Developer & Contributor Guide

## 1. Development Environment Setup

### 1.1 Prerequisites
- **Python**: Version 3.11 or higher.
- **Node.js**: Version 18 LTS or 20 LTS.
- **Package Managers**: `pip` (Python) and `npm` (Node).
- **Git**: For version control.
- **Operating System**: Windows (PowerShell), macOS (zsh), or Linux (bash).

---

## 2. Local Setup Instructions

### 2.1 Backend Setup

```bash
# 1. Navigate to the project root
cd "AURA -Autonomous Enterprise Intelligence Platform"

# 2. Create and activate a Python 3.11 virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate

# 3. Install required Python packages
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

# 4. Initialize environment configuration
cp .env.example .env

# 5. Start the FastAPI development server
# Windows PowerShell:
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Linux / macOS:
PYTHONPATH=backend python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000`.
Explore the interactive API docs at `http://127.0.0.1:8000/docs`.

---

### 2.2 Frontend Setup

```bash
# 1. Open a new terminal and navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start the Vite development server
npm run dev
```
The frontend UI will be available at `http://localhost:5173`.
Vite dev server automatically proxies `/api` and `/health` requests to `http://127.0.0.1:8000`.

---

## 3. Running Automated Tests & QA

### 3.1 Backend Tests (Pytest)
```powershell
$env:PYTHONPATH="backend"
.\.venv\Scripts\python.exe -m pytest backend/tests -v
```

### 3.2 End-to-End User Journey
Ensure the backend server is running on port 8000, then execute:
```powershell
.\.venv\Scripts\python.exe scripts/run_e2e_journey.py
```

### 3.3 Frontend Compilation & Type Checking
```bash
cd frontend
npm run build
```

---

## 4. Coding Standards & Conventions

### 4.1 Backend (Python)
- **Formatting**: PEP 8 compliance.
- **Typing**: Strict type hints on all function signatures (`pydantic` v2 models for DTOs, `TypedDict` for LangGraph agent states).
- **Asynchronous Architecture**: All I/O-bound functions (database calls, file writes, network requests) must be `async/await`.
- **Error Handling**: Use standard FastAPI `HTTPException` with explicit status codes and error payloads.

### 4.2 Frontend (TypeScript & React)
- **Strict Typing**: All React components, props, hooks, and API payloads must have explicit TypeScript types.
- **Styling**: Tailwind CSS utility classes; avoid inline styles.
- **Icons**: `lucide-react` icons for consistency across all 11 views.
- **Component Decomposition**: Shared components live in `src/components/`, while top-level page views live in `src/pages/`.

---

## 5. Adding New Capabilities

### 5.1 Adding a New Document Parser
1. Open `backend/app/ingestion/parsers.py`.
2. Implement your parser method `parse_<format>(content: bytes, filename: str) -> List[Dict[str, Any]]`.
3. Register the file extension in `backend/app/ingestion/pipeline.py` inside `SUPPORTED_EXTENSIONS`.

### 5.2 Adding a New Agent to the Multi-Agent Graph
1. Open `backend/app/agents/specialized/`.
2. Create `your_agent.py` implementing `class YourAgent(BaseAgent)`.
3. Define its node execution method `async def run(self, state: AgentState) -> Dict[str, Any]`.
4. Open `backend/app/agents/graph.py` and register the node with `workflow.add_node("your_agent", agent.run)` and add corresponding state edges.

### 5.3 Adding a New MCP Tool
1. Open `backend/app/mcp/tools.py`.
2. Define the tool function decorated with `@mcp_tool(name="...", description="...", input_schema={...})`.
3. Register the tool in `MCP_TOOLS_REGISTRY`. The tool is automatically discovered by both `tools/list` and the frontend Integrations view.
