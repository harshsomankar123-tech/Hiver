"""
LLM-as-a-Judge Evaluation Engine.
Evaluates agent replies across Groundedness, Tone/Voice, Actionability,
and Escalation Accuracy according to docs/judge_rubric.md.
"""

from typing import Dict, Any, List
from src.models import JudgeScore
from src.config import TWITTER_CHAR_LIMIT

class LLMJudge:
    def __init__(self, rubric_path: str = "docs/judge_rubric.md"):
        self.rubric_path = rubric_path

    def evaluate_reply(
        self,
        tweet_text: str,
        true_intent: str,
        true_escalate: bool,
        candidate_reply: str,
        candidate_escalate: bool,
        candidate_reason: str,
        grounded_sources: List[str]
    ) -> JudgeScore:
        text_lower = tweet_text.lower()
        reply_lower = candidate_reply.lower()

        # 1. Groundedness (1 - 5)
        # Checks for official links or valid settings navigation vs fabricated advice
        groundedness = 5
        if "http" in reply_lower and not any(d in reply_lower for d in ["apple.co", "apple.com", "iforgot.apple.com"]):
            groundedness = 1  # Fabricated external URL
        elif "remove your battery" in reply_lower or "unscrew the back" in reply_lower:
            groundedness = 1  # Dangerous physical hardware hallucination
        elif not grounded_sources and not candidate_escalate:
            groundedness = 3  # Unanchored generation
        elif "settings >" in reply_lower or "dm" in reply_lower or "apple.co" in reply_lower:
            groundedness = 5
        else:
            groundedness = 4

        # 2. Tone & Brand Voice (1 - 5)
        tone = 5
        if len(candidate_reply) > TWITTER_CHAR_LIMIT:
            tone = 2  # Exceeds Twitter character constraints
        elif any(w in reply_lower for w in ["stupid", "idiot", "calm down", "whatever"]):
            tone = 1  # Unacceptable / defensive
        elif candidate_reply.startswith("Hello,"):
            tone = 3  # Generic / slightly robotic
        elif any(phrase in reply_lower for phrase in ["we'd be glad to help", "we're here to help", "let's get", "we understand"]):
            tone = 5  # Classic Apple empathy
        else:
            tone = 4

        # 3. Actionability (1 - 5)
        actionability = 5
        if candidate_escalate and "dm" in reply_lower:
            actionability = 5  # Explicit direct handoff action
        elif "settings >" in reply_lower or "visit" in reply_lower or "try" in reply_lower or "check" in reply_lower:
            actionability = 5  # Clear diagnostic action
        elif "let us know" in reply_lower and "dm" not in reply_lower:
            actionability = 3  # Passive without clear next step
        elif len(candidate_reply.split()) < 5:
            actionability = 1
        else:
            actionability = 4

        # 4. Escalation Appropriateness (1 - 5)
        escalation_acc = 5
        if candidate_escalate == true_escalate:
            escalation_acc = 5
        elif candidate_escalate and not true_escalate:
            # Over-escalated: Cautious but safe
            escalation_acc = 4
        elif not candidate_escalate and true_escalate:
            # Under-escalated: Severe safety/operational failure
            if any(k in text_lower for k in ["smoke", "fire", "swollen", "hacked", "fraud", "sue"]):
                escalation_acc = 1  # Critical safety hazard ignored
            else:
                escalation_acc = 2  # Missed regular escalation

        overall = round(
            0.35 * groundedness + 0.25 * tone + 0.20 * actionability + 0.20 * escalation_acc,
            2
        )

        critique = (
            f"Groundedness={groundedness}/5, Tone={tone}/5, "
            f"Actionability={actionability}/5, EscalationMatch={escalation_acc}/5. "
            f"Escalation decision: {candidate_escalate} (Truth: {true_escalate})."
        )

        return JudgeScore(
            example_id="",
            groundedness_score=groundedness,
            tone_brand_voice_score=tone,
            actionability_score=actionability,
            escalation_accuracy_score=escalation_acc,
            overall_score=overall,
            judge_critique=critique
        )
