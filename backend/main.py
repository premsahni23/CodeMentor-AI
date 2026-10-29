import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="CodeMentor AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    # Vite normally uses 5173, but moves to 5174 when that port is occupied.
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReviewRequest(BaseModel):
    code: str = Field(min_length=1, max_length=30000)
    language: str = Field(min_length=1, max_length=32)


class ReviewResult(BaseModel):
    score: int = Field(ge=0, le=100)
    explanation: str
    bugs: list[str]
    improvements: list[str]
    unit_tests: str
    improved_code: str


class ReviewResponse(ReviewResult):
    source: Literal["ai", "demo"]


SYSTEM_PROMPT = """You are CodeMentor AI, an encouraging senior software engineer. Review code accurately.
Return constructive feedback appropriate to the provided programming language. Do not claim a bug is certain unless it is.
Give a score from 0 to 100. The improved_code and unit_tests fields must contain code only, without Markdown fences.
If there are no meaningful bugs, put an empty list in bugs. Keep all prose concise and beginner-friendly."""


def demo_review(code: str, language: str) -> ReviewResult:
    """Lets the project work immediately before an API key is configured."""
    lines = len(code.splitlines())
    has_print = "print(" in code or "console.log(" in code
    bugs = ["No definite runtime bug was found in this short example."]
    improvements = [
        "Use descriptive names and keep functions focused on one task.",
        "Add tests for normal inputs and edge cases before refactoring.",
    ]
    if has_print:
        improvements.insert(0, "Consider returning values from reusable functions instead of logging inside them.")
    return ReviewResult(
        score=76,
        explanation=f"This {language} snippet has {lines} line(s). Demo mode provides starter feedback; add an API key for a code-specific AI review.",
        bugs=bugs,
        improvements=improvements,
        unit_tests="# Add OPENAI_API_KEY for generated, code-specific unit tests.",
        improved_code=code,
    )


def ai_review(request: ReviewRequest) -> ReviewResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return demo_review(request.code, request.language)

    client = OpenAI(api_key=api_key)
    try:
        completion = client.chat.completions.parse(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Language: {request.language}\n\nCode to review:\n{request.code}"},
            ],
            response_format=ReviewResult,
        )
        message = completion.choices[0].message
        if message.refusal:
            raise HTTPException(status_code=422, detail="The AI could not review this code: " + message.refusal)
        if not message.parsed:
            raise HTTPException(status_code=502, detail="The AI returned an incomplete review. Please try again.")
        return message.parsed
    except HTTPException:
        raise
    except Exception as error:
        # Details stay in server logs; the client gets a safe, actionable message.
        print(f"OpenAI review failed: {type(error).__name__}: {error}")
        raise HTTPException(status_code=502, detail="Could not reach the AI service. Check your API key and try again.")


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_configured": bool(os.getenv("OPENAI_API_KEY"))}


@app.post("/api/review", response_model=ReviewResponse)
def review(request: ReviewRequest):
    result = ai_review(request)
    return ReviewResponse(**result.model_dump(), source="ai" if os.getenv("OPENAI_API_KEY") else "demo")
