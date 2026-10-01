# MeTTa Safety Layer

PolyCyGot uses MeTTa as a symbolic reasoning layer.

## Why MeTTa?

The neural model is responsible for language understanding and generation.

MeTTa is responsible for deterministic symbolic safety rules.

This creates a neuro-symbolic architecture.

## Knowledge

The knowledge base contains:

- unsafe actions
- safe actions
- threat categories
- threat indicators
- threat patterns

## Rules

Rules connect observed indicators with cybersecurity threats.

Example:

suspicious-link
      +
urgent-threat
      |
      v
phishing

## Verification

Generated responses are checked against safety rules.

Unsafe actions include:

- requesting OTPs
- requesting passwords
- requesting PINs
- disabling MFA
- downloading unknown files
- bypassing authentication

## Reasoning Trail

MeTTa can expose the facts and rules that caused a verification result.

This makes the safety layer inspectable.