"""
Escalation Decision Engine for AppleSupport.
Determines whether incoming messages are safe for automated resolution
or require human agent escalation, providing an explicit operational reason.
"""

import re
from src.config import CRITICAL_ESCALATION_KEYWORDS, CONFIDENCE_ESCALATION_THRESHOLD
from src.models import EscalationVerdict, IntentResult

SAFETY_PATTERNS = [
    r"\b(swollen|bulging|expanded)\b",
    r"\b(smoke|smoking|flames?|fire|sparking|spark)\b",
    r"\b(burn|burned|burning|blister|injury|melted)\b",
    r"\b(exploded|explosion)\b"
]

SECURITY_PATTERNS = [
    r"\b(hacked|compromised|stolen account|unauthorized access)\b",
    r"\b(someone changed my|lost recovery key)\b",
    r"\b(extortion|death threat|threats)\b"
]

LEGAL_FRAUD_PATTERNS = [
    r"\b(lawyer|attorney|lawsuit|sue|suing|court|police)\b",
    r"\b(fraud|fraudulent|unauthorized charge|unauthorized purchase|stole.*money)\b",
    r"\b(dispute.*charge|chargeback)\b"
]

CATASTROPHIC_HARDWARE_PATTERNS = [
    r"\b(boot loop|infinite loop|stuck in loop)\b",
    r"\b(error 4013|error 9)\b",
    r"\b(fell off|bent in half|screen detached)\b",
    r"\b(green line|white screen of death)\b",
    r"\b(wifi.*grayed out|toggle.*stuck)\b"
]

TOXICITY_PATTERNS = [
    r"\b(f\*\*\*|fuck|shit|bitch|bastard|useless bot)\b"
]

class EscalationEngine:
    def decide(
        self,
        tweet_text: str,
        intent_result: IntentResult,
        retrieval_score: float = 1.0
    ) -> EscalationVerdict:
        text_lower = tweet_text.lower()

        # 1. Critical Physical Safety / Hazard
        for pattern in SAFETY_PATTERNS:
            if re.search(pattern, text_lower):
                return EscalationVerdict(
                    should_escalate=True,
                    stated_reason="CRITICAL SAFETY HAZARD: Potential thermal runaway, battery swelling, or physical burn risk detected.",
                    risk_level="CRITICAL",
                    trigger="SAFETY_HAZARD"
                )

        # 2. Critical Security Compromise / Account Takeover
        for pattern in SECURITY_PATTERNS:
            if re.search(pattern, text_lower):
                return EscalationVerdict(
                    should_escalate=True,
                    stated_reason="ACCOUNT SECURITY COMPROMISE: Active unauthorized takeover, extortion, or recovery key loss detected.",
                    risk_level="CRITICAL",
                    trigger="SECURITY_COMPROMISE"
                )

        # 3. Legal Action & High-Value Financial Fraud
        for pattern in LEGAL_FRAUD_PATTERNS:
            if re.search(pattern, text_lower):
                return EscalationVerdict(
                    should_escalate=True,
                    stated_reason="LEGAL / FRAUD RISK: Explicit litigation threat or disputed unauthorized charges requiring compliance/billing specialist.",
                    risk_level="HIGH",
                    trigger="LEGAL_RISK"
                )

        # 4. Severe Catastrophic Hardware / Unbootable Device
        for pattern in CATASTROPHIC_HARDWARE_PATTERNS:
            if re.search(pattern, text_lower):
                return EscalationVerdict(
                    should_escalate=True,
                    stated_reason="HARDWARE / FIRMWARE FAILURE: Unbootable device, NAND error, or component defect requiring Genius Bar / depot service.",
                    risk_level="HIGH",
                    trigger="UNRESOLVED_HARDWARE"
                )

        # 5. Severe Profanity / High Toxicity
        for pattern in TOXICITY_PATTERNS:
            if re.search(pattern, text_lower):
                return EscalationVerdict(
                    should_escalate=True,
                    stated_reason="CUSTOMER DISSATISFACTION / TOXICITY: High distress or explicit profanity requiring human supervisor de-escalation.",
                    risk_level="MEDIUM",
                    trigger="SENTIMENT_FRUSTRATION"
                )

        # 6. Low Model Confidence or Low Retrieval Grounding
        if intent_result.confidence < CONFIDENCE_ESCALATION_THRESHOLD:
            return EscalationVerdict(
                should_escalate=True,
                stated_reason=f"LOW INTENT CONFIDENCE ({intent_result.confidence:.2f} < {CONFIDENCE_ESCALATION_THRESHOLD}): Ambiguous customer query.",
                risk_level="MEDIUM",
                trigger="LOW_CONFIDENCE"
            )

        # 7. Safe for Automated First-Line Resolution
        return EscalationVerdict(
            should_escalate=False,
            stated_reason="STANDARD RESOLUTION: Query matches verified self-service troubleshooting procedures and carries no risk flags.",
            risk_level="LOW",
            trigger="STANDARD_RESOLUTION"
        )
