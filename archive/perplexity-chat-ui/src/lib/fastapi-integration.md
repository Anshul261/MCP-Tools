# FastAPI Backend Integration Guide

This document outlines the expected FastAPI backend structure for full integration with the chat UI.

## Backend Endpoints Required

### Authentication
- `POST /auth/login` - User login with email/password
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user info

### Chat
- `POST /chat/message` - Send text message
- `POST /chat/upload` - Send message with file attachments
- `GET /chat/sessions` - Get user's chat sessions
- `GET /chat/sessions/{session_id}` - Get specific session
- `DELETE /chat/sessions/{session_id}` - Delete session

### Voice
- `POST /voice/transcribe` - Transcribe audio to text
- `POST /voice/synthesize` - Convert text to speech

## Expected Request/Response Formats

### Chat Message Request
```json
{
  "message": "Hello, how can you help me?",
  "session_id": "optional-session-id",
  "model": "gpt-4",
  "search_mode": "both",
  "temperature": 0.7
}
```

### Chat Response
```json
{
  "message": "I can help you with various tasks...",
  "session_id": "session-123",
  "sources": ["https://example.com/source1"],
  "model_used": "gpt-4"
}
```

### Session Object
```json
{
  "id": "session-123",
  "title": "Chat about AI",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T01:00:00Z",
  "messages": [
    {
      "id": "msg-1",
      "content": "Hello",
      "role": "user",
      "timestamp": "2024-01-01T00:00:00Z",
      "files": []
    }
  ]
}
```

## Environment Variables

Create a `.env.local` file with:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## CORS Configuration

Ensure your FastAPI backend includes CORS middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## File Upload Handling

The frontend sends files as multipart/form-data with the following structure:
- `message`: The text message
- `model`: AI model to use
- `search_mode`: Search mode (online/local/both)
- `files`: Array of uploaded files
- `session_id`: Optional session ID

## Authentication Flow

1. User logs in via `/auth/login`
2. Backend returns JWT token
3. Frontend stores token and includes in Authorization header
4. Token is validated on protected endpoints

## Error Handling

The API client expects HTTP status codes:
- 200-299: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses should include:
```json
{
  "detail": "Error description"
}
```