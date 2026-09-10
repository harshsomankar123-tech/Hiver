"""
Human-Judge Alignment Study.
Measures inter-rater agreement between Human Expert ratings and LLM-as-a-Judge
across Groundedness, Tone, Actionability, and Escalation Accuracy.
Computes Cohen's Kappa, Exact Agreement %, Pearson r, and Mean Absolute Error (MAE).
"""

import json
import math
from typing import List, Dict, Any
from src.judge import LLMJudge

def compute_cohens_kappa(rater1: List[int], rater2: List[int]) -> float:
    """Computes Cohen's Kappa coefficient."""
    assert len(rater1) == len(rater2), "Length mismatch"
    n = len(rater1)
    if n == 0:
        return 0.0

    categories = [1, 2, 3, 4, 5]
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    num_cats = len(categories)

    matrix = [[0] * num_cats for _ in range(num_cats)]
    for r1, r2 in zip(rater1, rater2):
        if r1 in cat_to_idx and r2 in cat_to_idx:
            matrix[cat_to_idx[r1]][cat_to_idx[r2]] += 1

    po = sum(matrix[i][i] for i in range(num_cats)) / n

    pe = 0.0
    for i in range(num_cats):
        row_sum = sum(matrix[i][j] for j in range(num_cats))
        col_sum = sum(matrix[j][i] for j in range(num_cats))
        pe += (row_sum * col_sum) / (n * n)

    if pe >= 1.0:
        return 1.0
    kappa = (po - pe) / (1.0 - pe)
    return round(kappa, 4)

def compute_pearson_r(x: List[float], y: List[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    den_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
    if den_x == 0 or den_y == 0:
        return 1.0 if x == y else 0.0
    return round(num / (den_x * den_y), 4)

def run_alignment_study(data_path: str = "data/human_annotations_sample.jsonl") -> Dict[str, Any]:
    with open(data_path, "r", encoding="utf-8") as f:
        items = [json.loads(line) for line in f if line.strip()]

    judge = LLMJudge()
    dimensions = ["groundedness", "tone", "actionability", "escalation_accuracy"]

    human_scores_by_dim = {d: [] for d in dimensions}
    judge_scores_by_dim = {d: [] for d in dimensions}
    human_overall = []
    judge_overall = []

    for item in items:
        j_score = judge.evaluate_reply(
            tweet_text=item["tweet_text"],
            true_intent=item["true_intent"],
            true_escalate=item["true_escalate"],
            candidate_reply=item["candidate_reply"],
            candidate_escalate=item["candidate_escalate"],
            candidate_reason=item["candidate_reason"],
            grounded_sources=item.get("retrieved_sources", [])
        )

        h_scores = item["human_scores"]

        human_scores_by_dim["groundedness"].append(h_scores["groundedness"])
        human_scores_by_dim["tone"].append(h_scores["tone"])
        human_scores_by_dim["actionability"].append(h_scores["actionability"])
        human_scores_by_dim["escalation_accuracy"].append(h_scores["escalation_accuracy"])

        judge_scores_by_dim["groundedness"].append(j_score.groundedness_score)
        judge_scores_by_dim["tone"].append(j_score.tone_brand_voice_score)
        judge_scores_by_dim["actionability"].append(j_score.actionability_score)
        judge_scores_by_dim["escalation_accuracy"].append(j_score.escalation_accuracy_score)

        h_ov = (
            0.35 * h_scores["groundedness"]
            + 0.25 * h_scores["tone"]
            + 0.20 * h_scores["actionability"]
            + 0.20 * h_scores["escalation_accuracy"]
        )
        human_overall.append(round(h_ov, 2))
        judge_overall.append(j_score.overall_score)

    dim_results = {}
    kappas = []
    agreements = []

    for d in dimensions:
        h_vals = human_scores_by_dim[d]
        j_vals = judge_scores_by_dim[d]
        exact_match = sum(1 for h, j in zip(h_vals, j_vals) if h == j)
        within_1_point = sum(1 for h, j in zip(h_vals, j_vals) if abs(h - j) <= 1)
        kappa = compute_cohens_kappa(h_vals, j_vals)
        mae = round(sum(abs(h - j) for h, j in zip(h_vals, j_vals)) / len(h_vals), 3)

        dim_results[d] = {
            "cohens_kappa": kappa,
            "exact_agreement_pct": round(exact_match / len(h_vals) * 100, 1),
            "adjacent_agreement_pct": round(within_1_point / len(h_vals) * 100, 1),
            "mae": mae
        }
        kappas.append(kappa)
        agreements.append(round(exact_match / len(h_vals) * 100, 1))

    overall_r = compute_pearson_r(human_overall, judge_overall)
    overall_mae = round(sum(abs(h - j) for h, j in zip(human_overall, judge_overall)) / len(human_overall), 3)

    return {
        "sample_size": len(items),
        "mean_cohens_kappa": round(sum(kappas) / len(kappas), 4),
        "mean_exact_agreement_pct": round(sum(agreements) / len(agreements), 1),
        "overall_pearson_r": overall_r,
        "overall_mae": overall_mae,
        "per_dimension_results": dim_results
    }

if __name__ == "__main__":
    res = run_alignment_study()
    print("=== Human-Judge Alignment Calibration Results ===")
    print(json.dumps(res, indent=2))
