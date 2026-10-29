# CodeMentor AI

A polished, beginner-friendly code-review app. Paste code, select a language, and get an explanation, potential bugs, improvements, test suggestions, a refactor, and an AI-estimated score.

## Stack

- **Frontend:** React, Vite, Monaco Editor
- **Backend:** Python, FastAPI, Pydantic
- **AI:** OpenAI Python SDK using Structured Outputs

## Quick start

Open two terminals from the project folder.

**1. Start the API**

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload --port 8000
```

**2. Start the website**

```powershell
cd frontend
npm install
npm run dev
```

Open the address Vite prints (normally `http://localhost:5173`).

## Add AI reviews

Edit `backend/.env` and set `OPENAI_API_KEY` to your OpenAI API key. `OPENAI_MODEL` defaults to `gpt-4o-mini`, which supports Structured Outputs. Restart the FastAPI server after changing `.env`.

Without a key, the app deliberately stays usable in **Demo mode** with starter feedback. It never exposes the key to the browser.

## Test the API

With the virtual environment activated in `backend`:

```powershell
pip install pytest httpx
pytest -q
```

## Project layout

```text
backend/       FastAPI API, LLM integration, env template, API smoke tests
frontend/      React/Vite application and Monaco-based editor
```

## Notes

- The API accepts code snippets up to 30,000 characters.
- CORS is restricted by `CORS_ORIGINS` in the backend environment file.
- AI feedback is advisory; run generated code and tests before using them in production.
