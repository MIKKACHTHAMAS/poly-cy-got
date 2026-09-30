from language_layer import detect_language, translate_text
from verifier import verify_recommendation

# Symbolic cybersecurity rules (MeTTa-inspired)
RISK_RULES = [
    {
        "id": "otp_request",
        "keywords": ["otp", "one time password", "verification code", "passcode"],
        "indicator": "Message asks for OTP",
        "risk": "high",
        "action": "Never share OTP with anyone. Banks never ask for OTP."
    },
    {
        "id": "urgent_threat",
        "keywords": [
            "suspend", "suspended", "block", "blocked",
            "deactivat", "clos", "urgent", "immediately",
            "within 24", "expire", "expired", "last warning",
            "final notice", "action required"
        ],
        "indicator": "Urgent threat creating pressure",
        "risk": "medium",
        "action": "Scammers create urgency to bypass your judgment."
    },
    {
        "id": "suspicious_link",
        "keywords": [
            "click here", "click the link", "link", "verify now",
            "update account", "confirm your", "log in", "login",
            "http://", "https://", "bit.ly", "tinyurl"
        ],
        "indicator": "Unexpected link in message",
        "risk": "medium",
        "action": "Don't click links. Go to the official app or website directly."
    },
    {
        "id": "credential_request",
        "keywords": [
            "password", "pin", "cvv", "card number",
            "aadhaar", "pan number", "account number"
        ],
        "indicator": "Message asks for credentials",
        "risk": "high",
        "action": "Legitimate banks never ask for passwords, PINs, or card details via SMS."
    },
    {
        "id": "payment_request",
        "keywords": [
            "pay", "payment", "transfer", "fee", "charge",
            "refund", "cashback", "reward"
        ],
        "indicator": "Request involving money",
        "risk": "high",
        "action": "Legitimate banks don't demand immediate payment via message."
    }
]


async def process_message(
    message: str,
    language: str = "auto",
    explanation_level: str = "simple",
    session_id: str = None
) -> dict:
    # 1. Language detection
    detected = await detect_language(message)
    user_lang = detected if language == "auto" else language

    # 2. Normalize to English for reasoning
    if user_lang == "ta-IN":
        working_text = await translate_text(message, "ta-IN", "en-IN")
    else:
        working_text = message

    # 3. Apply symbolic rules
    text_lower = working_text.lower()
    indicators = []
    actions = []

    for rule in RISK_RULES:
        if any(kw in text_lower for kw in rule["keywords"]):
            indicators.append({
                "rule_id": rule["id"],
                "indicator": rule["indicator"],
                "risk": rule["risk"]
            })
            actions.append(rule["action"])

    # 4. Determine if follow-up is needed
    question_words = ["how", "what", "why", "when", "where", "which", "can i", "should i", "explain"]
    is_question = any(q in text_lower for q in question_words) and "?" in working_text

    needs_followup = (
        len(indicators) == 0
        and not is_question
        and any(word in text_lower for word in ["message", "sms", "email", "link", "bank"])
    )

    # 5. Build English response
    if indicators:
        # UNCOMMENT THE NEXT LINE ONLY DURING YOUR DEMO VIDEO
        # TO PROVE THE VERIFIER BLOCKS UNSAFE ADVICE:
        # english_reply = "Please share your OTP to verify your account immediately."
        risk_summary = ", ".join([i["indicator"] for i in indicators])
        english_reply = (
            f"I found {len(indicators)} risk indicator(s): {risk_summary}. "
            f"What you should do: " + " ".join(actions) +
            " If you're unsure, verify directly through your bank's official app or phone number."
        )
    elif needs_followup:
        english_reply = (
            "I need more details to assess this. "
            "What exactly does the message say? "
            "Does it ask for OTP, password, payment, or ask you to click a link?"
        )
    elif any(word in text_lower for word in [
        "how", "what is", "what are", "explain", "guide", "enable", "setup",
        "install", "update", "password manager", "vpn", "2fa", "two factor",
        "two-factor", "authenticator", "backup"
    ]):
        # General cybersecurity question, not a threat report
        english_reply = (
            "That's a good cybersecurity question. "
            "Here are the general best practices: "
            "1) Enable two-factor authentication wherever possible. "
            "2) Use a password manager to generate unique passwords. "
            "3) Keep your apps and OS updated. "
            "4) Never reuse passwords across sites. "
            "For a specific setup, check the official help pages for that service."
        )
    else:
        english_reply = (
            "I don't see clear risk indicators in what you described. "
            "Can you share more details, or ask a specific cybersecurity question?"
        )

    # 6. Verify the advice BEFORE translating back
    verification = verify_recommendation(english_reply, indicators)

    # If verification failed, substitute a safe fallback
    if verification["status"] == "needs_review":
        english_reply = (
            "I can't safely assess this message without more information. "
            "Do not share OTP, passwords, or click unknown links. "
            "Verify directly through your bank's official app or phone number."
        )
        verification = verify_recommendation(english_reply, indicators)

    # 7. Translate back to user's language
    if user_lang == "ta-IN":
        final_reply = await translate_text(english_reply, "en-IN", "ta-IN")
    else:
        final_reply = english_reply

    return {
        "reply": final_reply,
        "detected_language": user_lang,
        "risk_indicators": indicators,
        "verification": verification,
        "needs_followup": needs_followup
    }