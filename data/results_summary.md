# Benchmark Evaluation Results Summary

### 1. Headline Results vs Baselines

| Model | Intent Macro F1 | Escalation F1 | False-Automation Rate | ROUGE-L | Judge Overall (1-5) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Baseline 0 (Trivial Canned) | 0.049 | 0.000 | 100.0% | 0.318 | 3.64/5.0 |
| Baseline 1 (Simple Zero-Shot) | 0.566 | 0.000 | 100.0% | 0.115 | 3.57/5.0 |
| Proposed Support Agent (RAG) | 0.847 | 0.446 | 60.9% | 0.164 | 4.58/5.0 |

### 2. Operational Safety & Escalation Audit

| Model | Precision | Recall | False-Automation Rate | Over-Escalation Rate |
| :--- | :---: | :---: | :---: | :---: |
| Baseline 0 (Trivial Canned) | 0.000 | 0.000 | 100.0% | 0.0% |
| Baseline 1 (Simple Zero-Shot) | 0.000 | 0.000 | 100.0% | 0.8% |
| Proposed Support Agent (RAG) | 0.519 | 0.391 | 60.9% | 19.1% |

### 3. Human-Judge Agreement Evidence

- **Cohen's Kappa (κ)**: `0.6271`
- **Pearson Correlation (r)**: `0.9284`
- **Exact Agreement**: `79.5%`
- **Mean Absolute Error**: `0.165` points on 1-5 scale
