"""
PolyCyGot minimal safety guard.

Gemini does all reasoning. This verifier only blocks genuinely unsafe
advice (in English or Tamil) that might slip through. It does not
require keywords, does not care about indicators, and does not
escalate to needs_review for normal replies.
"""

UNSAFE_PHRASES = [
    # English
    "share your otp",
    "share the otp",
    "send your otp",
    "send the otp",
    "give them your otp",
    "tell them your otp",
    "provide your otp",
    "share your password",
    "send your password",
    "give your password",
    "tell them your password",
    "share your pin",
    "share your cvv",
    "share your card details",
    "enter your card details",
    "share your aadhaar",
    "share your bank details",
    "click the suspicious link",
    "click the link in the message",
    "click the link in the sms",
    "it is safe to click",
    "go ahead and click",

    # Tamil
    "otp பகிர",
    "otp அனுப்ப",
    "otp சொல்ல",
    "otp கொடு",
    "கடவுச்சொல் பகிர",
    "கடவுச்சொல் அனுப்ப",
    "கடவுச்சொல் சொல்ல",
    "pin பகிர",
    "cvv பகிர",
    "aadhaar பகிர",
    "வங்கி விவரங்களை பகிர",
    "சந்தேகத்திற்குரிய இணைப்பை கிளிக்",
    "அந்த இணைப்பை கிளிக்",
]


def verify_recommendation(answer: str, indicators: list = None) -> dict:
    """
    Deterministic safety check.

    Passes unless the reply contains an explicitly unsafe phrase.
    Indicators (if provided) are informational only — they do not
    affect the pass/fail result.
    """
    text = (answer or "").lower()
    blocked = [phrase for phrase in UNSAFE_PHRASES if phrase in text]

    checks = []

    if blocked:
        for phrase in blocked:
            checks.append({
                "rule": f"Unsafe advice blocked: '{phrase}'",
                "passed": False,
                "detail": "Agent attempted to advise an unsafe action."
            })
    else:
        checks.append({
            "rule": "No unsafe phrases in advice",
            "passed": True,
        })

    # Add an informational note if indicators were detected
    if indicators:
        checks.append({
            "rule": f"Risk indicators detected: {len(indicators)}",
            "passed": True,
            "detail": ", ".join(i.get("indicator", "") for i in indicators),
        })

    return {
        "status": "needs_review" if blocked else "passed",
        "checks": checks,
        "blocked_phrases": blocked,
    }