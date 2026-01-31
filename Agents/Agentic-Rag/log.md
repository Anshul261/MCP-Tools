# Agentic-Rag Projects Feature — Implementation Log

## Plan

Add a "Projects" feature where users upload files that get ingested into a per-project AGNO `Knowledge` base backed by PgVector. Users then ask questions using AGNO's native agentic RAG (`search_knowledge=True`). User isolation via `user_id` stored in browser localStorage. Session metadata in SQLite (`agent_sessions.db`), vector embeddings in PostgreSQL with pgvector.

### Architecture

```
User uploads files to Project
  -> Backend saves file metadata to SQLite (agent_sessions.db)
  -> Backend ingests file content into AGNO Knowledge(PgVector) with table_name="project_{id}"
  -> User asks question
  -> Backend creates Agent with knowledge=Knowledge(PgVector(table="project_{id}")), search_knowledge=True
  -> AGNO's agentic RAG searches the vector DB automatically
  -> SSE streamed response back to UI
```

### Key Design Decisions

1. **AGNO-native RAG**: `agno.knowledge.knowledge.Knowledge` + `agno.vectordb.pgvector.PgVector` per project
2. **Per-project vector table**: Each project gets `project_{project_id}` table in PgVector
3. **Embedder**: `OllamaEmbedder` with `nomic-embed-text-v2-moe` (768 dims, fully local)
4. **File ingestion**: Extract text via PyPDF2 (PDF) or UTF-8 decode, wrap in `agno.knowledge.document.Document`, call `knowledge.load_documents()`
5. **Session DB**: SQLite `agent_sessions.db` for project + file metadata
6. **No new pyproject.toml**: Uses existing root `/home/anshul/projects/MCP-Tools/pyproject.toml` with `uv`

---

## Completed Work

### 1. `agent-api.py` — Backend (MODIFIED)

**New imports added:**
- `sqlite3`, `uuid`, `json`, `asyncio`
- `agno.knowledge.document.Document`
- `agno.knowledge.knowledge.Knowledge`
- `agno.knowledge.embedder.ollama.OllamaEmbedder`
- `agno.vectordb.pgvector.PgVector`, `SearchType`
- `fastapi.UploadFile`, `File`, `Form`, `Query`
- `fastapi.responses.StreamingResponse`
- `pydantic.BaseModel`

**Project database setup:**
- SQLite tables `projects` and `project_files` created in `agent_sessions.db`
- `projects`: id, user_id, name, description, created_at
- `project_files`: id, project_id, filename, file_type, size, created_at
- Foreign key with CASCADE delete

**Helper functions:**
- `init_project_tables()` — creates SQLite tables at startup
- `get_project_knowledge(project_id)` — returns AGNO Knowledge object with PgVector (hybrid search, OllamaEmbedder nomic-embed-text-v2-moe, 768 dims)
- `extract_text_from_bytes(content, filename)` — PDF via PyPDF2 or UTF-8 text

**7 new API endpoints on `custom_router`:**

| Endpoint | Method | Description |
|---|---|---|
| `/projects` | POST | Create project (JSON body: user_id, name, description) |
| `/projects` | GET | List projects by user_id query param |
| `/projects/{id}` | GET | Get project details + file list |
| `/projects/{id}` | DELETE | Delete project + drop PgVector table |
| `/projects/{id}/files` | POST | Upload files (multipart), extract text, ingest into PgVector |
| `/projects/{id}/files/{file_id}` | DELETE | Remove file metadata |
| `/projects/{id}/query` | POST | Query project knowledge base with SSE streaming |

**Query endpoint details:**
- Creates a per-request `Agent` with the project's `Knowledge` and `search_knowledge=True`
- Streams SSE events (`RunContent`, `RunEvent`, `RunError`) via `StreamingResponse`
- Uses `project_agent.arun(message, session_id=session_id, stream=True)` as async iterator (no await)
- Non-streaming fallback via `project_agent.run()`

