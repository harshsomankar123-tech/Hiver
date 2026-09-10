"""
Automated Evaluation Harness.
Computes Intent Classification Metrics (Macro F1, Per-class F1),
Escalation Metrics (Precision, Recall, F1, False Automation Rate),
Lexical Overlap (ROUGE/Jaccard), and Latency.
"""

from typing import List, Dict, Any
from collections import defaultdict
import re

def tokenize(text: str) -> List[str]:
    return re.findall(r'\b[a-z0-9]+\b', text.lower())

def compute_f1(tp: int, fp: int, fn: int) -> Dict[str, float]:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}

def rouge_l_score(hypothesis: str, reference: str) -> float:
    """Compute token-level Longest Common Subsequence (LCS) ratio."""
    hyp_tokens = tokenize(hypothesis)
    ref_tokens = tokenize(reference)
    if not hyp_tokens or not ref_tokens:
        return 0.0
    
    m, n = len(hyp_tokens), len(ref_tokens)
    # Optimized 1D LCS buffer
    dp = [0] * (n + 1)
    for i in range(1, m + 1):
        prev = 0
        for j in range(1, n + 1):
            temp = dp[j]
            if hyp_tokens[i - 1] == ref_tokens[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = temp
    lcs = dp[n]
    prec = lcs / m
    rec = lcs / n
    return (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

class AutomatedEvaluator:
    @staticmethod
    def evaluate(
        model_name: str,
        predictions: List[Dict[str, Any]],
        golden_set: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        total = len(golden_set)
        assert len(predictions) == total, f"Mismatched counts: {len(predictions)} vs {total}"

        # 1. Intent Metrics
        intent_tp = defaultdict(int)
        intent_fp = defaultdict(int)
        intent_fn = defaultdict(int)
        all_intents = set()
        intent_correct = 0

        # 2. Escalation Metrics
        # Ground truth: True = Escalate, False = Auto-handle
        esc_tp = 0  # correctly escalated
        esc_fp = 0  # escalated when should auto-handle (over-escalation)
        esc_fn = 0  # auto-handled when should escalate (CRITICAL: False Automation)
        esc_tn = 0  # correctly auto-handled

        # 3. Text Quality & Latency
        rouge_scores = []
        latencies = []

        for pred, gold in zip(predictions, golden_set):
            true_intent = gold["true_intent"]
            pred_intent = pred["intent_result"]["intent"]
            all_intents.add(true_intent)
            all_intents.add(pred_intent)

            if pred_intent == true_intent:
                intent_correct += 1
                intent_tp[true_intent] += 1
            else:
                intent_fp[pred_intent] += 1
                intent_fn[true_intent] += 1

            # Escalation
            true_esc = gold["ground_truth_escalate"]
            pred_esc = pred["escalation_verdict"]["should_escalate"]

            if pred_esc and true_esc:
                esc_tp += 1
            elif pred_esc and not true_esc:
                esc_fp += 1
            elif not pred_esc and true_esc:
                esc_fn += 1
            else:
                esc_tn += 1

            # ROUGE-L
            ref_text = gold["reference_reply"]
            cand_text = pred["draft_reply"]
            rouge_scores.append(rouge_l_score(cand_text, ref_text))

            latencies.append(pred.get("processing_time_ms", 0.0))

        # Compute Intent Macro F1
        intent_f1s = []
        per_intent_metrics = {}
        for it in all_intents:
            m = compute_f1(intent_tp[it], intent_fp[it], intent_fn[it])
            per_intent_metrics[it] = m
            intent_f1s.append(m["f1"])
        macro_intent_f1 = round(sum(intent_f1s) / len(intent_f1s), 4) if intent_f1s else 0.0
        intent_accuracy = round(intent_correct / total, 4)

        # Compute Escalation Metrics
        esc_metrics = compute_f1(esc_tp, esc_fp, esc_fn)
        esc_accuracy = round((esc_tp + esc_tn) / total, 4)
        
        # False Automation Rate = esc_fn / total ground truth escalations
        total_ground_truth_esc = (esc_tp + esc_fn)
        false_automation_rate = round(esc_fn / total_ground_truth_esc, 4) if total_ground_truth_esc > 0 else 0.0
        
        # Over-Escalation Rate = esc_fp / total ground truth auto-handles
        total_ground_truth_auto = (esc_fp + esc_tn)
        over_escalation_rate = round(esc_fp / total_ground_truth_auto, 4) if total_ground_truth_auto > 0 else 0.0

        avg_rouge_l = round(sum(rouge_scores) / total, 4)
        avg_latency = round(sum(latencies) / total, 2)

        return {
            "model_name": model_name,
            "total_examples": total,
            "intent_accuracy": intent_accuracy,
            "intent_macro_f1": macro_intent_f1,
            "per_intent_metrics": per_intent_metrics,
            "escalation_accuracy": esc_accuracy,
            "escalation_precision": esc_metrics["precision"],
            "escalation_recall": esc_metrics["recall"],
            "escalation_f1": esc_metrics["f1"],
            "false_automation_rate": false_automation_rate,
            "over_escalation_rate": over_escalation_rate,
            "avg_rouge_l": avg_rouge_l,
            "avg_latency_ms": avg_latency
        }
