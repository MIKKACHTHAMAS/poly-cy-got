"""
Verification engine for PolyCyGot.

Checks agent-generated advice against deterministic safety rules
BEFORE the response reaches the user. This is what separates
PolyCyGot from a plain LLM chatbot.
"""

# Phrases that must NEVER appear in safe cybersecurity advice
UNSAFE_PHRASES = [
    "share your otp",
    "share the otp",
    "send your otp",
    "tell them your otp",
    "share your password",
    "send your password",
    "give your password",
    "share your pin",
    "share your cvv",
    "click the suspicious link",
    "click the link in the message",
    "enter your card details",
    "provide your aadhaar",
    "share your aadhaar",
    "give your bank details",
]

# Actions we REQUIRE the agent to mention for high-risk scenarios.
# If a rule fires but the advice omits the safety action, we flag it.
REQUIRED_ACTIONS = {
    "otp_request": ["otp"],
    "credential_request": ["password", "pin", "credential"],
    "payment_request": ["bank", "official", "verify"],
    "suspicious_link": ["link", "official", "click"],
    "urgent_threat": ["verify", "official", "bank"],
}


def verify_recommendation(answer: str, indicators: list) -> dict:
    """
    Run deterministic checks on the agent's advice.

    Returns:
        {
            "status": "passed" | "needs_review" | "insufficient_evidence",
            "checks": [ {rule, passed, detail?}, ... ],
            "blocked_phrases": [...]
        }
    """
    checks = []
    text = answer.lower()
    blocked = []

    # Check 1: No unsafe phrases
    for phrase in UNSAFE_PHRASES:
        if phrase in text:
            blocked.append(phrase)
            checks.append({
                "rule": f"Unsafe advice blocked: '{phrase}'",
                "passed": False,
                "detail": "Agent attempted to advise an unsafe action."
            })

    if not blocked:
        checks.append({
            "rule": "No unsafe phrases in advice",
            "passed": True
        })

    # Check 2: Every detected indicator has a corresponding safety action
    for ind in indicators:
        rule_id = ind.get("rule_id", "")
        required = REQUIRED_ACTIONS.get(rule_id, [])

        if not required:
            continue

        # The English advice must mention at least one required safety term
        # (We check the pre-translation English text)
        mentioned = any(term in text for term in required)
        checks.append({
            "rule": f"Safety action present for '{rule_id}'",
            "passed": mentioned,
            "detail": None if mentioned else f"Expected one of {required}"
        })

    # Check 3: If there are no indicators, is there evidence?
    if not indicators:
        checks.append({
            "rule": "Evidence indicators provided",
            "passed": False,
            "detail": "No risk indicators detected — response should ask follow-up."
        })
    else:
        checks.append({
            "rule": "Evidence indicators provided",
            "passed": True
        })

    # Determine overall status
    all_passed = all(c["passed"] for c in checks)
    if blocked:
        status = "needs_review"
    elif all_passed:
        status = "passed"
    elif not indicators:
        status = "insufficient_evidence"
    else:
        status = "needs_review"

    return {
        "status": status,
        "checks": checks,
        "blocked_phrases": blocked
    }