**Config variables (with env overrides):**
- `PGVECTOR_DB_URL` — default: `postgresql+psycopg://postgres:postgres@localhost:5432/rag_db`
- `OLLAMA_HOST` — default: `http://localhost:11434`
- `EMBEDDING_MODEL` — default: `nomic-embed-text-v2-moe`
- `EMBEDDING_DIMENSIONS` — default: `768`

---

### 2. `UI-Iluminati/lib/api.ts` — API Client (MODIFIED)

**New exports:**
- `getUserId()` — generates/caches UUID in localStorage (`agno_user_id` key)
- `createProject(userId, name, description)` — POST `/projects`
- `listProjects(userId)` — GET `/projects?user_id=X`
- `getProject(projectId)` — GET `/projects/{id}` (returns files list)
- `deleteProject(projectId)` — DELETE `/projects/{id}`
- `uploadProjectFiles(projectId, files)` — POST `/projects/{id}/files` (FormData)
- `deleteProjectFile(projectId, fileId)` — DELETE `/projects/{id}/files/{file_id}`
- `queryProject(projectId, message, sessionId)` — POST `/projects/{id}/query` (returns raw Response for SSE)

**New TypeScript interfaces:**
- `ProjectInfo` (id, user_id, name, description, created_at, file_count)
- `ProjectFileInfo` (id, filename, file_type, size, created_at)
- `ProjectDetail extends ProjectInfo` (with files array)

---

### 3. `UI-Iluminati/components/chat-interface.tsx` — Frontend (MODIFIED)

**State changes:**
- Removed mock project data (3 hardcoded projects)
- Added `userId` state from `getUserId()`
- Added `uploadingFiles` loading state
- Changed `Project.chatCount` to `Project.file_count`

**New functions:**
- `loadProjects()` — fetches projects from API on mount
- `loadProjectDetails(projectId)` — fetches project with file list, sets as selected
- `handleDeleteProject(projectId)` — calls API delete, removes from state

**Modified functions:**
- `handleCreateProject` — now async, calls `apiCreateProject()`, adds result to state
- `handleProjectFileUpload` — now async, calls `uploadProjectFiles()`, updates state with returned file metadata, shows uploading indicator
- `handleRemoveFile` — now async, calls `deleteProjectFile()` API
- `handleSubmit` (project mode) — replaced mock setTimeout with real SSE streaming via `queryProject()`, parses `RunContent` and `RunError` events identically to team chat mode

**UI changes:**
- Project list items: now `<div>` with nested `<button>` for click + separate delete button (trash icon, visible on hover)
- Project click loads details from API and clears messages
- Upload button shows "Uploading..." with disabled state during upload
- Projects sidebar shows `file_count` instead of `chatCount`

---

## Bug Fixes

1. **AsyncIterator not awaitable**: Changed `await project_agent.arun(..., stream=True)` to `project_agent.arun(...)` — with `stream=True`, AGNO returns an `AsyncIterator` directly, not an awaitable
2. **Default port**: Fixed `PGVECTOR_DB_URL` default from port `5433` to `5432`

## Known Issue (Pending)

- PostgreSQL connection refused — Docker container may not be running or credentials/port may need adjustment in `.env`. The default in code is `postgresql+psycopg://postgres:postgres@localhost:5432/rag_db`. Override via `PGVECTOR_DB_URL` env var if your setup differs.

## Files Changed

| File | Action |
|---|---|
| `Agents/Agentic-Rag/agent-api.py` | Modified — added project DB, endpoints, Knowledge/PgVector integration |
| `Agents/Agentic-Rag/UI-Iluminati/lib/api.ts` | Modified — added project API functions + getUserId |
| `Agents/Agentic-Rag/UI-Iluminati/components/chat-interface.tsx` | Modified — connected projects to backend, SSE streaming for project queries |
