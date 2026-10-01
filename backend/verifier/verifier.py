from typing import List

from .models import VerificationResult
from metta.engine import MeTTaEngine


engine = MeTTaEngine()


# Text normalization layer.
# This does NOT decide the risk level.
# It only maps recognizable language to symbolic actions.
ACTION_PATTERNS = {
    "share-otp": [
        "share your otp",
        "share otp",
        "send me your otp",
    ],
    "share-password": [
        "share your password",
        "send your password",
    ],
    "share-pin": [
        "share your pin",
    ],
    "disable-mfa": [
        "disable mfa",
        "turn off mfa",
        "disable multi-factor authentication",
    ],
    "click-suspicious-link": [
        "click this suspicious link",
    ],
    "download-unknown-file": [
        "download this file",
        "download this unknown file",
    ],
    "bypass-authentication": [
        "bypass authentication",
        "bypass auth",
    ],
    "steal-credentials": [
        "steal credentials",
        "steal their credentials",
    ],
}


def detect_actions(response: str) -> List[str]:
    """
    Convert recognizable text into symbolic MeTTa actions.

    This function does not determine whether an action is safe.
    That decision is made by MeTTa rules.
    """

    response_lower = response.lower()

    detected = []

    for action, phrases in ACTION_PATTERNS.items():

        for phrase in phrases:

            if phrase in response_lower:

                detected.append(action)
                break

    return detected


def verify_response(
    response: str,
) -> VerificationResult:

    detected_actions = detect_actions(response)

    # No symbolic actions were identified.
    if not detected_actions:

        return VerificationResult(
            safe=True,
            risk="low",
            reasons=[
                "No prohibited action detected."
            ],
            safe_response=response,
        )

    reasons = []

    for action in detected_actions:

        # Add the detected symbolic fact to MeTTa.
        engine.run(
            f"(unsafe-action {action})"
        )

        # Ask MeTTa whether this action is unsafe.
        result = engine.run(
            f"!(verification-unsafe {action})"
        )

        if result:

            reasons.append(
                f"Unsafe action detected: {action}"
            )

    if reasons:

        return VerificationResult(
            safe=False,
            risk="high",
            reasons=reasons,
            safe_response=(
                "I can't recommend that action. "
                "For your safety, do not share "
                "passwords, OTPs, PINs, or other "
                "authentication secrets. Verify "
                "requests through an official channel."
            ),
        )

    return VerificationResult(
        safe=True,
        risk="low",
        reasons=[
            "No prohibited action detected."
        ],
        safe_response=response,
    )
