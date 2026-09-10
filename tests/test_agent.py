"""
Unit tests for Support Agent, Classifier, Retriever, and Escalation Engine.
Uses standard library unittest for zero-dependency portability.
"""

import unittest
from src.classifier import IntentClassifier
from src.retriever import ResolutionRetriever
from src.escalation import EscalationEngine
from src.agent import SupportAgent

class TestSupportAgent(unittest.TestCase):
    def setUp(self):
        self.clf = IntentClassifier()
        self.retriever = ResolutionRetriever()
        self.escalation_engine = EscalationEngine()
        self.agent = SupportAgent()

    def test_intent_classification(self):
        res1 = self.clf.classify("My iPhone 15 battery drains from 100 to 10% in two hours.")
        self.assertEqual(res1.intent, "HARDWARE_BATTERY")
        self.assertGreater(res1.confidence, 0.45)

        res2 = self.clf.classify("How do I cancel my Apple TV+ subscription?")
        self.assertEqual(res2.intent, "BILLING_SUBSCRIPTIONS")

        res3 = self.clf.classify("Stuck on the Apple logo boot loop after updating iOS 17.")
        self.assertEqual(res3.intent, "SOFTWARE_UPDATE_OS")

    def test_escalation_safety(self):
        tweet = "My iPhone battery is swollen, bulging, and smoking!"
        intent = self.clf.classify(tweet)
        verdict = self.escalation_engine.decide(tweet, intent)
        self.assertTrue(verdict.should_escalate)
        self.assertEqual(verdict.trigger, "SAFETY_HAZARD")
        self.assertEqual(verdict.risk_level, "CRITICAL")

    def test_escalation_standard_query(self):
        tweet = "How do I turn on low power mode in settings?"
        intent = self.clf.classify(tweet)
        verdict = self.escalation_engine.decide(tweet, intent)
        self.assertFalse(verdict.should_escalate)
        self.assertEqual(verdict.trigger, "STANDARD_RESOLUTION")

    def test_retriever_bm25(self):
        results = self.retriever.retrieve("battery health percentage dropping", intent_filter="HARDWARE_BATTERY", top_k=2)
        self.assertGreater(len(results), 0)
        top_res, score = results[0]
        self.assertTrue("battery" in top_res.customer_query.lower() or "battery" in top_res.brand_reply.lower())

    def test_support_agent_length_constraint(self):
        resp = self.agent.respond("test_01", "My battery is draining very fast on iOS 17.")
        self.assertLessEqual(len(resp.draft_reply), 280)
        self.assertIsNotNone(resp.intent_result.intent)

if __name__ == "__main__":
    unittest.main()
