"""
Intent Classification Engine for AppleSupport Tweets.
Combines domain keyword anchors, semantic phrase patterns, typo tolerance, and confidence estimation.
"""

import re
from typing import Dict, List, Tuple
from src.config import INTENTS, INTENT_DESCRIPTIONS
from src.models import IntentResult

INTENT_KEYWORDS: Dict[str, List[str]] = {
    "HARDWARE_BATTERY": [
        "battery", "drain", "draining", "charge", "charging", "charger", "magsafe", "heat",
        "overheating", "hot", "warm", "percentage", "cycle count", "swollen", "bulging",
        "battery health", "died", "shut off", "shuts down", "shutdown", "shudown", "power off",
        "low power mode", "low power", "clean energy charging", "mfi", "5w", "20w", "watts",
        "turning off", "shuts off", "turns down"
    ],
    "SOFTWARE_UPDATE_OS": [
        "update", "updating", "updated", "ios", "ipados", "macos", "sonoma", "ventura",
        "beta", "restore", "itunes", "finder", "boot loop", "stuck on apple logo",
        "unable to verify", "freeze", "froze", "system data", "downgrade", "error 4013",
        "error 9", "safari", "keyboard lag", "restarting every"
    ],
    "ACCOUNT_ICLOUD_SECURITY": [
        "apple id", "icloud", "password", "locked", "two-factor", "2fa", "verification code",
        "hacked", "stolen", "compromised", "iforgot", "activation lock", "find my",
        "recovery key", "trusted number", "phishing", "sync", "photos not syncing",
        "legacy contact", "stolen device protection", "safety check"
    ],
    "BILLING_SUBSCRIPTIONS": [
        "charge", "charged", "billing", "bill", "subscription", "refund", "receipt",
        "applecare+", "applecare", "apple tv+", "apple music", "in-app", "card declined",
        "payment method", "apple cash", "unauthorized charge", "cost", "cancel subscription",
        "roblox", "reportaproblem", "free trial", "money back", "gift card"
    ],
    "CONNECTIVITY_NETWORK": [
        "wi-fi", "wifi", "bluetooth", "airdrop", "cellular", "no service", "searching",
        "airpods disconnect", "disconnect", "disconnecting", "carplay", "hotspot", "esim",
        "signal", "pairing", "stuttering", "carrier", "airplane mode", "vpn", "5ghz"
    ],
    "DEVICE_PHYSICAL_AUDIO": [
        "screen", "cracked", "broken", "display", "speaker", "sound", "crackling", "mic",
        "microphone", "camera", "black screen", "button", "unresponsive", "touch screen",
        "dead zone", "liquid detected", "water", "dropped", "green line", "taptic", "vibrate",
        "ear speaker", "muffled", "truedepth", "face id"
    ],
    "OUT_OF_SCOPE_FEEDBACK": [
        "trash", "worst", "android", "keynote", "tim cook", "joke", "patent", "student discount",
        "store hours", "hate", "love", "lawyer", "lawsuit", "f***", "scam", "overpriced", "calculator",
        "thanksgiving", "meaning of life"
    ]
}

class IntentClassifier:
    def __init__(self):
        self.intents = INTENTS

    def classify(self, tweet_text: str) -> IntentResult:
        text_lower = tweet_text.lower()
        
        scores: Dict[str, float] = {intent: 0.0 for intent in self.intents}
        matched_terms: Dict[str, List[str]] = {intent: [] for intent in self.intents}

        for intent, kw_list in INTENT_KEYWORDS.items():
            for kw in kw_list:
                pattern = r'\b' + re.escape(kw) + r'\b' if ' ' not in kw else re.escape(kw)
                matches = len(re.findall(pattern, text_lower))
                if matches > 0:
                    weight = 2.5 if len(kw.split()) > 1 else 1.0
                    scores[intent] += matches * weight
                    matched_terms[intent].append(kw)

        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_intent, top_score = sorted_intents[0]
        second_intent, second_score = sorted_intents[1]

        total_score = sum(scores.values())
        if total_score == 0:
            return IntentResult(
                intent="OUT_OF_SCOPE_FEEDBACK",
                confidence=0.45,
                rationale="No strong technical hardware, software, or account keywords detected.",
                secondary_intents=[]
            )

        confidence = round(top_score / (top_score + second_score + 1e-6), 3)
        confidence = min(max(confidence, 0.40), 0.98)

        terms = matched_terms[top_intent][:3]
        rationale = f"Matched dominant keywords {terms} for {top_intent} (score: {top_score:.1f})."
        secondary = [intent for intent, score in sorted_intents[1:3] if score > 0]

        return IntentResult(
            intent=top_intent,
            confidence=confidence,
            rationale=rationale,
            secondary_intents=secondary
        )
