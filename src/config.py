"""
Configuration and taxonomy definitions for the Hiver AI Customer Support Agent.
Brand: AppleSupport
"""

from typing import Dict, List, Set

TARGET_BRAND = "AppleSupport"
BRAND_HANDLE = "@AppleSupport"

# Supported Intent Taxonomy
INTENTS: List[str] = [
    "HARDWARE_BATTERY",
    "SOFTWARE_UPDATE_OS",
    "ACCOUNT_ICLOUD_SECURITY",
    "BILLING_SUBSCRIPTIONS",
    "CONNECTIVITY_NETWORK",
    "DEVICE_PHYSICAL_AUDIO",
    "OUT_OF_SCOPE_FEEDBACK",
]

INTENT_DESCRIPTIONS: Dict[str, str] = {
    "HARDWARE_BATTERY": "Battery drain, overheating, device not charging, battery health percentage, swollen battery.",
    "SOFTWARE_UPDATE_OS": "iOS/macOS update issues, boot loops, frozen update screen, crashing apps post-update.",
    "ACCOUNT_ICLOUD_SECURITY": "Apple ID locked, 2FA code issues, forgotten password, iCloud sync failure, lost phone tracking.",
    "BILLING_SUBSCRIPTIONS": "App Store unexpected charge, refund requests, subscription cancellation, payment method declined.",
    "CONNECTIVITY_NETWORK": "Wi-Fi disconnecting, Bluetooth pairing failure, no cellular reception, AirDrop failing.",
    "DEVICE_PHYSICAL_AUDIO": "Broken screen, unresponsive touchscreen, speaker distortion, mic not working, camera black screen.",
    "OUT_OF_SCOPE_FEEDBACK": "General complaints, feature suggestions, jokes, trolling, or unintelligible rants without support query.",
}

# High-risk escalation keywords that warrant immediate human intervention
CRITICAL_ESCALATION_KEYWORDS: Set[str] = {
    "swollen", "smoke", "exploded", "fire", "injury", "burn", "hazard",  # Safety
    "lawsuit", "lawyer", "attorney", "sue", "court", "fraud", "police",   # Legal / Fraud
    "hacked", "stolen account", "unauthorized transfer", "compromised",    # Security breach
}

# Escalation rules threshold
CONFIDENCE_ESCALATION_THRESHOLD = 0.65
RETRIEVAL_SIMILARITY_THRESHOLD = 0.15

# Response limits
TWITTER_CHAR_LIMIT = 280

# Default canned response for Baseline 0
BASELINE_0_CANNED_REPLY = (
    "Thanks for reaching out! We are here to help. "
    "Please send us a DM with your device model and iOS version so we can take a closer look."
)
