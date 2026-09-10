#!/usr/bin/env python3
"""
Web UI Console for Hiver AI Support Agent.
Single-file self-contained application using Python standard library http.server.
Run with: python3 app.py
Then open: http://localhost:8000 in your browser.
"""

import http.server
import json
import socketserver
import urllib.parse
from src.agent import SupportAgent
from src.config import TARGET_BRAND, BRAND_HANDLE

PORT = 8000
agent = SupportAgent()

# Load precomputed benchmark metrics
try:
    with open("data/evaluation_results.json", "r") as f:
        BENCHMARK_DATA = json.load(f)
except Exception:
    BENCHMARK_DATA = {}

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AppleSupport AI Agent | Interactive Console</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --danger: #f43f5e;
      --success: #10b981;
      --warning: #f59e0b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      padding: 18px 32px;
      background: rgba(30, 41, 59, 0.8);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .brand-logo {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 18px;
      font-weight: 700;
      color: #fff;
    }
    .badge-apple {
      background: #0284c7;
      color: #fff;
      font-size: 11px;
      padding: 4px 8px;
      border-radius: 9999px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .container {
      max-width: 1100px;
      margin: 32px auto;
      padding: 0 20px;
      width: 100%;
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 28px;
    }
    @media (max-width: 860px) {
      .container { grid-template-columns: 1fr; }
    }
    .panel {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .panel h2 {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .chip-container {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 16px;
    }
    .chip {
      background: #334155;
      color: #e2e8f0;
      font-size: 12px;
      padding: 6px 12px;
      border-radius: 20px;
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .chip:hover {
      background: #475569;
      border-color: var(--accent);
      color: #fff;
    }
    .chip.alert-chip {
      border-color: rgba(244, 63, 94, 0.4);
      background: rgba(244, 63, 94, 0.15);
      color: #fda4af;
    }
    .chip.alert-chip:hover {
      background: rgba(244, 63, 94, 0.3);
    }
    textarea {
      width: 100%;
      height: 120px;
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      color: #fff;
      padding: 14px;
      font-size: 14px;
      font-family: inherit;
      resize: vertical;
      outline: none;
      transition: border 0.15s;
    }
    textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
    }
    .input-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 10px;
    }
    .char-counter {
      font-size: 12px;
      color: var(--text-muted);
    }
    button.btn-send {
      background: var(--accent);
      color: #0f172a;
      font-weight: 600;
      font-size: 14px;
      border: none;
      border-radius: 10px;
      padding: 10px 22px;
      cursor: pointer;
      transition: background 0.15s;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    button.btn-send:hover {
      background: var(--accent-hover);
      color: #fff;
    }

    /* Result Panel */
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 16px;
    }
    .badge-escalate {
      background: rgba(244, 63, 94, 0.15);
      color: var(--danger);
      border: 1px solid rgba(244, 63, 94, 0.4);
    }
    .badge-autohandle {
      background: rgba(16, 185, 129, 0.15);
      color: var(--success);
      border: 1px solid rgba(16, 185, 129, 0.4);
    }

    /* Twitter Card Preview */
    .tweet-preview {
      background: #000;
      border: 1px solid #2f3336;
      border-radius: 16px;
      padding: 16px;
      margin-top: 14px;
      font-size: 14px;
      line-height: 1.5;
    }
    .tweet-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
    }
    .avatar {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: #1d9bf0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      color: #fff;
    }
    .author-info {
      line-height: 1.2;
    }
    .author-name {
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .badge-verified {
      color: #1d9bf0;
      font-size: 14px;
    }
    .author-handle {
      font-size: 13px;
      color: #71767b;
    }
    .tweet-body {
      color: #e7e9ea;
      margin-bottom: 10px;
      word-break: break-word;
    }
    .tweet-meta {
      font-size: 12px;
      color: #71767b;
      border-top: 1px solid #2f3336;
      padding-top: 8px;
      display: flex;
      justify-content: space-between;
    }

    .detail-grid {
      margin-top: 20px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .stat-card {
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 12px;
    }
    .stat-label {
      font-size: 11px;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }
    .stat-value {
      font-size: 14px;
      font-weight: 600;
      margin-top: 4px;
      color: #fff;
    }
    .reason-box {
      margin-top: 14px;
      background: #0f172a;
      border-left: 3px solid var(--accent);
      padding: 12px 16px;
      border-radius: 4px;
      font-size: 13px;
      color: #cbd5e1;
    }

    /* Benchmark Table Tab */
    .benchmark-section {
      max-width: 1100px;
      margin: 0 auto 40px auto;
      padding: 0 20px;
      width: 100%;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 13px;
    }
    th, td {
      padding: 12px 14px;
      text-align: left;
      border-bottom: 1px solid var(--card-border);
    }
    th {
      background: #0f172a;
      color: var(--text-muted);
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 600;
    }
    tr:hover td {
      background: rgba(56, 189, 248, 0.04);
    }
    .highlight-cell {
      color: var(--accent);
      font-weight: 700;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand-logo">
      <span></span>
      <span>AppleSupport AI Console</span>
      <span class="badge-apple">Production Agent</span>
    </div>
    <div style="font-size: 13px; color: var(--text-muted);">
      Hiver SDE Intern Assignment
    </div>
  </header>

  <main class="container">
    <!-- Left: Input & Preset Tests -->
    <div class="panel">
      <h2>✉️ Incoming Customer Tweet</h2>
      <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
        Click any preset test case below or type your own tweet:
      </p>

      <div class="chip-container">
        <div class="chip" onclick="setQuery('My iPhone 15 battery drains from 100 to 10% in two hours after updating to iOS 17.')">🔋 Battery Drain</div>
        <div class="chip alert-chip" onclick="setQuery('HELP! My phone is smoking and the back casing is bulging swollen!!')">🚨 Smoking / Swollen Battery</div>
        <div class="chip alert-chip" onclick="setQuery('Someone hacked my Apple ID, changed my email, and stole my money! Help!!')">🚨 Account Hack / Security</div>
        <div class="chip" onclick="setQuery('How do I cancel my Apple TV+ subscription before the free trial renews tomorrow?')">💳 Cancel Subscription</div>
        <div class="chip" onclick="setQuery('My AirPods Pro keep disconnecting and audio stutters on phone calls.')">🎧 AirPods Disconnect</div>
        <div class="chip alert-chip" onclick="setQuery('I am suing Apple in small claims court for taking my money!')">⚖️ Legal Litigation</div>
        <div class="chip" onclick="setQuery('Android is 1000x better than iPhone, Tim Cook is a clown lol')">💬 Feedback / Rant</div>
      </div>

      <textarea id="tweetInput" placeholder="Enter customer tweet here...">My iPhone 15 battery drains from 100 to 10% in two hours after updating to iOS 17.</textarea>
      <div class="input-footer">
        <span class="char-counter" id="inputCounter">0 / 280</span>
        <button class="btn-send" onclick="sendTweet()">
          <span>Process Tweet</span>
          <span>⚡</span>
        </button>
      </div>
    </div>

    <!-- Right: Agent Live Response -->
    <div class="panel">
      <h2>🤖 Agent Operational Verdict</h2>
      
      <div id="verdictBadge" class="status-badge badge-autohandle">
        <span>✅ AUTO-HANDLE (Bot Safe)</span>
      </div>

      <div class="reason-box" id="reasonBox">
        Query matches verified self-service troubleshooting procedures and carries no risk flags.
      </div>

      <div class="detail-grid">
        <div class="stat-card">
          <div class="stat-label">Detected Intent</div>
          <div class="stat-value" id="intentValue">HARDWARE_BATTERY</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Confidence Meter</div>
          <div class="stat-value" id="confidenceValue">95.0%</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Risk Level</div>
          <div class="stat-value" id="riskValue">LOW</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Inference Latency</div>
          <div class="stat-value" id="latencyValue">0.52 ms</div>
        </div>
      </div>

      <div class="tweet-preview">
        <div class="tweet-header">
          <div class="avatar"></div>
          <div class="author-info">
            <div class="author-name">
              Apple Support
              <span class="badge-verified">✓</span>
            </div>
            <div class="author-handle">@AppleSupport</div>
          </div>
        </div>
        <div class="tweet-body" id="replyBody">
          We'd be glad to help look into your battery performance. Go to Settings > Battery > Battery Health to check Maximum Capacity. Send us a DM with the percentage shown so we can assist further. More info: https://apple.co/battery-health
        </div>
        <div class="tweet-meta">
          <span>Replying to customer</span>
          <span id="charCount">262 / 280 chars</span>
        </div>
      </div>
    </div>
  </main>

  <!-- Bottom: Benchmark Results Section -->
  <section class="benchmark-section">
    <div class="panel">
      <h2>🏆 Benchmark Comparison vs Baselines (200 Golden Items)</h2>
      <table>
        <thead>
          <tr>
            <th>Model Architecture</th>
            <th>Intent Macro-F1</th>
            <th>Escalation F1</th>
            <th>False-Automation Rate ⚠️</th>
            <th>LLM-as-a-Judge (1-5)</th>
            <th>Avg Latency</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Baseline 0 (Trivial Canned)</td>
            <td>0.049</td>
            <td>0.000</td>
            <td style="color: var(--danger)">100.0%</td>
            <td>3.64 / 5.0</td>
            <td>0.01 ms</td>
          </tr>
          <tr>
            <td>Baseline 1 (Simple Zero-Shot)</td>
            <td>0.566</td>
            <td>0.000</td>
            <td style="color: var(--danger)">100.0%</td>
            <td>3.57 / 5.0</td>
            <td>0.01 ms</td>
          </tr>
          <tr style="background: rgba(56, 189, 248, 0.08); font-weight: 600;">
            <td class="highlight-cell">Proposed Support Agent (RAG)</td>
            <td class="highlight-cell">0.847</td>
            <td class="highlight-cell">0.446</td>
            <td class="highlight-cell" style="color: var(--success)">60.9% (Safest)</td>
            <td class="highlight-cell">4.58 / 5.0</td>
            <td class="highlight-cell">0.55 ms</td>
          </tr>
        </tbody>
      </table>
      <p style="font-size: 12px; color: var(--text-muted); margin-top: 14px;">
        🔬 <strong>Human-Judge Agreement Proof:</strong> Cohen's Kappa κ = <strong>0.6271</strong> (Substantial Agreement) | Pearson Correlation r = <strong>0.9284</strong> | 100% within ±1 point.
      </p>
    </div>
  </section>

  <script>
    function setQuery(text) {
      document.getElementById('tweetInput').value = text;
      updateInputCount();
      sendTweet();
    }

    function updateInputCount() {
      const val = document.getElementById('tweetInput').value;
      document.getElementById('inputCounter').textContent = `${val.length} / 280`;
    }
    document.getElementById('tweetInput').addEventListener('input', updateInputCount);

    async function sendTweet() {
      const text = document.getElementById('tweetInput').value.trim();
      if (!text) return;

      try {
        const res = await fetch('/api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tweet: text })
        });
        const data = await res.json();

        // Update UI
        const isEscalate = data.escalation.should_escalate;
        const badge = document.getElementById('verdictBadge');
        if (isEscalate) {
          badge.className = 'status-badge badge-escalate';
          badge.innerHTML = '<span>🚨 ESCALATE TO HUMAN AGENT</span>';
        } else {
          badge.className = 'status-badge badge-autohandle';
          badge.innerHTML = '<span>✅ AUTO-HANDLE (Bot Safe)</span>';
        }

        document.getElementById('reasonBox').textContent = data.escalation.stated_reason;
        document.getElementById('intentValue').textContent = data.intent.intent;
        document.getElementById('confidenceValue').textContent = `${(data.intent.confidence * 100).toFixed(1)}%`;
        document.getElementById('riskValue').textContent = data.escalation.risk_level;
        document.getElementById('latencyValue').textContent = `${data.processing_time_ms.toFixed(2)} ms`;

        document.getElementById('replyBody').textContent = data.draft_reply;
        document.getElementById('charCount').textContent = `${data.draft_reply.length} / 280 chars`;

      } catch (err) {
        console.error("API error:", err);
      }
    }

    // Initial run
    updateInputCount();
    sendTweet();
  </script>
</body>
</html>
"""

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(BENCHMARK_DATA).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/predict":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            try:
                payload = json.loads(body)
                tweet = payload.get("tweet", "")
                resp = agent.respond("web_client", tweet)
                out = {
                    "intent": {
                        "intent": resp.intent_result.intent,
                        "confidence": resp.intent_result.confidence,
                        "rationale": resp.intent_result.rationale
                    },
                    "escalation": {
                        "should_escalate": resp.escalation_verdict.should_escalate,
                        "stated_reason": resp.escalation_verdict.stated_reason,
                        "risk_level": resp.escalation_verdict.risk_level,
                        "trigger": resp.escalation_verdict.trigger
                    },
                    "draft_reply": resp.draft_reply,
                    "processing_time_ms": resp.processing_time_ms
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(out).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print(f"\n=======================================================")
        print(f"  🚀 AppleSupport AI Agent UI Live at: http://localhost:{PORT}")
        print(f"=======================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
