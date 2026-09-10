#!/usr/bin/env python3
"""
Interactive CLI Demo for Hiver AI Support Agent.
Test any customer tweet in real time and inspect Intent, Grounded Reply, and Escalation Decision.
"""

import sys
from src.agent import SupportAgent

def main():
    agent = SupportAgent()
    print("=" * 65)
    print("  AppleSupport AI Agent - Interactive Test Console")
    print("=" * 65)
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        run_query(agent, query)
        return

    print("Type any customer tweet below to test (or 'exit' to quit):\n")
    sample_queries = [
        "My iPhone 15 battery drains from 100 to 10% in two hours.",
        "HELP! My phone is smoking and the back is swollen!",
        "How do I cancel my Apple TV+ subscription?",
        "Someone hacked my Apple ID and changed my phone number!!"
    ]
    print("Sample queries you can try:")
    for sq in sample_queries:
        print(f"  - \"{sq}\"")
    print("-" * 65)

    while True:
        try:
            tweet = input("\nCustomer Tweet: ").strip()
            if not tweet:
                continue
            if tweet.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            run_query(agent, tweet)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

def run_query(agent: SupportAgent, tweet: str):
    resp = agent.respond("interactive_demo", tweet)
    esc = resp.escalation_verdict
    print("\n--- [Agent Output] ---")
    print(f"  Intent:             {resp.intent_result.intent} (Confidence: {resp.intent_result.confidence*100:.1f}%)")
    print(f"  Escalation Verdict: {'ESCALATE TO HUMAN' if esc.should_escalate else 'AUTO-HANDLE (Bot Safe)'}")
    print(f"  Reason:             {esc.stated_reason}")
    print(f"  Draft Reply:\n    \"{resp.draft_reply}\"")
    print(f"  Latency:            {resp.processing_time_ms:.2f} ms")
    print("-" * 65)

if __name__ == "__main__":
    main()
