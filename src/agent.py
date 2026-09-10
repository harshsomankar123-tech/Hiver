"""
Production SupportAgent:
Coordinates Intent Classification, Historical RAG Grounding,
Escalation Logic, and Live Gemini LLM Generation.
"""

import time
from typing import Optional, List, Dict, Any
from src.models import AgentResponse, IntentResult, EscalationVerdict, HistoricalResolution
from src.classifier import IntentClassifier
from src.retriever import ResolutionRetriever
from src.escalation import EscalationEngine
from src.llm_client import LLMClient

SYSTEM_PROMPT = """You are the official @AppleSupport customer support assistant on Apple Chat.
Your job is to assist Apple customers with technical troubleshooting, hardware/software questions, Apple IDs, and purchasing guidance.
GUIDELINES:
1. Speak in Apple's authentic brand voice: calm, empathetic, professional, clear, and highly helpful.
2. If the user asks for specs, products, or options, explain the actual current Apple lineup clearly and concisely (e.g. MacBook Air M2/M3, MacBook Pro M3/M3 Pro/M3 Max with unified memory and Liquid Retina displays).
3. If the issue is a dangerous hazard (smoke, swelling battery, fire, active account hack), advise them to stop using the device and direct them to an Apple Store or emergency support.
4. NEVER invent fake URLs or fake policies. Use official Apple links (e.g. apple.com/mac, apple.co/battery-health, iforgot.apple.com).
"""

class SupportAgent:
    def __init__(self, data_path: str = "data/historical_resolutions.jsonl"):
        self.classifier = IntentClassifier()
        self.retriever = ResolutionRetriever(data_path=data_path)
        self.escalation_engine = EscalationEngine()
        self.llm_client = LLMClient()

    def respond(self, tweet_id: str, tweet_text: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> AgentResponse:
        start_time = time.perf_counter()
        history = conversation_history or []

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

        # Step 4: Generate Reply (Use Live Gemini LLM if configured!)
        draft_reply = None
        if self.llm_client.is_configured():
            context_docs = ""
            if top_res:
                context_docs = f"Relevant Official Resolution: {top_res.brand_reply}\nOfficial Link: {top_res.official_link or 'None'}"
            
            draft_reply = self.llm_client.generate_chat(
                system_prompt=SYSTEM_PROMPT,
                conversation_history=history,
                user_message=tweet_text,
                context_docs=context_docs
            )

        # Fallback to local rule engine if LLM is unavailable or offline
        if not draft_reply:
            draft_reply = self._generate_fallback(
                tweet_text=tweet_text,
                intent_result=intent_result,
                escalation=escalation,
                top_resolution=top_res
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return AgentResponse(
            tweet_id=tweet_id,
            intent_result=intent_result,
            draft_reply=draft_reply,
            escalation_verdict=escalation,
            retrieved_resolutions=[r.resolution_id for r, _ in retrieved],
            processing_time_ms=elapsed_ms
        )

    def _generate_fallback(
        self,
        tweet_text: str,
        intent_result: IntentResult,
        escalation: EscalationVerdict,
        top_resolution: Optional[HistoricalResolution]
    ) -> str:
        text_lower = tweet_text.lower()
        if "spec" in text_lower or "macbook" in text_lower:
            return "Current MacBook lineup features the M3, M3 Pro, and M3 Max chips offering up to 22 hours of battery life, Liquid Retina XDR displays, and unified memory up to 128GB. Check full specs: https://apple.com/mac"

        if escalation.should_escalate:
            if escalation.trigger == "SAFETY_HAZARD":
                return "Please disconnect the device from power immediately, stop using it, and store it in a cool, safe place. Please DM us right away or visit an Apple Store so our safety team can assist directly."
            elif escalation.trigger == "SECURITY_COMPROMISE":
                return "We take account security very seriously. Please visit iforgot.apple.com immediately to secure your account. We are escalating this to our Senior Security Specialists—please DM us your contact number."
            elif escalation.trigger == "LEGAL_RISK":
                return "We understand your concern regarding these unauthorized transactions. Our specialized billing and compliance team will review this directly. Please send us a DM with your case details."
            else:
                return "We want to make sure you get the right assistance for this. Please DM us your exact device model and software version so one of our advisors can look into this with you."

        if top_resolution:
            reply = top_resolution.brand_reply
            if top_resolution.official_link and top_resolution.official_link not in reply:
                reply = f"{reply} More info: {top_resolution.official_link}"
            return reply

        return "We'd be glad to help. Please restart your device and ensure you're on the latest software version. Feel free to DM us your details."
