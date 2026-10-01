# PolyCyGot Architecture

PolyCyGot uses a neuro-symbolic architecture.

## Components

### Frontend

React provides the user interface.

### FastAPI

FastAPI exposes the backend API.

### Gemini

Gemini performs natural-language reasoning and response generation.

### Sarvam

Sarvam handles multilingual processing and translation.

### MeTTa

MeTTa provides the symbolic reasoning and safety verification layer.

## Data Flow

User
    |
    v
React
    |
    v
FastAPI
    |
    +----> Sarvam
    |
    +----> Gemini
              |
              v
         Generated Response
              |
              v
          MeTTa Engine
              |
        +-----+-----+
        |           |
       SAFE       UNSAFE
        |           |
        v           v
     Response    Safe Fallback