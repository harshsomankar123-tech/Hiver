"""
Unified LLM API Client for Hiver AI Support Agent.
Powered by Google Gemini 2.5 Flash API with silent fallback.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any

def load_env():
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    val = v.strip().strip('"').strip("'")
                    os.environ[k.strip()] = val

load_env()

class LLMClient:
    def __init__(self):
        load_env()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.provider = "gemini" if self.gemini_key else ("openai" if self.openai_key else None)

    def is_configured(self) -> bool:
        return self.provider is not None

    def generate_chat(self, system_prompt: str, conversation_history: List[Dict[str, str]], user_message: str, context_docs: str = "") -> Optional[str]:
        if not self.is_configured():
            return None
        
        if self.provider == "gemini":
            return self._call_gemini(system_prompt, conversation_history, user_message, context_docs)
        elif self.provider == "openai":
            return self._call_openai(system_prompt, conversation_history, user_message, context_docs)
        return None

    def _call_gemini(self, system_prompt: str, history: List[Dict[str, str]], user_message: str, context_docs: str) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        
        contents = []
        full_system = f"{system_prompt}\n\n[Retrieved Apple Support Knowledge]:\n{context_docs if context_docs else 'Use official Apple knowledge.'}"
        
        for msg in history[-6:]:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("text", "")}]
            })
            
        if not contents or contents[-1]["role"] != "user":
            contents.append({
                "role": "user",
                "parts": [{"text": f"[Instructions: {full_system}]\n\nCustomer: {user_message}"}]
            })
        else:
            contents[-1]["parts"][0]["text"] += f"\n\n[System Instructions: {full_system}]"

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1500
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception:
            return None
        return None

    def _call_openai(self, system_prompt: str, history: List[Dict[str, str]], user_message: str, context_docs: str) -> Optional[str]:
        url = "https://api.openai.com/v1/chat/completions"
        full_system = f"{system_prompt}\n\n[Retrieved Apple Support Knowledge]:\n{context_docs if context_docs else 'Use official Apple knowledge.'}"

        messages = [{"role": "system", "content": full_system}]
        for msg in history[-6:]:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("text", "")})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 800
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_key}"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                choices = res_data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
        except Exception:
            return None
        return None

