"""
Proposed SupportAgent:
Coordinates Intent Classification, Historical RAG Grounding,
Escalation Logic, and Reply Generation with Safety Guardrails.
"""

import time
from typing import Optional, List
from src.models import AgentResponse, IntentResult, EscalationVerdict, HistoricalResolution
from src.classifier import IntentClassifier
from src.retriever import ResolutionRetriever
from src.escalation import EscalationEngine
from src.config import TWITTER_CHAR_LIMIT

class SupportAgent:
    def __init__(self, data_path: str = "data/historical_resolutions.jsonl"):
        self.classifier = IntentClassifier()
        self.retriever = ResolutionRetriever(data_path=data_path)
        self.escalation_engine = EscalationEngine()

    def respond(self, tweet_id: str, tweet_text: str) -> AgentResponse:
        start_time = time.perf_counter()

        # Step 1: Classify Intent
        intent_result: IntentResult = self.classifier.classify(tweet_text)

        # Step 2: Retrieve Top Historical Resolutions (Grounding context)
        retrieved = self.retriever.retrieve(
            query=tweet_text,
            intent_filter=intent_result.intent,
            top_k=2
        )
        top_res: Optional[HistoricalResolution] = retrieved[0][0] if retrieved else None
        top_score: float = retrieved[0][1] if retrieved else 0.0

        # Step 3: Decide Escalation (Auto-Handle vs Escalate)
        escalation: EscalationVerdict = self.escalation_engine.decide(
            tweet_text=tweet_text,
            intent_result=intent_result,
            retrieval_score=top_score
        )

        # Step 4: Draft Grounded Reply
        draft_reply = self._generate_reply(
            tweet_text=tweet_text,
            intent_result=intent_result,
            escalation=escalation,
            top_resolution=top_res
        )

        # Enforce Twitter Length Constraint
        if len(draft_reply) > TWITTER_CHAR_LIMIT:
            draft_reply = draft_reply[:TWITTER_CHAR_LIMIT - 3] + "..."

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return AgentResponse(
            tweet_id=tweet_id,
            intent_result=intent_result,
            draft_reply=draft_reply,
            escalation_verdict=escalation,
            retrieved_resolutions=[r.resolution_id for r, _ in retrieved],
            processing_time_ms=elapsed_ms
        )

    def _generate_reply(
        self,
        tweet_text: str,
        intent_result: IntentResult,
        escalation: EscalationVerdict,
        top_resolution: Optional[HistoricalResolution]
    ) -> str:
        # Case A: Escalation Required
        if escalation.should_escalate:
            if escalation.trigger == "SAFETY_HAZARD":
                return (
                    "Please disconnect the device from power immediately, stop using it, and store it in a cool, "
                    "safe place. Please DM us right away or visit an Apple Store so our safety team can assist directly."
                )
            elif escalation.trigger == "SECURITY_COMPROMISE":
                return (
                    "We take account security very seriously. Please visit iforgot.apple.com immediately to secure "
                    "your account. We are escalating this to our Senior Security Specialists—please DM us your contact number."
                )
            elif escalation.trigger == "LEGAL_RISK":
                return (
                    "We understand your concern regarding these unauthorized transactions. Our specialized billing and "
                    "compliance team will review this directly. Please send us a DM with your case details."
                )
            elif escalation.trigger == "UNRESOLVED_HARDWARE":
                return (
                    "Because this indicates a physical hardware or firmware fault, please meet us in DM with your "
                    "device serial number so we can arrange diagnostics or an Apple Store service appointment."
                )
            elif escalation.trigger == "SENTIMENT_FRUSTRATION":
                return (
                    "We apologize for the frustration this has caused. We want to get this sorted out with you directly. "
                    "Please send us a DM so a senior advisor can take over and assist."
                )
            else: # Low confidence / Ambiguous
                return (
                    "We want to make sure you get the right assistance for this. Please DM us your exact device model "
                    "and software version so one of our advisors can look into this with you."
                )

        # Case B: Auto-Handle using Grounded Historical Knowledge
        if top_resolution:
            # Clean grounded reply using official resolution
            reply = top_resolution.brand_reply
            # Ensure official link is present if relevant
            if top_resolution.official_link and top_resolution.official_link not in reply:
                reply = f"{reply} More info: {top_resolution.official_link}"
            return reply
        
        # Fallback for auto-handle if no close retrieval match
        return (
            "We'd be glad to help. Please restart your device and ensure you're on the latest software version. "
            "If you need additional help, feel free to DM us your details."
        )
