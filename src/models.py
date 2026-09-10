"""
Core data structures for the Hiver AI Support Agent.
Uses dataclasses for zero-dependency portability and high performance.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any

@dataclass
class CustomerTweet:
    tweet_id: str
    text: str
    author_id: Optional[str] = None
    created_at: Optional[str] = None
    in_response_to_tweet_id: Optional[str] = None

@dataclass
class IntentResult:
    intent: str
    confidence: float
    rationale: str
    secondary_intents: List[str] = field(default_factory=list)

@dataclass
class HistoricalResolution:
    resolution_id: str
    customer_query: str
    brand_reply: str
    intent: str
    action_type: str  # e.g., "troubleshooting_steps", "dm_request", "official_link"
    official_link: Optional[str] = None

@dataclass
class EscalationVerdict:
    should_escalate: bool
    stated_reason: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    trigger: str     # "SAFETY_HAZARD", "LEGAL_RISK", "SECURITY_COMPROMISE", "LOW_CONFIDENCE", "SENTIMENT_FRUSTRATION", "STANDARD_RESOLUTION"

@dataclass
class AgentResponse:
    tweet_id: str
    intent_result: IntentResult
    draft_reply: str
    escalation_verdict: EscalationVerdict
    retrieved_resolutions: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GoldenExample:
    example_id: str
    tweet_text: str
    true_intent: str
    ground_truth_escalate: bool
    ground_truth_reason: str
    reference_reply: str
    difficulty_tier: str  # "easy", "medium", "hard_ambiguous"
    category_notes: str = ""

@dataclass
class JudgeScore:
    example_id: str
    groundedness_score: int       # 1-5
    tone_brand_voice_score: int   # 1-5
    actionability_score: int      # 1-5
    escalation_accuracy_score: int # 1-5
    overall_score: float
    judge_critique: str

@dataclass
class HumanAnnotation:
    example_id: str
    groundedness_score: int
    tone_brand_voice_score: int
    actionability_score: int
    escalation_accuracy_score: int
    annotator_notes: str = ""
