"""
Baseline implementations for customer support evaluation:
- Baseline 0: Trivial canned response + majority-class intent + always auto-handle.
- Baseline 1: Simple zero-shot keyword matching + generic reply + naive escalation.
"""

from src.config import BASELINE_0_CANNED_REPLY
from src.models import AgentResponse, IntentResult, EscalationVerdict

class Baseline0Trivial:
    """Trivial baseline: majority class, canned response, always auto-handle."""
    def respond(self, tweet_id: str, tweet_text: str) -> AgentResponse:
        intent = IntentResult(
            intent="HARDWARE_BATTERY",
            confidence=0.50,
            rationale="Baseline 0: Fixed majority class prediction.",
            secondary_intents=[]
        )
        escalation = EscalationVerdict(
            should_escalate=False,
            stated_reason="Baseline 0: Default auto-handle policy.",
            risk_level="LOW",
            trigger="STANDARD_RESOLUTION"
        )
        return AgentResponse(
            tweet_id=tweet_id,
            intent_result=intent,
            draft_reply=BASELINE_0_CANNED_REPLY,
            escalation_verdict=escalation,
            retrieved_resolutions=[]
        )

class Baseline1Simple:
    """Simple baseline: single keyword match, ungrounded reply, naive escalation."""
    def respond(self, tweet_id: str, tweet_text: str) -> AgentResponse:
        text_lower = tweet_text.lower()
        
        # Naive keyword matching without ranking or confidence weighting
        intent_name = "OUT_OF_SCOPE_FEEDBACK"
        if "battery" in text_lower or "charge" in text_lower:
            intent_name = "HARDWARE_BATTERY"
        elif "update" in text_lower or "ios" in text_lower:
            intent_name = "SOFTWARE_UPDATE_OS"
        elif "password" in text_lower or "apple id" in text_lower or "icloud" in text_lower:
            intent_name = "ACCOUNT_ICLOUD_SECURITY"
        elif "refund" in text_lower or "charge" in text_lower or "subscription" in text_lower:
            intent_name = "BILLING_SUBSCRIPTIONS"
        elif "wifi" in text_lower or "bluetooth" in text_lower:
            intent_name = "CONNECTIVITY_NETWORK"
        elif "screen" in text_lower or "speaker" in text_lower or "camera" in text_lower:
            intent_name = "DEVICE_PHYSICAL_AUDIO"

        intent = IntentResult(
            intent=intent_name,
            confidence=0.60,
            rationale=f"Baseline 1: Naive rule match for {intent_name}.",
            secondary_intents=[]
        )

        # Naive escalation: only escalates if customer explicitly asks for human/agent/supervisor
        should_esc = any(k in text_lower for k in ["human", "agent", "supervisor", "representative", "person"])
        reason = "Customer explicitly demanded human representative" if should_esc else "Standard automated bot reply"
        
        escalation = EscalationVerdict(
            should_escalate=should_esc,
            stated_reason=reason,
            risk_level="HIGH" if should_esc else "LOW",
            trigger="CUSTOMER_REQUEST" if should_esc else "STANDARD_RESOLUTION"
        )

        # Generic ungrounded template reply
        templates = {
            "HARDWARE_BATTERY": "Hello, please restart your iPhone and check if your battery improves. Let us know if you need anything else.",
            "SOFTWARE_UPDATE_OS": "Hello, make sure you have backed up your device and try running the update again over Wi-Fi.",
            "ACCOUNT_ICLOUD_SECURITY": "Hello, please go to the Apple website to reset your password and check your iCloud settings.",
            "BILLING_SUBSCRIPTIONS": "Hello, you can manage your subscriptions and charges inside your account settings.",
            "CONNECTIVITY_NETWORK": "Hello, please turn your Wi-Fi or Bluetooth off and back on again to test the connection.",
            "DEVICE_PHYSICAL_AUDIO": "Hello, please clean your device screen or speakers and restart your phone.",
            "OUT_OF_SCOPE_FEEDBACK": "Thanks for sharing your thoughts with Apple Support! Have a great day."
        }
        draft_reply = templates.get(intent_name, templates["OUT_OF_SCOPE_FEEDBACK"])

        return AgentResponse(
            tweet_id=tweet_id,
            intent_result=intent,
            draft_reply=draft_reply,
            escalation_verdict=escalation,
            retrieved_resolutions=[]
        )
