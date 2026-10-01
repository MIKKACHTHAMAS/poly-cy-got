from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.request import ChatRequest
from models.response import ChatResponse

from gemini.client import generate_response
from verifier.verifier import verify_response


app = FastAPI(
    title="PolyCyGot",
    description="Multilingual cybersecurity assistant with MeTTa safety reasoning",
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "PolyCyGot",
        "version": "2.0.0",
        "status": "running",
        "reasoning_engine": "MeTTa",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "metta": True,
        "gemini": True,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty",
        )

    # 1. Generate answer using Gemini
    generated = await generate_response(
        request.message
    )

    # 2. Verify generated answer using MeTTa
    verification = verify_response(
        generated
    )

    # 3. Reject unsafe output
    if not verification.safe:
        return ChatResponse(
            response=verification.safe_response,
            safe=False,
            risk=verification.risk,
            reasons=verification.reasons,
        )

    return ChatResponse(
        response=generated,
        safe=True,
        risk=verification.risk,
        reasons=verification.reasons,
    )