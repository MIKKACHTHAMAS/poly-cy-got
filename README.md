# 🛡️ PolyCyGot

**An adaptive multilingual cybersecurity agent for the next billion users.**

🌐 **Live App**: [https://polycygot.pages.dev](https://polycygot.pages.dev)
📊 **API Docs**: [https://polycygot-backend.onrender.com/docs](https://polycygot-backend.onrender.com/docs)

PolyCyGot helps users identify phishing, scam messages, and suspicious digital communications — in their own language, at their own literacy level, through text, voice, or a screenshot. It reasons across languages instead of translating a generic chatbot's output, and every reply is verified for safety before it reaches the user.

Built for the **Omega AI Agents — The Agent Without Borders** track.

---

## Table of Contents

- [Why PolyCyGot](#why-polycygot)
- [Live Demo](#live-demo)
- [Features](#features)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Local Setup](#local-setup)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Test Results](#test-results)
- [Security & Privacy](#security--privacy)
- [Roadmap](#roadmap)
- [Hackathon Track](#hackathon-track)
- [License](#license)

---

## Why PolyCyGot

**Cybersecurity help is almost always English-only.** For hundreds of millions of Indian users who prefer Tamil, Hindi, or another local language, this means:

- They cannot understand bank warnings written in English.
- They cannot explain a suspicious message in English.
- Existing chatbot products simply translate English answers, which lose meaning, tone, and cultural context.
- Low-literacy users need simpler, more visual explanations — not a longer paragraph.

PolyCyGot solves this by **reasoning across languages**, not just translating. It detects what language the user is using (including Tamil–English code-mixing), understands the cybersecurity concern, applies an explicit safety knowledge base, verifies the advice, and replies in the user's language at their preferred level of detail.

---

## Live Demo

| Resource | URL |
|---|---|
| **Live App** | https://polycygot.pages.dev |
| **Backend API** | https://polycygot-backend.onrender.com |
| **API Docs** | https://polycygot-backend.onrender.com/docs |
| **Video Demo** | _[add after recording]_ |
| **Source Code** | https://github.com/MIKKACHTHAMAS/poly-cy-got |

The backend is kept awake with UptimeRobot pinging every 5 minutes, so it responds instantly when you visit.

---

## Features

### 🌐 Adaptive Multilingual Communication

- **Language detection** — English, Tamil, and code-mixed "Tanglish" (e.g., *"My bank கணக்கு blocked ஆகும், link click பண்ணுங்க"*)
- **Bidirectional translation** — Sarvam AI handles Tamil ↔ English with cybersecurity-domain accuracy
- **Preserves meaning** — the agent reasons in English (where security logic is reliable) and renders the reply in the user's language, so the underlying safety facts never change

### 🧠 Natural Language Reasoning

- **LLM-driven responses** — Google Gemini 3.5 Flash-Lite generates the reply, so it never sounds templated
- **Handles any query type** — threat analysis, education ("what is phishing?"), general advice, greetings, follow-ups
- **Follow-up questions** — when a message is vague, the agent asks for specifics instead of guessing

### 🎤 Voice Input & 🔊 Voice Output

- **Speak your question** — Gemini 3.8 Flash transcribes voice in English or Tamil
- **Hear the reply** — Sarvam Bulbul v3 speaks the answer back in the user's language
- **Designed for accessibility** — hands-free use for users who find typing difficult

### 🖼️ Image Input — Screenshot Analysis

- **Upload a screenshot** of a suspicious SMS, email, or message
- **Gemini multimodal** analyzes the image for phishing indicators (fake domains, urgency language, suspicious links)
- **Privacy-first** — a warning dialog reminds users to redact OTPs and personal details before uploading

### ✅ Verification Engine

- **Deterministic safety layer** that runs after the LLM and before the user sees the reply
- **Blocks unsafe advice** in both English and Tamil — e.g., if the LLM tries to say *"share your OTP"* or *"click the link"*, the verifier catches it
- **Transparent audit trail** — every reply shows which checks passed
- **Self-correcting** — if the LLM produces something unsafe, the agent substitutes a safe fallback

### 💬 Chat History

- **Persistent sessions** — every conversation is stored locally in the browser
- **Resume anytime** — click a past chat to reload it
- **Delete individually or clear all** — full control over history
- **No server storage** — history lives only in `localStorage`

### 🎨 Adaptive Explanation Levels

- **Beginner mode** — plain language with relatable analogies ("MFA is like a second lock on your front door")
- **Technical mode** — precise terminology ("credential harvesting," "phishing vector," "domain mismatch")
- **Same security facts** — only the wording changes

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  React Frontend (Cloudflare Pages)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Chat UI     │  │  Voice I/O   │  │  Image Upload    │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│  Language selector · Level toggle · Chat history (localStorage) │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / JSON / multipart
┌──────────────────────────▼──────────────────────────────────┐
│  FastAPI Backend (Render)                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Sarvam AI                                           │   │
│  │  · Language detection (Tamil / English / Tanglish)   │   │
│  │  · Translation (ta-IN ↔ en-IN)                       │   │
│  │  · Text-to-speech (Bulbul v3)                        │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Google Gemini                                       │   │
│  │  · Natural-language reasoning (3.5 Flash-Lite)       │   │
│  │  · Voice transcription (3.8 Flash, multimodal)       │   │
│  │  · Image / screenshot analysis (multimodal)          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Verification Engine (symbolic safety layer)         │   │
│  │  · Unsafe-phrase blocking (EN + TA)                  │   │
│  │  · Pass/fail audit trail                             │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  SQLite                                              │   │
│  │  · Consent-based user preferences                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Neural-symbolic split:**

- **Neural:** Sarvam and Gemini handle language understanding, translation, reasoning, and generation
- **Symbolic:** The verification engine enforces explicit safety rules — the LLM never gets the final word on safety-critical advice

---

## How It Works

1. **User sends a message** — typed, spoken, or as an image
2. **Language detection** — Sarvam identifies English, Tamil, or code-mixed input
3. **Translation to English** — for consistency in the reasoning layer
4. **LLM reasoning** — Gemini analyzes the query and generates a natural reply
5. **Verification** — the symbolic safety layer checks the reply for unsafe advice in both languages
6. **Translation back** — Sarvam renders the reply in the user's language
7. **Voice output** — if enabled, Sarvam Bulbul speaks the reply

If verification fails, the agent substitutes a safe fallback and flags it transparently.

---

## Screenshots

> Screenshots are stored in `docs/screenshots/`. Add your images there with these filenames.

### Hero — clean, distraction-free interface

![Hero screen](docs/screenshots/01-hero.png)

### Tamil phishing detection with risk badges

![Tamil phishing](docs/screenshots/02-tamil-phishing.png)

### Verification engine — every reply audited

![Verification panel](docs/screenshots/03-verification.png)

### Voice input — speak in English or Tamil

![Voice input](docs/screenshots/04-voice.png)

### Image analysis — screenshot a suspicious message

![Image analysis](docs/screenshots/05-image.png)

### Chat history — persistent across sessions

![Chat history](docs/screenshots/06-history.png)

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 18 + Vite | Fast, modern UI |
| Styling | Tailwind CSS v4 | Responsive dark UI |
| Icons | lucide-react | Clean, consistent iconography |
| Backend | FastAPI | Async API, file uploads, CORS |
| Language AI | Sarvam AI | Detection, translation, TTS |
| Reasoning AI | Google Gemini | Natural language, multimodal |
| Safety | Custom Python verifier | Unsafe-phrase blocking |
| Storage | SQLite + localStorage | Preferences + chat history |
| Fonts | Noto Sans Tamil | Proper Tamil script rendering |
| Frontend Host | Cloudflare Pages | Global CDN, free tier |
| Backend Host | Render | Free tier with uptime monitoring |
| Monitoring | UptimeRobot | Keeps backend awake |

---

## Local Setup

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Git**
- **Sarvam AI key** — [dashboard.sarvam.ai](https://dashboard.sarvam.ai)
- **Google Gemini key** — [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/MIKKACHTHAMAS/poly-cy-got.git
cd poly-cy-got
```

**2. Configure API keys**

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```
SARVAM_API_KEY=your_sarvam_key_here
GEMINI_API_KEY=your_gemini_key_here
```

**3. Backend setup**

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**4. Frontend setup** (in a new terminal)

```bash
cd frontend
npm install
npm run dev
```

**5. Open the app**

- Frontend: http://localhost:5173
- Backend docs: http://127.0.0.1:8000/docs

---

## Deployment

### Backend — Render

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect the GitHub repository
3. Set:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
4. Add environment variables:
   - `SARVAM_API_KEY`
   - `GEMINI_API_KEY`
   - `PYTHON_VERSION=3.11.9`

### Frontend — Cloudflare Pages

1. Go to **Workers & Pages** → **Create application** → **Pages tab**
2. Connect the GitHub repository
3. Set:
   - **Framework preset**: React (Vite)
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
   - **Root directory**: `frontend`
4. Add environment variable:
   - `VITE_API_URL` = `https://polycygot-backend.onrender.com`
5. Click **Save and Deploy**

### Keep Backend Awake — UptimeRobot

Render's free tier sleeps after 15 minutes of inactivity. To prevent cold-start delays:

1. Sign up at [uptimerobot.com](https://uptimerobot.com) (free)
2. Add a new **HTTP(s)** monitor
3. URL: `https://polycygot-backend.onrender.com/`
4. Interval: **5 minutes**

---

## API Reference

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/chat` | Send a text message and receive an agent reply |
| `POST` | `/transcribe` | Upload audio, receive transcribed text (Gemini 3.8 Flash) |
| `POST` | `/speak` | Convert text to speech (Sarvam Bulbul v3) |
| `POST` | `/analyze-image` | Upload a screenshot, receive phishing analysis |
| `GET` | `/memory/{user_id}` | Retrieve saved preferences (if consented) |
| `POST` | `/memory` | Save preferences |
| `DELETE` | `/memory/{user_id}` | Delete saved preferences |

Full interactive docs available at `/docs` when the backend is running.

---

## Test Results

All tests run against the live deployment. Language detection via Sarvam, reasoning via Gemini 3.5 Flash-Lite.

### English

| Test | Input | Expected | Result |
|---|---|---|---|
| Phishing SMS | "My bank says my account will be blocked. It has a link." | Detects urgent_threat + suspicious_link, warns against clicking | ✅ |
| OTP request | "My bank is asking for my OTP. Should I share it?" | Warns never to share OTP | ✅ |
| Vague message | "I got a weird message." | Asks clarifying questions, no false claim | ✅ |
| Benign question | "How do I enable 2FA on my Gmail?" | General advice, no false positive | ✅ |
| Technical term | "man in the middle" | Explains MITM concept | ✅ |
| Greeting | "hi" | Warm, helpful response | ✅ |

### Tamil

| Test | Input | Expected | Result |
|---|---|---|---|
| Tamil phishing | "எனக்கு வங்கியிலிருந்து ஒரு மெசேஜ் வந்திருக்கு..." | Tamil reply, ta-IN detected, indicators fire | ✅ |
| Tamil OTP request | "என் வங்கி OTP கேட்கிறது. நான் பகிர வேண்டுமா?" | Tamil reply warning against sharing | ✅ |
| Tanglish code-mix | "My bank கணக்கு blocked ஆகும், link click பண்ணுங்க" | ta-IN detected, both indicators fire | ✅ |
| Tamil awareness | "phishing என்றால் என்ன?" | Tamil explanation | ✅ |
| Tamil greeting | "வணக்கம்" | Tamil greeting reply | ✅ |

### Voice & Image

| Feature | Test | Result |
|---|---|---|
| Voice input | Spoken English via mic → transcribed correctly | ✅ |
| Voice input | Spoken Tamil via mic → transcribed correctly | ✅ |
| Voice output | English reply played back via Sarvam Bulbul | ✅ |
| Voice output | Tamil reply played back via Sarvam Bulbul | ✅ |
| Image input | Screenshot of phishing email → flagged as phishing with domain + urgency + bit.ly indicators | ✅ |

### Verification

| Scenario | Expected | Result |
|---|---|---|
| Safe advice | Verification status: passed | ✅ |
| Unsafe advice (demo) | Blocked phrase `share your otp` detected, reply replaced with safe fallback | ✅ |

**Summary:** All 20+ test cases pass. No false positives on legitimate questions. Zero unsafe advice reached the user.

---

## Security & Privacy

PolyCyGot is a cybersecurity agent, so its own privacy and safety practices matter.

- **No passwords or OTPs are ever requested** — the agent explicitly warns against sharing them
- **Screenshot privacy reminder** — before uploading an image, users are asked to redact any OTP, account number, or personal detail
- **No server-side chat storage** — chat history lives only in the user's browser
- **Consent-based preference storage** — user preferences are saved only if the user opts in
- **API keys are never committed** — `.env` is gitignored; `.env.example` shows the required variables only
- **LLM output is verified** — a deterministic safety layer catches any unsafe advice before the user sees it
- **Multimodal inputs are processed but not retained** — images and audio are sent to Google's API for a single inference call and never stored on our server

---

## Roadmap

Features designed but not yet shipped:

- **MeTTa symbolic reasoning** — replace the Python verifier's rule engine with MeTTa expressions for a fully inspectable reasoning trail
- **Omega agent integration** — run PolyCyGot's reasoning core on the Omega framework for stateful, persistent agent behavior
- **Offline fallback** — a small local rule set for when the network is unavailable, reconciled with the full agent when connectivity returns
- **Hindi, Telugu, Kannada** — expand beyond Tamil and English
- **WhatsApp bot** — meet users where they already are

---

## Hackathon Track

**Omega AI Agents — The Agent Without Borders (Track 2)**

This project directly addresses the track's challenges:

- ✅ **A reasoning agent that explains its decisions in a local language**
- ✅ **An accessibility-first agent that adapts its explanations while preserving its reasoning trail**
- ⏳ **An offline-first agent that reconciles local decisions when connectivity returns** (roadmap)

PolyCyGot combines multilingual reasoning, accessibility, and a verifiable safety layer — designed for the users who need cybersecurity help most, in the language they actually speak.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **SingularityNET** — for the Omega AI Agents hackathon and the Agent Without Borders track
- **Sarvam AI** — for multilingual language models trained on Indian languages
- **Google** — for Gemini's multimodal capabilities
- **The Tamil community** — for keeping the language alive in the digital age

---

**Built with ❤️ for users who deserve cybersecurity help in their own language.**