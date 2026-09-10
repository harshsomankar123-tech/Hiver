# Production-Grade AI Customer Support Agent & Rigorous Evaluation Pipeline

An end-to-end AI customer support agent for **`@AppleSupport`** on Twitter/X that turns noisy real-world customer tweets into structured, grounded, and safe customer support resolutions.

---

## Quickstart: Reproduce Headline Results in < 15 Seconds

The entire core evaluation pipeline runs out-of-the-box using the **Python standard library** with zero heavy server or API key requirements.

```bash
# 1. Clone repository
git clone https://github.com/harshsomankar123-tech/Hiver.git
cd Hiver

# 2. (Optional) Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Run the complete evaluation benchmark (runs in ~0.5s)
python3 run_eval.py
```

### Run Unit Tests
```bash
python3 -m unittest discover -s tests -v
```

---

## Headline Benchmark Results

Evaluated across the **200 hand-curated Golden Evaluation Set** (51.5% Easy, 30.0% Medium, 18.5% Hard/Ambiguous):

| Model | Intent Macro F1 | Escalation F1 | False-Auto Rate | ROUGE-L | LLM Judge (1-5) | Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline 0 (Trivial Canned)** | 0.049 | 0.000 | 100.0% | 0.318 | 3.64 / 5.0 | 0.01 ms |
| **Baseline 1 (Simple Zero-Shot)** | 0.566 | 0.000 | 100.0% | 0.115 | 3.57 / 5.0 | 0.01 ms |
| **Proposed Support Agent (RAG)** | **0.847** | **0.446** | **60.9%** | **0.158** | **4.56 / 5.0** | **0.55 ms** |

### Operational Escalation & Safety Breakdown
* **False Automation Rate**: Dropped significantly compared to baselines (which failed on 100% of high-risk cases).
* **LLM-as-a-Judge Groundedness**: Reached **5.0/5.0** due to strict RAG grounding over verified historical Apple resolutions.
* **Human-Judge Agreement Calibration**:
  * **Cohen's Kappa (κ)**: `0.6271` (*Substantial Agreement*, >0.60 standard)
  * **Pearson Correlation (r)**: `0.9284` (*Strong Linear Alignment*)
  * **Adjacent Score Match**: `100.0%` (within ±1 point on 1–5 scale)

---

## Dual-Mode Architecture & Execution

The agent operates in two interchangeable execution modes designed for high reliability and zero-configuration benchmarking:

1. **Live Cloud LLM Mode (Google Gemini & OpenAI ChatGPT)**:
   - When an API key (`GEMINI_API_KEY` or `OPENAI_API_KEY`) is configured in `.env`, the agent uses **Google Gemini 2.5 Flash** or **OpenAI GPT-4o-mini** to synthesize conversational, brand-aligned customer responses.
   - Retrieved official resolutions from the historical corpus are injected directly into the LLM system prompt as verified grounding context, preventing hallucinations and ensuring factual accuracy.
   - Features multi-turn context retention across up to 6 dialogue turns for interactive troubleshooting.
   - Built with native standard-library HTTP clients (`urllib.request`) and an 8-second timeout, failing over silently to offline mode if the external API is unreachable.

2. **Offline Local Deterministic Fallback Mode (Zero API Keys Required)**:
   - When no API keys are provided, the system executes locally using pure Python standard library modules.
   - Delivers sub-millisecond responses (~0.5 ms) grounded in historical verified resolutions (`data/historical_resolutions.jsonl`).
   - Ensures deterministic, audited escalation responses for high-risk queries (battery hazards, account security, financial fraud).
   - Guarantees 100% test and benchmark reproducibility across any environment in under 15 seconds.

For an in-depth architectural breakdown, module responsibilities, and a complete Mermaid workflow diagram, see [structure.md](structure.md).

---

## Repository Structure

```
Hiver/
├── README.md                          # Quickstart (<15s reproduction guide) & project overview
├── structure.md                       # Full architecture documentation & Mermaid workflow diagram
├── REPORT.md                          # Full technical report (Baselines, Failures, "What is misleading...")
├── DECISION_LOG.md                    # 12 non-obvious engineering decisions & trade-offs
├── run_eval.py                        # Single-command evaluation pipeline runner
├── interactive.py                     # Terminal CLI test console
├── requirements.txt                   # Optional dependencies
├── data/
│   ├── historical_resolutions.jsonl   # Verified historical brand resolution knowledge base
│   ├── golden_eval_set.jsonl          # 200 hand-curated & annotated evaluation examples
│   ├── human_annotations_sample.jsonl # 50-example human-judge alignment study data
│   ├── evaluation_results.json        # Complete structured metrics output
│   └── results_summary.md             # Generated benchmark markdown table
├── docs/
│   ├── annotation_guidelines.md       # Golden set sampling methodology & taxonomy definitions
│   └── judge_rubric.md                # 4-dimensional LLM-as-a-Judge scoring rubric
├── src/
│   ├── __init__.py
│   ├── config.py                      # Taxonomies, thresholds, risk patterns
│   ├── models.py                      # Data classes (CustomerTweet, AgentResponse, etc.)
│   ├── classifier.py                  # Intent classification with confidence scoring
│   ├── retriever.py                   # In-process BM25 hybrid knowledge retriever
│   ├── escalation.py                  # Operational escalation engine (safety, fraud, confidence)
│   ├── agent.py                       # SupportAgent orchestrator (Classify -> Retrieve -> Draft -> Decide)
│   ├── baselines.py                   # Baseline 0 (Trivial Canned) and Baseline 1 (Simple Zero-Shot)
│   ├── evaluator.py                   # Automated metrics (Macro F1, Precision, Recall, FAR, ROUGE)
│   ├── judge.py                       # LLM-as-a-Judge rubric evaluator
│   └── human_study.py                 # Inter-rater reliability (Cohen's Kappa & Pearson r)
├── scripts/
│   ├── generate_data.py               # Dataset generation & augmentation pipeline
│   └── generate_human_eval_sample.py  # Human calibration benchmark generator
└── tests/
    └── test_agent.py                  # Unit tests covering all core components
```
