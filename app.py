#!/usr/bin/env python3
"""
Simple & Sleek Chatbot UI for AppleSupport AI Agent.
Pure Python standard library http.server (no extra dependencies required).
"""

import http.server
import json
import socketserver
import urllib.parse
from src.agent import SupportAgent

PORT = 8000
agent = SupportAgent()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Apple Support Chat</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f172a;
      --chat-bg: #1e293b;
      --card-border: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --user-msg: #0284c7;
      --bot-msg: #334155;
      --accent: #38bdf8;
      --danger: #f43f5e;
      --success: #10b981;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 16px;
    }
    .chat-wrapper {
      width: 100%;
      max-width: 760px;
      height: 92vh;
      background: var(--chat-bg);
      border: 1px solid var(--card-border);
      border-radius: 24px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
    }
    /* Header */
    .chat-header {
      padding: 16px 24px;
      background: rgba(15, 23, 42, 0.7);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .apple-avatar {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: #000;
      border: 1px solid #475569;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      color: #fff;
    }
    .header-titles h1 {
      font-size: 16px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .verified-icon {
      color: #38bdf8;
      font-size: 15px;
    }
    .status-text {
      font-size: 12px;
      color: #10b981;
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 2px;
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
    }
    .btn-clear {
      background: transparent;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .btn-clear:hover {
      background: #334155;
      color: #fff;
    }

    /* Message Area */
    .chat-messages {
      flex: 1;
      padding: 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }
    .message-row {
      display: flex;
      gap: 12px;
      max-width: 85%;
    }
    .message-row.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }
    .message-row.bot {
      align-self: flex-start;
    }
    .msg-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #000;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      flex-shrink: 0;
    }
    .msg-bubble {
      padding: 14px 18px;
      border-radius: 18px;
      font-size: 14.5px;
      line-height: 1.5;
      word-break: break-word;
    }
    .message-row.user .msg-bubble {
      background: var(--user-msg);
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .message-row.bot .msg-bubble {
      background: var(--bot-msg);
      color: #f1f5f9;
      border-bottom-left-radius: 4px;
      border: 1px solid rgba(255,255,255,0.05);
    }
    .bot-footer {
      margin-top: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }
    .meta-tag {
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 6px;
      font-weight: 600;
      background: rgba(15, 23, 42, 0.6);
      color: var(--text-muted);
    }
    .meta-tag.escalate {
      background: rgba(244, 63, 94, 0.2);
      color: #fda4af;
      border: 1px solid rgba(244, 63, 94, 0.3);
    }
    .meta-tag.autohandle {
      background: rgba(16, 185, 129, 0.2);
      color: #6ee7b7;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* Starter prompt pills */
    .starter-prompts {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }
    .prompt-pill {
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--card-border);
      color: #cbd5e1;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12.5px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .prompt-pill:hover {
      background: #0284c7;
      color: #fff;
      border-color: #0284c7;
    }

    /* Input Bar */
    .chat-input-bar {
      padding: 16px 20px;
      background: rgba(15, 23, 42, 0.8);
      border-top: 1px solid var(--card-border);
      display: flex;
      gap: 12px;
      align-items: center;
    }
    input[type="text"] {
      flex: 1;
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 14px 18px;
      color: #fff;
      font-size: 14.5px;
      outline: none;
      font-family: inherit;
      transition: border 0.15s;
    }
    input[type="text"]:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
    }
    .btn-send {
      width: 48px;
      height: 48px;
      border-radius: 14px;
      background: var(--accent);
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #0f172a;
      font-size: 18px;
      font-weight: 700;
      transition: background 0.15s, transform 0.1s;
      flex-shrink: 0;
    }
    .btn-send:hover {
      background: #7dd3fc;
      transform: scale(1.03);
    }
    .btn-send:active {
      transform: scale(0.97);
    }

    /* Typing indicator */
    .typing {
      display: flex;
      gap: 4px;
      padding: 8px 12px;
      background: var(--bot-msg);
      border-radius: 16px;
      width: fit-content;
    }
    .typing span {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--text-muted);
      animation: blink 1.2s infinite ease-in-out;
    }
    .typing span:nth-child(2) { animation-delay: 0.2s; }
    .typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink {
      0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
      40% { opacity: 1; transform: scale(1.1); }
    }
  </style>
