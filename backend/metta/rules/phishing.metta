; ==================================
; Phishing Rules
; ==================================

(-> (threat-indicator phishing suspicious-link)
    (phishing-signal suspicious-link))

(-> (threat-indicator phishing urgent-threat)
    (phishing-signal urgency))

(-> (threat-indicator phishing credential-request)
    (phishing-signal credentials))

(-> (threat-indicator phishing fake-domain)
    (phishing-signal fake-domain))

(-> (phishing-signal suspicious-link)
    (phishing-risk high))

(-> (phishing-signal credentials)
    (phishing-risk high))