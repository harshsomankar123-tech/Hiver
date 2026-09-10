# Golden Evaluation Set: Sampling Methodology & Annotation Guidelines

## 1. Dataset Overview
The golden evaluation set consists of **200 hand-curated customer tweets** targeting `@AppleSupport`. It is designed to rigorously evaluate:
1. **Intent Classification Accuracy & Calibration** across 7 distinct domain intents.
2. **Reply Quality & Brand Voice Grounding** against historical Apple resolutions.
3. **Escalation Decision Precision & Recall** (knowing when to answer vs. when to hand off).

## 2. Sampling Strategy
To avoid synthetic sterility and evaluate real production edge cases, the dataset was sampled using stratified multi-tier sampling:

- **Difficulty Tiers**:
  - **Easy (103 examples / ~51%)**: Clear, single-intent inquiries with standard troubleshooting answers (e.g. "How do I turn off Clean Energy Charging?", "AirPods volume is low").
  - **Medium (60 examples / ~30%)**: Tweets with noisy punctuation, mild colloquialisms, multi-step issues, or device/OS version ambiguities.
  - **Hard / Ambiguous (37 examples / ~19%)**: Multi-intent overlaps (e.g. hardware thermal issue combined with legal threat), sarcastic complaints, severe safety hazards (swollen batteries, smoke), or phishing inquiries with deceptive URLs.

- **Class Distribution**:
  - `HARDWARE_BATTERY`: 41 samples
  - `SOFTWARE_UPDATE_OS`: 38 samples
  - `ACCOUNT_ICLOUD_SECURITY`: 32 samples
  - `BILLING_SUBSCRIPTIONS`: 26 samples
  - `CONNECTIVITY_NETWORK`: 23 samples
  - `DEVICE_PHYSICAL_AUDIO`: 21 samples
  - `OUT_OF_SCOPE_FEEDBACK`: 19 samples

- **Escalation Distribution**:
  - `AUTO_HANDLE`: 131 samples (65.5%)
  - `ESCALATE`: 69 samples (34.5%)

---

## 3. Ground Truth Labeling Criteria

### A. Intent Taxonomy & Boundaries
1. **`HARDWARE_BATTERY`**: Device thermal issues, rapid drainage, battery health %, charging port connection faults, swollen battery casings.
2. **`SOFTWARE_UPDATE_OS`**: Boot loops, iOS/macOS update download or verification failures, app crashes occurring specifically post-update, system storage bloat.
3. **`ACCOUNT_ICLOUD_SECURITY`**: Apple ID account lockouts, 2FA code delivery failures, suspected account compromises/phishing, iCloud sync discrepancies.
4. **`BILLING_SUBSCRIPTIONS`**: In-app purchase disputes, duplicate charges, unexpected Apple subscriptions, refund requests via `reportaproblem.apple.com`.
5. **`CONNECTIVITY_NETWORK`**: Cellular drops ("No Service"), Wi-Fi disconnects, Bluetooth audio stuttering, AirDrop failure, CarPlay drops.
6. **`DEVICE_PHYSICAL_AUDIO`**: Broken screens, display lines, speaker distortion, mic static, stuck physical buttons, liquid ingress.
7. **`OUT_OF_SCOPE_FEEDBACK`**: Platform rants, unsolicited feature ideas, casual jokes, profanity/trolling without technical issue.

### B. Escalation Decision Rubric
An example **MUST be escalated (`should_escalate: true`)** if ANY of the following apply:
1. **Safety / Physical Hazard**: Device swelling, smoke, fire, overheating causing bodily harm.
2. **Security / Active Takeover**: Customer's Apple ID is actively compromised or unauthorized password changes occurred.
3. **High-Value / Disputed Billing**: Large unauthorized charges ($100+), disputed refund rejections, or litigation threats.
4. **Catastrophic Hardware / Data Failure**: Unbootable restore errors (Error 4013, Error 9), total screen blackout, permanent data loss.
5. **Customer Rage / Toxicity**: Abusive profanity or explicit legal counsel mentions requiring supervisor review.

An example **MUST be auto-handled (`should_escalate: false`)** if:
- Safe, standard diagnostic or troubleshooting steps exist in official Apple documentation.
- The inquiry is informational or educational (e.g., how to cancel a subscription, warranty pricing lookup).
- The query can be resolved by routing to official self-service portals (`reportaproblem.apple.com`, `iforgot.apple.com`).

---

## 4. Human Reference Replies
Each example includes a human-curated gold standard reply that follows Apple's real Twitter support style:
- Empathetic acknowledgment of the issue.
- Concise, actionable initial diagnostic question or troubleshooting step within the 280-character limit.
- Verified official Apple link (`apple.co/*` or official portal).
- Request for DM when private serial numbers or account details are required.