</head>
<body>
  <div class="chat-wrapper">
    <!-- Header -->
    <header class="chat-header">
      <div class="header-left">
        <div class="apple-avatar"></div>
        <div class="header-titles">
          <h1>Apple Support <span class="verified-icon">✓</span></h1>
          <div class="status-text">
            <span class="status-dot"></span>
            <span>Online • AI Assistant</span>
          </div>
        </div>
      </div>
      <button class="btn-clear" onclick="clearChat()">Clear Chat</button>
    </header>

    <!-- Message Thread -->
    <div class="chat-messages" id="messageList">
      <div class="message-row bot">
        <div class="msg-avatar"></div>
        <div>
          <div class="msg-bubble">
            Hello! I'm your Apple Support Assistant. How can we help you with your iPhone, Mac, Apple ID, or battery today?
            <div class="starter-prompts">
              <div class="prompt-pill" onclick="sendQuickPrompt('My iPhone 15 battery drains from 100 to 10% in two hours.')">🔋 Battery draining quickly</div>
              <div class="prompt-pill" onclick="sendQuickPrompt('How do I cancel my Apple TV+ subscription?')">💳 Cancel subscription</div>
              <div class="prompt-pill" onclick="sendQuickPrompt('HELP! My phone is smoking and the back is swollen!!')">🚨 Battery smoking / swollen</div>
              <div class="prompt-pill" onclick="sendQuickPrompt('AirPods keep disconnecting during Zoom calls')">🎧 AirPods disconnecting</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Bar -->
    <form class="chat-input-bar" id="chatForm" onsubmit="handleSend(event)">
      <input type="text" id="userInput" placeholder="Ask Apple Support anything... (Press Enter to send)" autocomplete="off" autofocus />
      <button type="submit" class="btn-send" title="Send message">➔</button>
    </form>
  </div>

  <script>
    const messageList = document.getElementById('messageList');
    const userInput = document.getElementById('userInput');

    function sendQuickPrompt(text) {
      userInput.value = text;
      handleSend(new Event('submit'));
    }

    function clearChat() {
      messageList.innerHTML = `
        <div class="message-row bot">
          <div class="msg-avatar"></div>
          <div>
            <div class="msg-bubble">
              Chat cleared. How can Apple Support help you today?
              <div class="starter-prompts">
                <div class="prompt-pill" onclick="sendQuickPrompt('My iPhone 15 battery drains from 100 to 10% in two hours.')">🔋 Battery draining quickly</div>
                <div class="prompt-pill" onclick="sendQuickPrompt('How do I cancel my Apple TV+ subscription?')">💳 Cancel subscription</div>
                <div class="prompt-pill" onclick="sendQuickPrompt('HELP! My phone is smoking and the back is swollen!!')">🚨 Battery smoking / swollen</div>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    async function handleSend(e) {
      if (e) e.preventDefault();
      const text = userInput.value.trim();
      if (!text) return;

      // Add user message bubble
      const userRow = document.createElement('div');
      userRow.className = 'message-row user';
      userRow.innerHTML = `<div class="msg-bubble">${escapeHtml(text)}</div>`;
      messageList.appendChild(userRow);

      userInput.value = '';
      messageList.scrollTop = messageList.scrollHeight;

      // Add typing indicator
      const typingRow = document.createElement('div');
      typingRow.className = 'message-row bot';
      typingRow.id = 'typingIndicator';
      typingRow.innerHTML = `
        <div class="msg-avatar"></div>
        <div class="typing"><span></span><span></span><span></span></div>
      `;
      messageList.appendChild(typingRow);
      messageList.scrollTop = messageList.scrollHeight;

      try {
        const res = await fetch('/api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tweet: text })
        });
        const data = await res.json();

        // Remove typing indicator
        const typingElem = document.getElementById('typingIndicator');
        if (typingElem) typingElem.remove();

        // Bot reply bubble
        const isEscalate = data.escalation.should_escalate;
        const botRow = document.createElement('div');
        botRow.className = 'message-row bot';

        const statusTag = isEscalate 
          ? `<span class="meta-tag escalate">🚨 Escalate to Human: ${escapeHtml(data.escalation.stated_reason)}</span>`
          : `<span class="meta-tag autohandle">✅ Auto-Handled</span>`;

        botRow.innerHTML = `
          <div class="msg-avatar"></div>
          <div>
            <div class="msg-bubble">${escapeHtml(data.draft_reply)}</div>
            <div class="bot-footer">
              <span class="meta-tag">🎯 ${data.intent.intent}</span>
              ${statusTag}
            </div>
          </div>
        `;
        messageList.appendChild(botRow);
        messageList.scrollTop = messageList.scrollHeight;

      } catch (err) {
        const typingElem = document.getElementById('typingIndicator');
        if (typingElem) typingElem.remove();

        const errRow = document.createElement('div');
        errRow.className = 'message-row bot';
        errRow.innerHTML = `
          <div class="msg-avatar"></div>
          <div class="msg-bubble" style="color: var(--danger)">Sorry, something went wrong processing your request. Please try again.</div>
        `;
        messageList.appendChild(errRow);
        messageList.scrollTop = messageList.scrollHeight;
      }
    }

    function escapeHtml(str) {
      return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }
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
                resp = agent.respond("web_chat", tweet)
                out = {
                    "intent": {
                        "intent": resp.intent_result.intent,
                        "confidence": resp.intent_result.confidence
                    },
                    "escalation": {
                        "should_escalate": resp.escalation_verdict.should_escalate,
                        "stated_reason": resp.escalation_verdict.stated_reason,
                        "risk_level": resp.escalation_verdict.risk_level
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
        print(f"  💬 AppleSupport Chatbot Live at: http://localhost:{PORT}")
        print(f"=======================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
