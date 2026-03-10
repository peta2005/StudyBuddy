# StudyBuddy

A PDF-based question-answering assistant with a Python backend and TypeScript React frontend.

## Project structure

- `backend/` - Flask API, PDF upload, embedding store, query + LLM summarization.
- `pdf-pal-genius/` - Vite + React frontend UI.

## Setup

### Backend

1. Open terminal:
   `cd backend`
2. Create venv:
   `python -m venv .venv`
3. Activate venv:
   `.venv\Scripts\activate` (Windows)
4. Install deps:
   `pip install -r requirements.txt`
5. Set API key in `.env` (or env var):
   `GROQ_API_KEY=your_groq_key`
6. Start server:
   `python app.py` (or `uvicorn app:app --reload --port 5000`)

### Frontend

1. Open a terminal:
   `cd pdf-pal-genius`
2. Install deps:
   `npm install`
3. Run dev server:
   `npm run dev`
4. Open `http://localhost:5173`

## API end-points

- `POST /upload` (form-data, key `pdf`) - upload PDF and build vector store
- `POST /ask` (JSON `{ "query": "..." }`) - ask question

## Notes

- API base for frontend configured in `pdf-pal-genius/src/api.ts`.
- In `backend/app.py`, LLM client configured via `groq` (`GROQ_API_KEY`).
- Branch `ask` endpoint prints errors `ASK ROUTE ERROR:` to terminal.

## Troubleshooting

- If you encounter `Incorrect API key provided`:
  - remove stale `OPENAI_API_KEY` and set `GROQ_API_KEY` only
  - restart terminal and backend server.

- If `uvicorn` missing:
  - `pip install uvicorn`

## Optional

- Switch model in `app.py`:
  - `grok-3-latest` -> `llama-3.3-70b-versatile`

Enjoy building your StudyBuddy application!
