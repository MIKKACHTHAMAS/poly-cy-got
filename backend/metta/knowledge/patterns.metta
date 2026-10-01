; ==================================
; Threat Patterns
; ==================================

(threat-indicator phishing urgent-threat)
(threat-indicator phishing suspicious-link)
(threat-indicator phishing credential-request)
(threat-indicator phishing fake-domain)
(threat-indicator phishing impersonation)

(threat-indicator account-takeover otp-request)
(threat-indicator account-takeover password-request)
(threat-indicator account-takeover credential-request)

(threat-indicator financial-scam payment-request)
(threat-indicator financial-scam reward-promise)

(threat-indicator malware unknown-attachment)