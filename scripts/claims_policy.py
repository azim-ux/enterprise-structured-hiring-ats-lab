#!/usr/bin/env python3
"""Contextual policy for public capability claims in portfolio artifacts."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimRule:
    identifier: str
    pattern: re.Pattern


@dataclass(frozen=True)
class ClaimFinding:
    rule: str


def _rule(identifier, pattern):
    return ClaimRule(identifier, re.compile(pattern, re.IGNORECASE))


# Target affirmative implementation or outcome language. Discussion remains
# allowed when a control is clearly proposed, required, absent, or unvalidated.
GOVERNED_CLAIM_RULES = (
    _rule("production-system", r"\b(?:a |an )?privacy-first enterprise hiring system\b"),
    _rule("runtime-knockout", r"\bblind automated knockout\b"),
    _rule("operational-erasure", r"\btransfer\s*\+\s*purge\b"),
    _rule("runtime-demographic-isolation", r"\bcohorts hidden from screeners and panels\b"),
    _rule("operational-erasure", r"\brejected résumés queued for 180-day purge\b"),
    _rule("implemented-rbac", r"\breceive separated permissions\b"),
    _rule("operational-workflow", r"\bwhat operators can run\b"),
    _rule("operational-governance", r"\bwhat HRIS teams can govern\b"),
    _rule(
        "implemented-sensitive-control",
        r"\b(?:implements?|enforces?|provides?) (?:runtime )?"
        r"(?:RBAC|role-based access|encryption|immutable audit logging|"
        r"retention|erasure|backups?|disaster recovery|incident response|"
        r"production integrations?)\b",
    ),
    _rule("legal-compliance", r"\b(?:is|are|ensures?|guarantees?) (?:legally |regulatory )?compliant\b"),
    _rule("validated-fairness", r"\b(?:validated fairness|bias-free|eliminates bias)\b"),
    _rule("predictive-validity", r"\bpredictive validity (?:is|was) (?:proven|established|validated)\b"),
    _rule("accessibility-conformance", r"\b(?:WCAG|accessibility) (?:compliant|conformant|certified)\b"),
)

QUALIFYING_CONTEXT = re.compile(
    r"(?:\bno\b|not (?:proof|a claim)|does not|do not|proposed|documented production "
    r"requirement|requires independent)[^.]{0,400}$",
    re.IGNORECASE,
)


def evaluate_claims(text):
    """Return privacy-safe rule identifiers for unsupported affirmative claims."""
    findings = []
    for rule in GOVERNED_CLAIM_RULES:
        for match in rule.pattern.finditer(text):
            prefix = text[max(0, match.start() - 400):match.start()]
            if QUALIFYING_CONTEXT.search(prefix):
                continue
            findings.append(ClaimFinding(rule.identifier))
    return list(dict.fromkeys(findings))
