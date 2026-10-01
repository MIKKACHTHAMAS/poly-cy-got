# PolyCyGot

PolyCyGot is a multilingual cybersecurity assistant.

It combines:

- Gemini
- Sarvam AI
- FastAPI
- React
- MeTTa symbolic reasoning

## Architecture

PolyCyGot follows a neuro-symbolic architecture.

Gemini performs natural-language reasoning.

Sarvam provides multilingual processing.

MeTTa provides deterministic symbolic safety verification.

## Features

- Cybersecurity question answering
- Phishing analysis
- Scam detection
- Multilingual interaction
- Symbolic safety verification
- Explainable verification
- Safe fallback responses

## Backend

Start the backend:

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload