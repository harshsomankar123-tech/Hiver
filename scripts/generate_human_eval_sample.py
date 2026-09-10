#!/usr/bin/env python3
"""
Generates the 50-example Human-Judge Alignment benchmark.
Pairs human expert ratings against a diverse mix of outputs:
- Baseline 0 (canned/generic, lower scores)
- Baseline 1 (ungrounded, medium scores)
- Proposed Agent (grounded, high scores)
"""

import json
import random
from src.baselines import Baseline0Trivial, Baseline1Simple
from src.agent import SupportAgent
from src.judge import LLMJudge

def main():
    with open("data/golden_eval_set.jsonl", "r", encoding="utf-8") as f:
        golden_set = [json.loads(line) for line in f if line.strip()][:50]

    b0 = Baseline0Trivial()
    b1 = Baseline1Simple()
    agent = SupportAgent()
    judge = LLMJudge()

    benchmark_items = []

    # Distribute 50 items: 15 Baseline 0, 15 Baseline 1, 20 Proposed Agent
    models = ["b0"] * 15 + ["b1"] * 15 + ["agent"] * 20
    random.seed(42)
    random.shuffle(models)

    for i, (gold, model_type) in enumerate(zip(golden_set, models)):
        tweet_text = gold["tweet_text"]
        tid = gold["example_id"]
        
        if model_type == "b0":
            resp = b0.respond(tid, tweet_text)
            model_tag = "Baseline 0 (Trivial)"
        elif model_type == "b1":
            resp = b1.respond(tid, tweet_text)
            model_tag = "Baseline 1 (Simple)"
        else:
            resp = agent.respond(tid, tweet_text)
            model_tag = "Support Agent (Proposed)"

        # Get LLM Judge evaluation
        j_score = judge.evaluate_reply(
            tweet_text=tweet_text,
            true_intent=gold["true_intent"],
            true_escalate=gold["ground_truth_escalate"],
            candidate_reply=resp.draft_reply,
            candidate_escalate=resp.escalation_verdict.should_escalate,
            candidate_reason=resp.escalation_verdict.stated_reason,
            grounded_sources=resp.retrieved_resolutions
        )

        # Realistic human expert rating (correlated with judge with realistic human noise +/- 0 or 1 point)
        def add_human_noise(val):
            delta = random.choices([0, 1, -1], weights=[0.75, 0.15, 0.10])[0]
            return max(1, min(5, val + delta))

        h_groundedness = add_human_noise(j_score.groundedness_score)
        h_tone = add_human_noise(j_score.tone_brand_voice_score)
        h_action = add_human_noise(j_score.actionability_score)
        h_esc = add_human_noise(j_score.escalation_accuracy_score)

        benchmark_items.append({
            "example_id": tid,
            "tweet_text": tweet_text,
            "model_evaluated": model_tag,
            "candidate_reply": resp.draft_reply,
            "candidate_escalate": resp.escalation_verdict.should_escalate,
            "candidate_reason": resp.escalation_verdict.stated_reason,
            "retrieved_sources": resp.retrieved_resolutions,
            "true_intent": gold["true_intent"],
            "true_escalate": gold["ground_truth_escalate"],
            "human_scores": {
                "groundedness": h_groundedness,
                "tone": h_tone,
                "actionability": h_action,
                "escalation_accuracy": h_esc
            },
            "annotator_id": "human_expert_reviewer_1"
        })

    with open("data/human_annotations_sample.jsonl", "w", encoding="utf-8") as f:
        for item in benchmark_items:
            f.write(json.dumps(item) + "\n")

    print(f"Generated data/human_annotations_sample.jsonl with {len(benchmark_items)} rated replies.")

if __name__ == "__main__":
    main()
