# Engram Intelligent Wiring & Chat Interface Plan

The goal is to create a "Live Context" environment where the Engram model is aware of your entire project and accessible via a premium web UI that integrates with OpenCode.

## Key Features

1.  **Context-Aware Server**:
    *   Inject `project.md` and active specs into the model's environment.
    *   Enable CORS for web access.
    *   Expose metadata about the project (file list, spec status).
2.  **Premium Web UI**:
    *   Glassmorphism design, dark mode, rich animations.
    *   Real-time chat with the Engram model.
    *   "Project Insight" panel showing active specs.
    *   "OpenCode Trigger" interface to run terminal commands directly from the chat.
3.  **Live Updates**:
    *   Use `fastapi` to serve the frontend and the model API.

## Implementation Steps

1.  **Update `engram_server.py`**:
    *   Add CORS middleware.
    *   Add logic to load all `.md` files in `openspec/` as "context".
    *   Add `StaticFiles` mounting for the frontend.
2.  **Create `frontend/static/index.html`**:
    *   The core UI structure and Glassmorphism styling.
3.  **Create `frontend/static/app.js`**:
    *   State management for chat.
    *   API calls to the local OpenResponses endpoint.
    *   OpenCode execution bridging.
