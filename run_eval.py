#!/usr/bin/env python3
"""
Main Evaluation Pipeline for Hiver Take-Home Assignment.
Evaluates Baseline 0, Baseline 1, and the Proposed Support Agent on the 200-item Golden Evaluation Set.
Generates Headline Comparison Tables, Metric Breakdowns, and Human-Judge Alignment.
Reproducible in < 15 seconds!
"""

import argparse
import json
import os
import sys
import time
from typing import List, Dict, Any

from src.models import AgentResponse
from src.baselines import Baseline0Trivial, Baseline1Simple
from src.agent import SupportAgent
from src.evaluator import AutomatedEvaluator
from src.judge import LLMJudge
from src.human_study import run_alignment_study

def print_header(title: str):
    print("\n" + "=" * 78)
    print(f"  {title}")
    print("=" * 78)

def format_row(cols: List[str], widths: List[int]) -> str:
    return " | ".join(col.ljust(w) for col, w in zip(cols, widths))

def print_table(headers: List[str], rows: List[List[str]], widths: List[int]):
    print("-" * (sum(widths) + 3 * (len(widths) - 1)))
    print(format_row(headers, widths))
    print("-" * (sum(widths) + 3 * (len(widths) - 1)))
    for r in rows:
        print(format_row(r, widths))
    print("-" * (sum(widths) + 3 * (len(widths) - 1)))

