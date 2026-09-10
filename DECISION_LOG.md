# Decision Log: 12 Non-Obvious Engineering & Design Decisions

This document records 12 non-obvious decisions made during the architecture, dataset curation, and evaluation design for the Hiver AI Customer Support Agent.

---

### 1. Selected `@AppleSupport` Over Retail / E-commerce Brands
* **Context**: The Kaggle Twitter dataset contains dozens of brands (AmazonHelp, Delta, Uber_Support, AppleSupport).
* **Decision**: Focused strictly on `@AppleSupport`.
* **Rationale**: Apple has the most distinct, high-stakes operational boundary between public Twitter triage and private DM/in-store escalation. Hardware safety (thermal runaway, battery swelling) and account security (Apple ID lockouts, 2FA) have unambiguous ground truths compared to subjective retail delivery complaints.

---

### 2. Collapsed Taxonomy to 7 Domain Intents Instead of 77 Intents (e.g., Banking77)
* **Context**: The assignment allowed using Banking77 (77 intents) or creating our own.
* **Decision**: Designed a targeted 7-intent taxonomy (`HARDWARE_BATTERY`, `SOFTWARE_UPDATE_OS`, `ACCOUNT_ICLOUD_SECURITY`, `BILLING_SUBSCRIPTIONS`, `CONNECTIVITY_NETWORK`, `DEVICE_PHYSICAL_AUDIO`, `OUT_OF_SCOPE_FEEDBACK`).
* **Rationale**: Twitter customer messages average 12–18 words. Fine-grained taxonomies (>30 classes) suffer severe boundary ambiguity on noisy tweets (e.g., "my phone died" could be battery, boot loop, or screen). A 7-intent structure provides high operational clarity where each intent maps cleanly to distinct diagnostic workflows.

---

### 3. Decoupled Escalation Decision from Intent Classification
* **Context**: Many conversational AI architectures treat "Escalate to Agent" or "Human_Handoff" as a single intent class.
* **Decision**: Modeled Escalation as an independent, orthogonal decision engine that evaluates risk across *all* intents.
* **Rationale**: An issue like `HARDWARE_BATTERY` can be either an automated resolution (how to toggle Low Power Mode) or a life-safety emergency (battery swelling and smoking). Treating escalation as an intent forces artificial trade-offs and blinds the model to the underlying technical domain.

---

### 4. Prioritized Minimizing False Automation Rate Over Deflection Rate
* **Context**: Business stakeholders often celebrate high "deflection rates" (percentage of tickets handled without humans).
* **Decision**: Optimized the agent to minimize the **False Automation Rate (FAR)** (percentage of high-risk cases that the bot incorrectly tried to handle), accepting a higher Over-Escalation Rate (~19–22%).
* **Rationale**: In customer support, an unnecessary escalation costs $3–$5 in human agent time. An unescalated battery explosion, account takeover, or legal litigation can cost tens of thousands in liability, churn, and regulatory scrutiny. Safety and security strictly supersede automation deflection.

---

### 5. Deterministic Guardrail Layer for Critical Safety & Legal Triggers
* **Context**: We could have relied entirely on an LLM prompt to identify safety hazards.
* **Decision**: Implemented an explicit deterministic regex/keyword safety filter that intercepts inputs prior to generation.
* **Rationale**: Pure probabilistic LLMs exhibit non-zero variance and can fail on adversarial phrasing, typos, or jailbreaks. Critical hazards (smoke, fire, child fraud, legal action) require deterministic zero-tolerance enforcement.

---

### 6. Retrieval-Augmented Grounding (RAG) Over LLM Fine-Tuning
* **Context**: We could have fine-tuned an open-weight model (e.g. Llama-3-8B) on AppleSupport tweets.
* **Decision**: Adopted few-shot RAG over a verified corpus of canonical brand resolutions.
* **Rationale**: Support policies, iOS versions, and official URLs change constantly. Fine-tuned models suffer from knowledge cutoffs and parametric hallucination (fabricating non-existent URLs like `apple.com/fix-my-phone`). RAG provides strict provenance: the agent only references verified Apple knowledge sources.

---

### 7. In-Process BM25 Retriever Over External Heavy Vector Databases
* **Context**: Standard RAG tutorials default to running Chroma, Pinecone, or Qdrant daemons.
* **Decision**: Built a high-performance in-process BM25 retriever with intent-gated scoring using standard Python libraries.
* **Rationale**: Eliminates cold-start server dependencies, network latency, and heavyweight binary requirements. Guarantees that any evaluator can clone the repository and run the full 200-item evaluation benchmark in **under 15 seconds** with 100% reproducibility.

---

### 8. Hard Stratification of the Golden Evaluation Set (Easy, Medium, Hard)
* **Context**: Random sampling from Kaggle yields 90% simple repetitive questions.
* **Decision**: Curated exactly 200 golden examples with a 50% Easy, 30% Medium, and 20% Hard/Ambiguous split.
* **Rationale**: Random test sets inflate performance metrics and hide catastrophic tail failures. Deliberately including multi-intent overlaps, customer rage, sarcasm, and ambiguous error codes forces the evaluation harness to reveal real production failure modes.

---

### 9. 4-Dimensional Asymmetric Weighting for LLM-as-a-Judge
* **Context**: Most judge prompts use a single generic "Rate 1 to 5" prompt.
* **Decision**: Formulated a structured rubric: Groundedness (35%), Tone (25%), Actionability (20%), and Escalation Match (20%).
* **Rationale**: In enterprise customer service, an articulate, polite hallucination is far worse than a blunt, factual response. Groundedness received the highest weighting to penalize unsupported technical advice.

---

### 10. Empirical Inter-Annotator Calibration (Cohen's Kappa & Pearson Correlation)
* **Context**: Assignments often assert "we used an LLM judge" without proving the judge is accurate.
* **Decision**: Curated a 50-item human annotation calibration set to empirically measure Cohen's Kappa ($\kappa = 0.627$) and Pearson correlation ($r = 0.928$) between human ratings and LLM Judge scores.
* **Rationale**: Demonstrates to evaluators that the evaluation harness is scientifically calibrated, trustworthy, and not grading in an echo chamber.

---

### 11. Strict 280-Character Truncation & Post-Generation Formatting Guardrail
* **Context**: LLMs naturally default to long, verbose paragraphs.
* **Decision**: Built an explicit post-generation length check that truncates and formats replies to fit within Twitter's 280-character limit.
* **Rationale**: A beautifully drafted 500-word response is completely unusable on Twitter. Real support agents must communicate compactly.

---

### 12. De-Emphasized Lexical ROUGE in Favor of Groundedness Metrics
* **Context**: NLP benchmarks frequently report ROUGE-1/ROUGE-L.
* **Decision**: Kept ROUGE as a diagnostic metric but explicitly warned against using it as a primary success metric.
* **Rationale**: In conversational support, multiple completely different responses can be equally valid (e.g. "Try a force restart by pressing Volume Up..." vs. "Please restart your iPhone and check if the Apple logo disappears"). ROUGE severely penalizes semantic paraphrases that are factually perfect.
