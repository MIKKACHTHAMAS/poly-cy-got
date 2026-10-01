from dataclasses import dataclass
from typing import List


@dataclass
class VerificationResult:

    safe: bool

    risk: str

    reasons: List[str]

    safe_response: str