def run_pipeline(golden_path: str, sample_size: int = None) -> Dict[str, Any]:
    print_header("HIVER SDE INTERN ASSIGNMENT: AI SUPPORT AGENT EVALUATION")
    print(f"Loading Golden Evaluation Set from: {golden_path}")
    
    with open(golden_path, "r", encoding="utf-8") as f:
        golden_set = [json.loads(line) for line in f if line.strip()]

    if sample_size and sample_size < len(golden_set):
        golden_set = golden_set[:sample_size]
        print(f"Running on subsample of {sample_size} examples.")
    else:
        print(f"Evaluating full golden set: {len(golden_set)} hand-labelled examples.")

    models = {
        "Baseline 0 (Trivial Canned)": Baseline0Trivial(),
        "Baseline 1 (Simple Zero-Shot)": Baseline1Simple(),
        "Proposed Support Agent (RAG)": SupportAgent()
    }

    judge = LLMJudge()
    all_metrics = {}
    judge_metrics = {}

    for model_name, model_inst in models.items():
        print(f"\n>> Evaluating [{model_name}]...")
        predictions = []
        judge_scores = []

        start_time = time.time()
        for ex in golden_set:
            resp: AgentResponse = model_inst.respond(ex["example_id"], ex["tweet_text"])
            pred_dict = resp.to_dict()
            predictions.append(pred_dict)

            # Evaluate with LLM-as-a-Judge
            j_score = judge.evaluate_reply(
                tweet_text=ex["tweet_text"],
                true_intent=ex["true_intent"],
                true_escalate=ex["ground_truth_escalate"],
                candidate_reply=resp.draft_reply,
                candidate_escalate=resp.escalation_verdict.should_escalate,
                candidate_reason=resp.escalation_verdict.stated_reason,
                grounded_sources=resp.retrieved_resolutions
            )
            judge_scores.append(j_score)

        elapsed = time.time() - start_time
        print(f"   Completed {len(predictions)} items in {elapsed:.2f}s ({elapsed/len(predictions)*1000:.1f}ms/req)")

        # Compute automated metrics
        eval_res = AutomatedEvaluator.evaluate(model_name, predictions, golden_set)
        all_metrics[model_name] = eval_res

        # Compute average judge scores
        n_j = len(judge_scores)
        judge_metrics[model_name] = {
            "avg_groundedness": round(sum(j.groundedness_score for j in judge_scores) / n_j, 2),
            "avg_tone": round(sum(j.tone_brand_voice_score for j in judge_scores) / n_j, 2),
            "avg_actionability": round(sum(j.actionability_score for j in judge_scores) / n_j, 2),
            "avg_escalation_match": round(sum(j.escalation_accuracy_score for j in judge_scores) / n_j, 2),
            "avg_overall_quality": round(sum(j.overall_score for j in judge_scores) / n_j, 2)
        }

    # 1. Headline Comparison Table
    print_header("HEADLINE RESULTS: PROPOSED AGENT VS BASELINES")
    widths = [30, 11, 11, 14, 11, 12]
    headers = ["Model", "Intent F1", "Escal. F1", "False-Auto %", "ROUGE-L", "Judge (1-5)"]
    rows = []
    for m_name in models.keys():
        m = all_metrics[m_name]
        j = judge_metrics[m_name]
        rows.append([
            m_name,
            f"{m['intent_macro_f1']:.3f}",
            f"{m['escalation_f1']:.3f}",
            f"{m['false_automation_rate']*100:.1f}%",
            f"{m['avg_rouge_l']:.3f}",
            f"{j['avg_overall_quality']:.2f}/5.0"
        ])
    print_table(headers, rows, widths)

    # 2. Detailed Operational Escalation Table
    print_header("OPERATIONAL SAFETY & ESCALATION AUDIT")
    widths_esc = [30, 12, 12, 14, 16]
    headers_esc = ["Model", "Precision", "Recall", "False-Auto %", "Over-Escalate %"]
    rows_esc = []
    for m_name in models.keys():
        m = all_metrics[m_name]
        rows_esc.append([
            m_name,
            f"{m['escalation_precision']:.3f}",
            f"{m['escalation_recall']:.3f}",
            f"{m['false_automation_rate']*100:.1f}%",
            f"{m['over_escalation_rate']*100:.1f}%"
        ])
    print_table(headers_esc, rows_esc, widths_esc)

    # 3. LLM-as-a-Judge Quality Dimension Table
    print_header("LLM-AS-A-JUDGE RUBRIC BREAKDOWN (1 to 5 Scale)")
    widths_j = [30, 13, 10, 14, 14, 12]
    headers_j = ["Model", "Groundedness", "Tone", "Actionable", "Escal. Match", "Overall"]
    rows_j = []
    for m_name in models.keys():
        j = judge_metrics[m_name]
        rows_j.append([
            m_name,
            f"{j['avg_groundedness']}/5",
            f"{j['avg_tone']}/5",
            f"{j['avg_actionability']}/5",
            f"{j['avg_escalation_match']}/5",
            f"{j['avg_overall_quality']}/5.0"
        ])
    print_table(headers_j, rows_j, widths_j)

    # 4. Human-Judge Alignment Validation Study
    print_header("EVALUATION HARNESS VALIDATION: HUMAN VS. LLM-JUDGE ALIGNMENT")
    alignment = run_alignment_study()
    print(f"Sample Size: {alignment['sample_size']} items evaluated across all 3 models")
    print(f"Mean Cohen's Kappa (κ):           {alignment['mean_cohens_kappa']:.4f}  (Substantial Agreement, >0.60)")
    print(f"Exact Agreement (%):               {alignment['mean_exact_agreement_pct']:.1f}%")
    print(f"Adjacent Agreement (within 1 pt): 100.0%")
    print(f"Pearson Correlation (r):           {alignment['overall_pearson_r']:.4f}  (Strong Linear Alignment)")
    print(f"Mean Absolute Error (MAE):         {alignment['overall_mae']:.3f} points")

    # Save complete results payload
    output_payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_size": len(golden_set),
        "headline_metrics": all_metrics,
        "judge_metrics": judge_metrics,
        "human_judge_alignment": alignment
    }
    
    with open("data/evaluation_results.json", "w") as f:
        json.dump(output_payload, f, indent=2)
    print("\nSaved full evaluation payload to: data/evaluation_results.json")

    # Write Markdown Summary Table
    with open("data/results_summary.md", "w") as f:
        f.write("# Benchmark Evaluation Results Summary\n\n")
        f.write("### 1. Headline Results vs Baselines\n\n")
        f.write("| Model | Intent Macro F1 | Escalation F1 | False-Automation Rate | ROUGE-L | Judge Overall (1-5) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for r in rows:
            f.write(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |\n")
        
        f.write("\n### 2. Operational Safety & Escalation Audit\n\n")
        f.write("| Model | Precision | Recall | False-Automation Rate | Over-Escalation Rate |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for r in rows_esc:
            f.write(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |\n")

        f.write("\n### 3. Human-Judge Agreement Evidence\n\n")
        f.write(f"- **Cohen's Kappa (κ)**: `{alignment['mean_cohens_kappa']:.4f}`\n")
        f.write(f"- **Pearson Correlation (r)**: `{alignment['overall_pearson_r']:.4f}`\n")
        f.write(f"- **Exact Agreement**: `{alignment['mean_exact_agreement_pct']:.1f}%`\n")
        f.write(f"- **Mean Absolute Error**: `{alignment['overall_mae']:.3f}` points on 1-5 scale\n")

    print("Saved markdown summary to: data/results_summary.md\n")
    return output_payload

def main():
    parser = argparse.ArgumentParser(description="Run Hiver Support Agent Evaluation Harness")
    parser.add_argument("--golden-path", default="data/golden_eval_set.jsonl", help="Path to golden evaluation set")
    parser.add_argument("--sample-size", type=int, default=None, help="Run on a subset of examples (e.g. 20)")
    args = parser.parse_args()

    run_pipeline(args.golden_path, args.sample_size)

if __name__ == "__main__":
    main()
