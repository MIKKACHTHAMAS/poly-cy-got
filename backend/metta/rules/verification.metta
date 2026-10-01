; ==================================
; PolyCyGot Verification Rules
; ==================================

; Any risk action is unsafe.
(-> (risk-action $action)
    (verification-unsafe $action))

; Any high-risk action is unsafe.
(-> (risk-level $action high)
    (verification-unsafe $action))

; Unsafe verification results are recorded for auditing.
(-> (verification-unsafe $reason)
    (audit-failed $reason))
