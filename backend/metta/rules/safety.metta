; ==================================
; PolyCyGot Safety Rules
; ==================================

; Unsafe actions become risk actions.
(-> (unsafe-action $action)
    (risk-action $action))

; Specific unsafe actions map to risk categories.
(-> (unsafe-action share-otp)
    (risk-category share-otp credential-theft))

(-> (unsafe-action share-password)
    (risk-category share-password credential-theft))

(-> (unsafe-action share-pin)
    (risk-category share-pin credential-theft))

(-> (unsafe-action share-api-key)
    (risk-category share-api-key secret-disclosure))

(-> (unsafe-action reveal-secret)
    (risk-category reveal-secret secret-disclosure))

(-> (unsafe-action click-suspicious-link)
    (risk-category click-suspicious-link phishing))

(-> (unsafe-action download-unknown-file)
    (risk-category download-unknown-file malware))

(-> (unsafe-action disable-mfa)
    (risk-category disable-mfa account-security))

(-> (unsafe-action bypass-authentication)
    (risk-category bypass-authentication authentication-bypass))

(-> (unsafe-action steal-credentials)
    (risk-category steal-credentials credential-theft))


; Risk categories determine severity.
(-> (risk-category $action credential-theft)
    (risk-level $action high))

(-> (risk-category $action secret-disclosure)
    (risk-level $action high))

(-> (risk-category $action phishing)
    (risk-level $action high))

(-> (risk-category $action malware)
    (risk-level $action high))

(-> (risk-category $action account-security)
    (risk-level $action high))

(-> (risk-category $action authentication-bypass)
    (risk-level $action high))


; Safe actions.
(-> (safe-action-contact-bank)
    (recommended-action contact-bank))

(-> (safe-action-report-phishing)
    (recommended-action report-phishing))

(-> (safe-action-enable-mfa)
    (recommended-action enable-mfa))

(-> (safe-action-change-password)
    (recommended-action change-password))

(-> (safe-action-contact-official-support)
    (recommended-action contact-official-support))
